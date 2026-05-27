FROM stain/jena-fuseki

ENV ADMIN_PASSWORD=admin

RUN mkdir -p /fuseki/databases

CMD ["/jena-fuseki/fuseki-server", "--loc=/fuseki/databases", "/eventos"]