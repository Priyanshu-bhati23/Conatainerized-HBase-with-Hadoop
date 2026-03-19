#!/bin/bash
set -e

ROLE=${HBASE_ROLE:-master}
echo "Starting HBase: $ROLE"

if [ "$ROLE" = "master" ]; then
    while ! nc -z zookeeper 2181; do
        sleep 3
        echo "Waiting for ZooKeeper..."
    done
    while ! nc -z namenode 9870; do
        sleep 3
        echo "Waiting for NameNode..."
    done
    /hbase/bin/hbase master start &

elif [ "$ROLE" = "regionserver" ]; then
    while ! nc -z hbase-master 16000; do
        sleep 3
        echo "Waiting for HBase Master..."
    done
    /hbase/bin/hbase regionserver start &
fi

echo "HBase $ROLE started."
tail -f /dev/null