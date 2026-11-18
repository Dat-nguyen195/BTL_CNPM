FROM python:3.12-slim
WORKDIR /app
COPY requirements-tested.txt .
RUN pip install --no-cache-dir -r requirements-tested.txt
COPY src src
COPY scripts/iot_producer.py scripts/iot_producer.py
ENV EMOBILITY_IOT_DB=/data/telemetry.sqlite3
EXPOSE 8501
CMD ["python", "-m", "streamlit", "run", "src/app.py", "--server.address=0.0.0.0", "--server.headless=true", "--browser.gatherUsageStats=false"]
