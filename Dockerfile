FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY ./utils ./utils
COPY ./start_server.py ./start_server.py
COPY ./worker_improved.py ./worker_improved.py

EXPOSE 8080

CMD ["python", "start_server.py"]