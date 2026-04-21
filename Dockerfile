FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/
COPY examples/ examples/
COPY requirements.txt .

RUN pip install --no-cache-dir -e .
RUN pip install --no-cache-dir fastapi uvicorn requests pyyaml httpx

EXPOSE 8000

CMD ["uvicorn", "oran_metrics.api.ric_server:app", "--host", "0.0.0.0", "--port", "8000"]
