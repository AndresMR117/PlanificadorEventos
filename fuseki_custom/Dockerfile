FROM stain/jena-fuseki

USER root

# Carpetas internas de Fuseki
RUN chmod -R 777 /fuseki || true
RUN mkdir -p /fuseki/backups
RUN mkdir -p /fuseki/configuration
RUN mkdir -p /fuseki/system
RUN mkdir -p /fuseki/templates

# Carpeta persistente REAL
RUN mkdir -p /data

# Permisos
RUN chmod -R 777 /fuseki
RUN chmod -R 777 /data

# Password admin
ENV ADMIN_PASSWORD=admin123

# Fuseki persistente con TDB2
CMD ["/jena-fuseki/fuseki-server", "--update", "--tdb2", "--loc", "/data", "/ds"]