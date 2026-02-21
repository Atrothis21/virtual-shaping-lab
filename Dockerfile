FROM python:3.11-slim

WORKDIR /app/virtual_shaping_lab

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/virtual_shaping_lab

COPY virtual_shaping_lab/requirements.txt /app/virtual_shaping_lab/requirements.txt
RUN pip install --no-cache-dir -r /app/virtual_shaping_lab/requirements.txt

COPY virtual_shaping_lab /app/virtual_shaping_lab

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "api.run:app", "--host", "0.0.0.0", "--port", "8000"]
