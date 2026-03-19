export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))
export HBASE_HEAPSIZE=2048
export HBASE_OPTS="-XX:+UseG1GC"
export HBASE_MANAGES_ZK=false