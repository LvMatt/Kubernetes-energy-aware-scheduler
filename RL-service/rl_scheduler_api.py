from fastapi import FastAPI
import torch
from stable_baselines3 import DQN
import numpy as np
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI()

# Load the trained RL model
MODEL_PATH = "RL-service/dqn_kubernetes"
model = DQN.load(MODEL_PATH)

# Define request model
class Node(BaseModel):
    id: str
    cpu_usage: float

class NodeList(BaseModel):
    nodes: list[Node]

@app.post("/schedule")
def schedule_pod(nodes: NodeList):
    # Convert node data to a NumPy array for the RL model
    cpu_usages = np.array([node.cpu_usage for node in nodes.nodes])
    
    # The RL model takes a state vector as input
    state = cpu_usages.reshape(1, -1)  # Ensure correct shape for model

    # Get the action (node index) from the RL model
    action, _states = model.predict(state, deterministic=True)
    
    # Find the selected node
    selected_node = nodes.nodes[action]

    return {"selected_node": selected_node.id}

# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "RL Scheduler API is running"}