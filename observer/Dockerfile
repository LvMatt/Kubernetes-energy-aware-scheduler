FROM python:3.10-slim

WORKDIR /app

# Install Flask and requests directly
RUN pip install --no-cache-dir flask requests

# Copy your code (including utils/ directory)
COPY . .

EXPOSE 5001

CMD ["python", "observability-service.py"]
