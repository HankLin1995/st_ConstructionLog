FROM python:3.10-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴文件
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程序代碼
COPY . .

# 創建必要的目錄
RUN mkdir -p /app/data /app/uploads

# 設置權限
RUN chmod -R 777 /app/data /app/uploads

# 設置環境變量
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 8000

# 默認命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
