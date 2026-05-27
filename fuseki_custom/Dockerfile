FROM stain/jena-fuseki

RUN mkdir -p /fuseki/databases \
    && mkdir -p /fuseki/templates \
    && mkdir -p /fuseki/backups \
    && mkdir -p /fuseki/system \
    && chmod -R 777 /fuseki

ENV ADMIN_PASSWORD=admin123

CMD ["/jena-fuseki/fuseki-server", "--update", "--mem", "/ds"]