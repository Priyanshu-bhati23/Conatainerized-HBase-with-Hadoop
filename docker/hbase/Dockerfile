FROM harisekhon/hbase:2.1

USER root

RUN apk add --no-cache netcat-openbsd curl

COPY config/hbase-site.xml /hbase/conf/hbase-site.xml
COPY config/hbase-env.sh /hbase/conf/hbase-env.sh
COPY config/regionservers /hbase/conf/regionservers

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 16000 16010 16020 16030

ENTRYPOINT ["/entrypoint.sh"]