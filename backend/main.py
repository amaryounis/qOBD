from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from itertools import cycle
import os, math
import random
from datetime import datetime, timedelta

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
csv_path = os.path.join(os.path.dirname(__file__), "data/driving_sim_upt.csv")
df = pd.read_csv(csv_path)

# Create an iterator to loop through the dataset continuously
data_iterator = cycle(df.to_dict(orient="records"))

# Track trip data (simple simulation)
trip_start_time = datetime.now() - timedelta(minutes=random.randint(15, 120))
trip_distance = random.uniform(5.0, 50.0)
trip_avg_speed = random.uniform(40.0, 90.0)
prev_avg_speed = trip_avg_speed - random.uniform(-5.0, 5.0)
trip_fuel_consumption = random.uniform(6.0, 10.0)
fuel_tank_size = 50.0
fuel_remaining = random.uniform(fuel_tank_size * 0.2, fuel_tank_size * 0.8)

# Driving behavior data (simulated)
acceleration_score = random.uniform(2.5, 4.5)
braking_score = random.uniform(2.5, 4.5)
current_efficiency = random.uniform(7.5, 10.5)
week_efficiency = random.uniform(7.0, 11.0)
harsh_accel_current = random.randint(0, 5)
harsh_accel_week = random.randint(7, 25)
harsh_braking_current = random.randint(0, 3)
harsh_braking_week = random.randint(5, 20)

# Define data models
class OBDData(BaseModel):
    speed: float
    rpm: float
    fuel_efficiency: float
    engine_temp: float
    throttle: float
    fault_code: str
    gear: int

class TripData(BaseModel):
    distance: float
    avgSpeed: float
    duration: float
    startTime: datetime
    avgConsumption: float
    fuelRemaining: float
    estimatedRange: float
    prevAvgSpeed: float

class DrivingBehaviorData(BaseModel):
    accelerationScore: float
    brakingScore: float
    currentEfficiency: float
    weekEfficiency: float
    currentHarshAccel: int
    weekHarshAccel: int
    currentHarshBraking: int
    weekHarshBraking: int

class MaintenancePrediction(BaseModel):
    component: str
    detail: str
    timeframe: str
    urgency: str

class EfficiencyPrediction(BaseModel):
    current: float
    nextTrip: float
    monthly: float
    improvement: str

class CostPeriod(BaseModel):
    fuel: float
    maintenance: float
    total: float

class CostPrediction(BaseModel):
    month: CostPeriod
    quarter: CostPeriod
    year: CostPeriod

class Optimization(BaseModel):
    category: str
    title: str
    description: str
    saving: str

class PredictiveModel(BaseModel):
    maintenance: list[MaintenancePrediction]
    efficiency: EfficiencyPrediction
    costs: CostPrediction
    optimizations: list[Optimization]

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
            "gear": int(data["gear"]),  # Ensure gear is sent
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
        return {"efficiency_score": 0}
    
    score = (data.fuel_efficiency / data.speed) * 100
    return {"efficiency_score": round(min(score, 100), 2)}

@app.get("/api/trip-info")
def get_trip_info():
    """
    Provides information about the current trip.
    This is a simulation - in a real implementation, this would
    track actual trip data from the vehicle.
    """
    global trip_distance, trip_avg_speed, trip_start_time, trip_fuel_consumption
    global prev_avg_speed, fuel_remaining
    
    # Simulate incremental updates to trip data
    trip_distance += random.uniform(0.01, 0.1)
    trip_avg_speed += random.uniform(-0.5, 0.5)
    trip_fuel_consumption += random.uniform(-0.05, 0.05)
    fuel_remaining -= random.uniform(0.01, 0.05)
    
    # Calculate trip duration in minutes
    now = datetime.now()
    duration_minutes = (now - trip_start_time).total_seconds() / 60
    
    # Calculate estimated range based on remaining fuel and consumption
    estimated_range = (fuel_remaining / trip_fuel_consumption) * 100
    
    return {
        "distance": trip_distance,
        "avgSpeed": trip_avg_speed,
        "duration": duration_minutes,
        "startTime": trip_start_time,
        "avgConsumption": trip_fuel_consumption,
        "fuelRemaining": fuel_remaining,
        "estimatedRange": estimated_range,
        "prevAvgSpeed": prev_avg_speed
    }

@app.get("/api/driving-behavior")
def get_driving_behavior():
    """
    Provides driving behavior analysis.
    This is a simulation - in a real implementation, this would
    analyze actual driving patterns from the vehicle.
    """
    global acceleration_score, braking_score, current_efficiency, week_efficiency
    global harsh_accel_current, harsh_accel_week, harsh_braking_current, harsh_braking_week
    
    # Simulate slight changes to make it feel dynamic
    acceleration_score += random.uniform(-0.1, 0.1)
    acceleration_score = max(1.0, min(5.0, acceleration_score))
    
    braking_score += random.uniform(-0.1, 0.1)
    braking_score = max(1.0, min(5.0, braking_score))
    
    current_efficiency += random.uniform(-0.1, 0.1)
    current_efficiency = max(5.0, min(15.0, current_efficiency))
    
    # Occasionally add harsh events
    if random.random() < 0.02:  # 2% chance
        harsh_accel_current += 1
    if random.random() < 0.01:  # 1% chance
        harsh_braking_current += 1
    
    return {
        "accelerationScore": acceleration_score,
        "brakingScore": braking_score,
        "currentEfficiency": current_efficiency,
        "weekEfficiency": week_efficiency,
        "currentHarshAccel": harsh_accel_current,
        "weekHarshAccel": harsh_accel_week,
        "currentHarshBraking": harsh_braking_current,
        "weekHarshBraking": harsh_braking_week
    }

