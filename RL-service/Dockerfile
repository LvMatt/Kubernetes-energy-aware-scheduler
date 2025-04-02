# Use an official Python image as the base
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the entire RL-service folder
COPY RL-service/ RL-service/

# Install required Python packages
RUN pip install fastapi
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install uvicorn
RUN pip install stable-baselines3
RUN pip install numpy

# Expose the API port
EXPOSE 8000

# Run the FastAPI server
CMD ["uvicorn", "RL-service.rl_scheduler_api:app", "--host", "0.0.0.0", "--port", "8000"]