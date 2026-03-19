FROM apache/hadoop:3.4.3

USER root

RUN apt-get update && apt-get install -y \
    netcat-openbsd curl \
    && rm -rf /var/lib/apt/lists/*

COPY config/core-site.xml /opt/hadoop/etc/hadoop/core-site.xml
COPY config/hdfs-site.xml /opt/hadoop/etc/hadoop/hdfs-site.xml
COPY config/yarn-site.xml /opt/hadoop/etc/hadoop/yarn-site.xml
COPY config/mapred-site.xml /opt/hadoop/etc/hadoop/mapred-site.xml

RUN mkdir -p /hadoop/dfs/name /hadoop/dfs/data && chmod -R 755 /hadoop

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 9870 9864 8088 8042

ENTRYPOINT ["/entrypoint.sh"]