@app.get("/api/predictive-model")
def get_predictive_model():
    """
    Provides predictive analysis for maintenance, efficiency, and costs.
    This is a simulation - in a real implementation, this would connect
    to a machine learning model trained on vehicle data.
    """
    global trip_fuel_consumption, acceleration_score, braking_score
    
    # Calculate some values based on current data to make predictions "relevant"
    current_efficiency = trip_fuel_consumption
    
    # Randomize next trip efficiency (within reasonable bounds)
    next_trip = current_efficiency * (1 + (random.random() * 0.1 - 0.05))
    monthly_avg = next_trip * (1 + (random.random() * 0.15 - 0.05))
    
    # Simulated driving tips based on scores
    improvement_tip = ""
    if acceleration_score < 3.5:
        improvement_tip = "Try accelerating more gradually to improve fuel economy."
    elif braking_score < 3.5:
        improvement_tip = "Anticipate stops earlier to reduce harsh braking and improve efficiency."
    else:
        improvement_tip = "Maintain a steady speed on highways to maximize fuel economy."
    
    # Calculate simulated costs
    monthly_km = 1200  # Assumed monthly distance
    fuel_price = 1.50  # Assumed price per liter
    fuel_consumption = monthly_km / current_efficiency
    monthly_fuel_cost = fuel_consumption * fuel_price
    
    # Simulated maintenance schedule based on random value (would be ML-based in real app)
    maintenance_urgency = ["Low", "Medium", "High"]
    maintenance_items = [
        {
            "component": "Oil Change",
            "detail": "Based on mileage and engine conditions",
            "timeframe": f"In {random.randint(1500, 3500)} km",
            "urgency": random.choice(maintenance_urgency)
        },
        {
            "component": "Brake Pads (Front)",
            "detail": f"{random.randint(20, 50)}% remaining, wear pattern detected",
            "timeframe": f"In {random.randint(3000, 7000)} km",
            "urgency": random.choice(maintenance_urgency)
        },
        {
            "component": "Air Filter",
            "detail": "Reduced airflow detected",
            "timeframe": f"In {random.randint(500, 2000)} km",
            "urgency": random.choice(maintenance_urgency)
        }
    ]
    
    # Simulated optimization suggestions
    optimizations = [
        {
            "category": "Driving",
            "title": "Reduce Hard Accelerations",
            "description": "Your acceleration rate is higher than optimal. Gradually accelerating could improve fuel economy.",
            "saving": "5-8% fuel economy improvement"
        },
        {
            "category": "Maintenance",
            "title": "Tire Pressure Adjustment",
            "description": "Current tire pressure appears slightly low. Optimal pressure would improve efficiency and tire life.",
            "saving": "3% fuel economy improvement"
        },
        {
            "category": "Route",
            "title": "Alternative Routes",
            "description": "Your common routes have high congestion. Alternative routes may reduce idle time.",
            "saving": f"Up to {random.randint(15, 25)} minutes per day"
        }
    ]
    
    # Randomly shuffle maintenance urgency and details to make it dynamic
    for item in maintenance_items:
        item["urgency"] = random.choice(maintenance_urgency)
    
    # Cost predictions
    # Monthly costs
    monthly_maintenance = 0  # Assume no maintenance this month
    if any(item["urgency"] == "High" for item in maintenance_items):
        monthly_maintenance = random.randint(50, 150)
    
    # Quarterly costs (3 months)
    quarterly_fuel = monthly_fuel_cost * 3
    quarterly_maintenance = monthly_maintenance + random.randint(100, 200)
    
    # Yearly costs
    yearly_fuel = monthly_fuel_cost * 12
    yearly_maintenance = quarterly_maintenance * 2 + random.randint(300, 500)
    
    return {
        "maintenance": maintenance_items,
        "efficiency": {
            "current": current_efficiency,
            "nextTrip": next_trip,
            "monthly": monthly_avg,
            "improvement": improvement_tip
        },
        "costs": {
            "month": {
                "fuel": monthly_fuel_cost,
                "maintenance": monthly_maintenance,
                "total": monthly_fuel_cost + monthly_maintenance
            },
            "quarter": {
                "fuel": quarterly_fuel,
                "maintenance": quarterly_maintenance,
                "total": quarterly_fuel + quarterly_maintenance
            },
            "year": {
                "fuel": yearly_fuel,
                "maintenance": yearly_maintenance,
                "total": yearly_fuel + yearly_maintenance
            }
        },
        "optimizations": optimizations
    }