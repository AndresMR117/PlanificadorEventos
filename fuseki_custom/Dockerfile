FROM stain/jena-fuseki

RUN mkdir -p /fuseki/templates && chmod -R 777 /fuseki

ENV ADMIN_PASSWORD=admin123

CMD ["/jena-fuseki/fuseki-server", "--update", "--mem", "/ds"]