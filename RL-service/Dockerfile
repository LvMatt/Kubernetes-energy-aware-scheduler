# Use an official Python image as the base
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy model and script into the container
COPY dqn_kubernetes_cpu.zip .
COPY dqn_kubernetes_energy.zip .
COPY rl_scheduler_api.py .

# Install required Python packages
RUN pip install fastapi uvicorn numpy
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install stable-baselines3

# Expose the API port
EXPOSE 8000

# Run the FastAPI server
CMD ["uvicorn", "rl_scheduler_api:app", "--host", "0.0.0.0", "--port", "8000"]
