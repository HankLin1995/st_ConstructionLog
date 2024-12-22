# Use Python 3.10 as the base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p /app/uploads

# Set permissions
RUN chmod -R 777 /app/uploads

# Expose port for Streamlit
EXPOSE 8501

# Command to run Streamlit
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501"]
