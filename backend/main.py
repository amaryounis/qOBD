from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define a data model
class OBDData(BaseModel):
    speed: float
    rpm: float
    fuel_efficiency: float

# Simulate OBD-II data
@app.get("/api/obd-data")
def get_obd_data():
    return {
        "speed": round(random.uniform(20, 120), 2),
        "rpm": round(random.uniform(1000, 5000), 2),
        "fuel_efficiency": round(random.uniform(5, 30), 2)
    }

# Predict driver efficiency score (placeholder logic)
@app.post("/api/efficiency-score")
def get_efficiency_score(data: OBDData):
    if data.speed == 0:
        return {"error": "Speed cannot be zero for efficiency calculation."}
    score = (data.fuel_efficiency / data.speed) * 100
    return {"efficiency_score": round(score, 2)}