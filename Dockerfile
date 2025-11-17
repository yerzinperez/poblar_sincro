FROM alpine
COPY . /app/
WORKDIR /app/
RUN apk update
RUN apk upgrade
RUN apk add --no-cache \
    python3 \
    py3-pip \
    gcc \
    python3-dev \
    musl-dev \
    mariadb-dev
RUN pip install --break-system-packages mysql-connector-python faker python-dotenv

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]