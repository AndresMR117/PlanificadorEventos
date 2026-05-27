FROM stain/jena-fuseki

USER root

RUN chmod -R 777 /fuseki || true
RUN mkdir -p /fuseki/databases
RUN mkdir -p /fuseki/backups
RUN mkdir -p /fuseki/configuration
RUN mkdir -p /fuseki/system
RUN mkdir -p /fuseki/templates

RUN chmod -R 777 /fuseki

ENV ADMIN_PASSWORD=admin123

CMD ["/jena-fuseki/fuseki-server", "--update", "--mem", "/ds"]