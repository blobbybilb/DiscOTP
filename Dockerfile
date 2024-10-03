FROM python:3.11-slim

WORKDIR /app

RUN pip install discotp

VOLUME /app

CMD ["discotp"]