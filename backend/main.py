from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from itertools import cycle
import os, math

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the custom dataset
csv_path = os.path.join(os.path.dirname(__file__), "data/custom_vehicle_data.csv")
df = pd.read_csv(csv_path)

# Create an iterator to loop through the dataset continuously
data_iterator = cycle(df.to_dict(orient="records"))

# Define a data model
class OBDData(BaseModel):
    speed: float
    rpm: float
    fuel_efficiency: float
    engine_temp: float
    throttle: float
    fault_code: str


@app.get("/api/real-time-obd-data")
def get_real_time_obd_data():
    """
    Streams real-time vehicle data row by row.
    Handles NaN, Inf, and invalid float values.
    """
    try:
        data = next(data_iterator)  # Get the next row

        # Replace NaN or Infinity values with 0
        for key in data:
            if isinstance(data[key], float) and (math.isnan(data[key]) or math.isinf(data[key])):
                data[key] = 0.0  # Set a safe default value

        return {
            "speed": data["speed"],
            "rpm": data["rpm"],
            "fuel_efficiency": data["fuel_efficiency"],
            "engine_temp": data["engine_temp"],
            "throttle": data["throttle"],
            "fault_code": data["fault_code"]
        }
    except Exception as e:
        return {"error": f"Failed to retrieve OBD data: {str(e)}"}

@app.post("/api/efficiency-score")
def get_efficiency_score(data: OBDData):
    """
    Calculates efficiency score based on speed, RPM, and fuel efficiency.
    """
    if data.speed == 0:
        return {"error": "Speed cannot be zero for efficiency calculation."}
    
    score = (data.fuel_efficiency / data.speed) * 100
    return {"efficiency_score": round(score, 2)}

