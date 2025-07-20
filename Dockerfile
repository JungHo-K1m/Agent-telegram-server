FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app
COPY ./utils ./utils
COPY ./start_server.py ./start_server.py  # ✅ 추가됨
EXPOSE 8080
CMD ["python", "start_server.py"]  # ✅ 변경됨