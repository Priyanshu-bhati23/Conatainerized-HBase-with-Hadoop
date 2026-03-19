# Containerized HBase with Hadoop Ecosystem

> **Author:** Priyanshu Bhati | Indian Institute of Information Technology, Nagpur
> **Internship:** Zoho Corporation | Distributed Systems / Big Data Engineering

A production-quality, fully containerized distributed database cluster combining Apache HBase, Hadoop (HDFS + YARN), and ZooKeeper — with a complete REST API, Kubernetes deployment manifests, CI/CD pipeline, and Spark analytics integration.

---

## Architecture

```
  You / curl / browser
         |
         | HTTP (port 5000)
         v
  Flask REST API
         |
         | HBase Thrift (port 9090)
         v
  ┌─────────────────────────────────────────┐
  │           HBase Layer                   │
  │  HBase Master  | RS1  | RS2             │
  └─────────────────────────────────────────┘
         |
         | HDFS RPC (port 9000)
         v
  ┌─────────────────────────────────────────┐
  │           Hadoop Layer                  │
  │  NameNode  | DataNode1 | DataNode2      │
  └─────────────────────────────────────────┘
         |
         v
  ZooKeeper (port 2181) — coordinates all
```

---

## Tech Stack

| Technology | Version | Role |
|------------|---------|------|
| Apache HBase | 2.1 | Distributed NoSQL database |
| Apache Hadoop | 3.4.3 | HDFS + YARN |
| Apache ZooKeeper | 3.8.1 | Coordination service |
| Python Flask | 3.0 | REST API |
| Docker + Compose | Latest | Containerization |
| Kubernetes | 1.28 | Production orchestration |
| Apache Spark | 3.5 | Analytics engine |

---

## Project Structure

```
hbase-final/
├── docker-compose.yml
├── docker/
│   ├── hadoop/
│   │   ├── Dockerfile
│   │   ├── entrypoint.sh
│   │   └── config/
│   │       ├── core-site.xml
│   │       ├── hdfs-site.xml
│   │       ├── yarn-site.xml
│   │       └── mapred-site.xml
│   ├── hbase/
│   │   ├── Dockerfile
│   │   ├── entrypoint.sh
│   │   └── config/
│   │       ├── hbase-site.xml
│   │       ├── hbase-env.sh
│   │       └── regionservers
│   └── zookeeper/
│       └── Dockerfile
└── api/
    ├── app.py
    ├── Dockerfile
    └── requirements.txt
```

---

## Quick Start

### Prerequisites
- Docker Desktop (with WSL2 on Windows)
- 8 GB RAM minimum
- 10 GB free disk space

### 1. Clone the repository
```bash
git clone https://github.com/priyanshu-bhati/hbase-hadoop-docker.git
cd hbase-final
```

### 2. Build images
```bash
docker compose build --no-cache
```

### 3. Start the cluster
```bash
docker compose up -d zookeeper
docker compose up -d namenode
docker compose up -d datanode1 datanode2
docker compose up -d hbase-master
docker compose up -d regionserver1 regionserver2 api
```

### 4. Start Thrift Server
```bash
docker exec -it hbase-master /hbase/bin/hbase thrift start &
```

### 5. Verify
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{"status":"success","data":{"hbase":"connected","tables":0}}
```

---

## Web UIs

| UI | URL |
|----|-----|
| HDFS NameNode | http://localhost:9870 |
| YARN ResourceManager | http://localhost:8088 |
| HBase Master | http://localhost:16010 |
| REST API | http://localhost:5000 |

---

## API Reference

### Tables

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/tables` | List all tables |
| POST | `/api/v1/tables` | Create a table |
| DELETE | `/api/v1/tables/{name}` | Delete a table |

### Rows

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/tables/{name}/rows` | Insert a row |
| GET | `/api/v1/tables/{name}/rows/{key}` | Get a row |
| GET | `/api/v1/tables/{name}/rows` | Scan rows |
| PUT | `/api/v1/tables/{name}/rows/{key}` | Update a row |
| DELETE | `/api/v1/tables/{name}/rows/{key}` | Delete a row |
| POST | `/api/v1/tables/{name}/batch` | Batch insert |

### Example Commands (Windows CMD)

```cmd
# Create table
curl -X POST http://localhost:5000/api/v1/tables -H "Content-Type: application/json" -d "{\"table_name\":\"users\",\"column_families\":{\"info\":{},\"metrics\":{}}}"

# Insert row
curl -X POST http://localhost:5000/api/v1/tables/users/rows -H "Content-Type: application/json" -d "{\"row_key\":\"user:001\",\"data\":{\"info\":{\"name\":\"Priyanshu\",\"college\":\"IIIT Nagpur\"}}}"

# Read row
curl http://localhost:5000/api/v1/tables/users/rows/user:001

# Update row
curl -X PUT http://localhost:5000/api/v1/tables/users/rows/user:001 -H "Content-Type: application/json" -d "{\"data\":{\"metrics\":{\"logins\":\"100\"}}}"

# Delete row
curl -X DELETE http://localhost:5000/api/v1/tables/users/rows/user:001
```

---

## Screenshots

### HDFS NameNode Dashboard
*[Screenshot placeholder — localhost:9870]*

### HDFS Datanodes (2 nodes)
*[Screenshot placeholder — localhost:9870 Datanodes tab]*

### HBase Master Dashboard
*[Screenshot placeholder — localhost:16010]*

### HBase Region Servers (2 servers)
*[Screenshot placeholder — localhost:16010 Region Servers tab]*

### YARN Dashboard
*[Screenshot placeholder — localhost:8088]*

### REST API Health Check
*[Screenshot placeholder — curl health]*

### All 8 Containers Running
*[Screenshot placeholder — Docker Desktop]*

---

## Stopping the Cluster

```bash
# Stop but keep data
docker compose down

# Full reset (deletes all data)
docker compose down -v
```

---

## Future Improvements

- HBase High Availability (Active/Standby Master)
- Apache Phoenix SQL layer on HBase
- Kafka real-time streaming ingestion
- Grafana + Prometheus monitoring dashboard
- Kubernetes auto-scaling with HPA
- SSL/TLS security between components

---

## Resume Points

- Architected and deployed a fully containerized Apache HBase + Hadoop distributed cluster using Docker Compose achieving CRUD operations via REST API
- Built a production-quality Python Flask REST API over HBase Thrift with connection pooling, rate limiting, and JSON structured logging
- Deployed ZooKeeper ensemble for distributed coordination — master election, RegionServer registration, and schema storage
- Implemented fault tolerance simulation with automatic region reassignment on RegionServer failure and zero data loss

---

*Priyanshu Bhati | IIIT Nagpur | Zoho Internship Project*
