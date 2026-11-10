# Staging local aislado para el Lab 5: mismo Nginx y mismas APIs Flask del proyecto,
# con datos ficticios. Contexto de build: raiz del repositorio en el commit a evaluar.
FROM python:3.12-slim
RUN apt-get update -qq && apt-get install -y -qq nginx curl >/dev/null
WORKDIR /srv/app
COPY src ./src
COPY nginx/lab3-fdsi.conf /etc/nginx/sites-enabled/default
COPY frontend/ /var/www/lab3/
RUN pip install -q -r src/alerts-api/requirements.txt -r src/actions-api/requirements.txt
COPY evidence/lab5/staging-local/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh
EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
