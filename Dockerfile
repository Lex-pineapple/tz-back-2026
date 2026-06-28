FROM python:3.10-slim
WORKDIR /app
COPY recs.txt .
RUN pip install --no-cache-dir -r recs.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]