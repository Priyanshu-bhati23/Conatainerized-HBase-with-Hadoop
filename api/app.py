import os
import time
import logging
from datetime import datetime
from functools import wraps

import happybase
from flask import Flask, request, jsonify, g

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HBASE_HOST = os.environ.get('HBASE_HOST', 'localhost')
HBASE_PORT = int(os.environ.get('HBASE_PORT', 9090))

_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = happybase.ConnectionPool(size=5, host=HBASE_HOST, port=HBASE_PORT)
    return _pool

def ok(data, msg="Success", status=200):
    return jsonify({"status": "success", "message": msg, "data": data,
                    "timestamp": datetime.utcnow().isoformat() + "Z"}), status

def err(msg, status=400):
    return jsonify({"status": "error", "message": msg,
                    "timestamp": datetime.utcnow().isoformat() + "Z"}), status

def decode_row(row_data):
    decoded = {}
    for col_bytes, val_bytes in row_data.items():
        col = col_bytes.decode('utf-8')
        val = val_bytes.decode('utf-8')
        family, qualifier = col.split(':', 1)
        if family not in decoded:
            decoded[family] = {}
        decoded[family][qualifier] = val
    return decoded

def hbase_errors(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error: {e}")
            return err(str(e), 500)
    return decorated

@app.route('/health')
def health():
    try:
        with get_pool().connection() as conn:
            tables = conn.tables()
        return ok({"hbase": "connected", "tables": len(tables)})
    except Exception as e:
        return err(f"HBase unreachable: {e}", 503)

@app.route('/')
def index():
    return ok({"name": "HBase REST API", "version": "1.0.0",
                "endpoints": ["/health", "/api/v1/tables", "/api/v1/tables/<name>/rows"]})

# ── Tables ──────────────────────────────────────────
@app.route('/api/v1/tables', methods=['GET'])
@hbase_errors
def list_tables():
    with get_pool().connection() as conn:
        tables = [t.decode() for t in conn.tables()]
    return ok({"tables": tables, "count": len(tables)})

@app.route('/api/v1/tables', methods=['POST'])
@hbase_errors
def create_table():
    data = request.get_json()
    name = data.get('table_name')
    families = data.get('column_families', {})
    if not name:
        return err("table_name is required")
    with get_pool().connection() as conn:
        existing = [t.decode() for t in conn.tables()]
        if name in existing:
            return err(f"Table '{name}' already exists", 409)
        conn.create_table(name, {cf: {} for cf in families})
    return ok({"table_name": name}, "Table created", 201)

@app.route('/api/v1/tables/<table_name>', methods=['DELETE'])
@hbase_errors
def delete_table(table_name):
    with get_pool().connection() as conn:
        conn.delete_table(table_name, disable=True)
    return ok({"table_name": table_name}, "Table deleted")

# ── Rows ────────────────────────────────────────────
@app.route('/api/v1/tables/<table_name>/rows', methods=['POST'])
@hbase_errors
def insert_row(table_name):
    body = request.get_json()
    row_key = body.get('row_key')
    data = body.get('data', {})
    if not row_key:
        return err("row_key is required")
    hbase_data = {}
    for family, cols in data.items():
        for q, v in cols.items():
            hbase_data[f"{family}:{q}".encode()] = str(v).encode()
    with get_pool().connection() as conn:
        conn.table(table_name).put(row_key.encode(), hbase_data)
    return ok({"row_key": row_key, "columns_written": len(hbase_data)}, "Row inserted", 201)

@app.route('/api/v1/tables/<table_name>/rows/<path:row_key>', methods=['GET'])
@hbase_errors
def get_row(table_name, row_key):
    with get_pool().connection() as conn:
        row = conn.table(table_name).row(row_key.encode())
    if not row:
        return err(f"Row '{row_key}' not found", 404)
    return ok({"table": table_name, "row_key": row_key, "data": decode_row(row)})

@app.route('/api/v1/tables/<table_name>/rows', methods=['GET'])
@hbase_errors
def scan_rows(table_name):
    limit = min(int(request.args.get('limit', 100)), 1000)
    prefix = request.args.get('prefix')
    row_start = request.args.get('row_start')
    row_stop = request.args.get('row_stop')
    scan_kwargs = {}
    if row_start: scan_kwargs['row_start'] = row_start.encode()
    if row_stop:  scan_kwargs['row_stop']  = row_stop.encode()
    results = []
    with get_pool().connection() as conn:
        table = conn.table(table_name)
        scanner = table.scan(row_prefix=prefix.encode(), **scan_kwargs) if prefix else table.scan(**scan_kwargs)
        for i, (rk, rd) in enumerate(scanner):
            if i >= limit: break
            results.append({"row_key": rk.decode(), "data": decode_row(rd)})
    return ok({"table": table_name, "rows": results, "count": len(results)})

@app.route('/api/v1/tables/<table_name>/rows/<path:row_key>', methods=['PUT'])
@hbase_errors
def update_row(table_name, row_key):
    body = request.get_json()
    data = body.get('data', {})
    hbase_data = {}
    for family, cols in data.items():
        for q, v in cols.items():
            hbase_data[f"{family}:{q}".encode()] = str(v).encode()
    with get_pool().connection() as conn:
        table = conn.table(table_name)
        if not table.row(row_key.encode()):
            return err(f"Row '{row_key}' not found", 404)
        table.put(row_key.encode(), hbase_data)
    return ok({"row_key": row_key, "columns_updated": len(hbase_data)}, "Row updated")

@app.route('/api/v1/tables/<table_name>/rows/<path:row_key>', methods=['DELETE'])
@hbase_errors
def delete_row(table_name, row_key):
    with get_pool().connection() as conn:
        conn.table(table_name).delete(row_key.encode())
    return ok({"row_key": row_key}, "Row deleted")

@app.route('/api/v1/tables/<table_name>/batch', methods=['POST'])
@hbase_errors
def batch_insert(table_name):
    rows = request.get_json().get('rows', [])
    if not rows:
        return err("rows array is required")
    if len(rows) > 10000:
        return err("Max batch size is 10000")
    start = time.time()
    with get_pool().connection() as conn:
        table = conn.table(table_name)
        with table.batch(batch_size=500) as batch:
            for row in rows:
                rk = row.get('row_key')
                data = {}
                for family, cols in row.get('data', {}).items():
                    for q, v in cols.items():
                        data[f"{family}:{q}".encode()] = str(v).encode()
                batch.put(rk.encode(), data)
    duration = time.time() - start
    return ok({"rows_inserted": len(rows), "duration_seconds": round(duration, 3)}, "Batch done", 201)

@app.errorhandler(404)
def not_found(e): return err("Endpoint not found", 404)

@app.errorhandler(405)
def method_not_allowed(e): return err("Method not allowed", 405)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
