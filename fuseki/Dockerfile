FROM stain/jena-fuseki

ENV ADMIN_PASSWORD=admin123

RUN mkdir -p /fuseki/databases && chmod -R 777 /fuseki

CMD ["/jena-fuseki/fuseki-server", "--update", "--mem", "/eventos"]