#!/bin/bash
set -e

export HADOOP_HOME=/opt/hadoop
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Auto detect JAVA_HOME
export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))
echo "JAVA_HOME: $JAVA_HOME"

ROLE=${HADOOP_ROLE:-namenode}
echo "Starting Hadoop: $ROLE"

if [ "$ROLE" = "namenode" ]; then
    if [ ! -d "/hadoop/dfs/name/current" ]; then
        echo "Formatting NameNode..."
        hdfs namenode -format -force
    fi
    echo "Starting NameNode..."
    hdfs namenode &
    echo "Starting ResourceManager..."
    yarn resourcemanager &

elif [ "$ROLE" = "datanode" ]; then
    while ! nc -z namenode 9870; do
        sleep 3
        echo "Waiting for NameNode..."
    done
    echo "Starting DataNode..."
    hdfs datanode &
    echo "Starting NodeManager..."
    yarn nodemanager &
fi

echo "$ROLE started."
tail -f /dev/null