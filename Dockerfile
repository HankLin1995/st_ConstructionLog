FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 創建一個目錄用於存放 SQLite 數據庫文件
RUN mkdir -p /app/data && \
    chmod 777 /app/data

ENV SQLALCHEMY_DATABASE_URL="sqlite:///./data/sql_app.db"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
