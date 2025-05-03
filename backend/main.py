from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic import validator
from typing import Union
import pandas as pd
from itertools import cycle
import os, math
import random
from datetime import datetime, timedelta

from fuel_efficiency_model import FuelEfficiencyPredictor, process_obd_data, determine_driving_style

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fuel_predictor = FuelEfficiencyPredictor("fuel_efficiency_model.pkl")

recent_obd_data = []
MAX_HISTORY_SIZE = 50

csv_path = os.path.join(os.path.dirname(__file__), "data/drv.csv")
try:
    df = pd.read_csv(csv_path)
    data_iterator = cycle(df.to_dict(orient="records"))
except FileNotFoundError:
    print(f"Warning: CSV file not found at {csv_path}. Using simulated data.")

# Trip data
trip_start_time = datetime.now() - timedelta(minutes=random.randint(15, 120))
trip_distance = random.uniform(5.0, 50.0)
trip_avg_speed = random.uniform(40.0, 90.0)
prev_avg_speed = trip_avg_speed - random.uniform(-5.0, 5.0)
trip_fuel_consumption = random.uniform(6.0, 10.0)
fuel_tank_size = 50.0
fuel_remaining = random.uniform(fuel_tank_size * 0.2, fuel_tank_size * 0.8)

# Driving behavior data
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
    
    gear: Union[int, str]

    @validator("gear", pre=True)
    def convert_gear(cls, v):
        if isinstance(v, str) and v.upper() in ["N", "R"]:
            return 0  # Treat "N" or "R" as neutral/zero
        try:
            return int(v)
        except:
            return 0

    fuel: float = 0

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
        data = next(data_iterator)
        
        for key in data:
            if isinstance(data[key], float) and (math.isnan(data[key]) or math.isinf(data[key])):
                data[key] = 0.0
        
        fuel_value = 0.0
        if 'fuel' in data:
            try:
                fuel_value = float(data['fuel'])
            except (ValueError, TypeError):
                try:
                    fuel_str = str(data['fuel']).replace('%', '').replace(',', '.')
                    fuel_value = float(fuel_str)
                except:
                    fuel_value = 0.0

        gear_value = 0
        if 'gear' in data:
            try:
                gear_value = int(float(data['gear']))
            except (ValueError, TypeError):
                try:
                    gear_value = data['gear']
                except:
                    gear_value = 0

        engine_load = 0.0
        if 'engine_load' in data:
            try:
                if isinstance(data['engine_load'], str):
                    load_str = data['engine_load'].replace('%', '').replace(',', '.')
                    engine_load = float(load_str)
                else:
                    engine_load = float(data['engine_load'])
            except:
                engine_load = 0.0

        result = {
            "speed": data["speed"],
            "rpm": data["rpm"],
            "gear": gear_value,
            "fuel_efficiency": data.get("fuel_efficiency", 0.0),
            "engine_temp": data["engine_temp"],
            "throttle": data["throttle"],
            "fault_code": data["fault_code"],
            "fuel": fuel_value,
            "engine_load": engine_load
        }
        
        global recent_obd_data
        recent_obd_data.append(result)
        if len(recent_obd_data) > MAX_HISTORY_SIZE:
            recent_obd_data = recent_obd_data[-MAX_HISTORY_SIZE:]
            
        return result
    except Exception as e:
        print(f"Error in get_real_time_obd_data: {str(e)}")
        return {"error": f"Failed to retrieve OBD data: {str(e)}"}

@app.post("/api/efficiency-score")
def get_efficiency_score(data: OBDData):
    """
    Calculates efficiency score based on speed, RPM, and fuel efficiency.
    """
    if data.speed == 0:
        return {"efficiency_score": 0}
    
    processed_data = {
        'rpm': data.rpm,
        'speed': data.speed,
        'throttle': data.throttle,
        'engine_load': 50 
    }
    
    predicted_efficiency = fuel_predictor.predict_efficiency(
        processed_data['rpm'],
        processed_data['speed'],
        processed_data['throttle'],
        processed_data['engine_load']
    )
    
    score = min(100, max(0, (predicted_efficiency / 15) * 100))
    
    return {"efficiency_score": round(score, 2)}

@app.get("/api/trip-info")
def get_trip_info():
    """
    Provides information about the current trip.
    Now uses real OBD data for fuel values.
    """
    global trip_distance, trip_avg_speed, trip_start_time, trip_fuel_consumption
    global prev_avg_speed

    trip_distance += random.uniform(0.01, 0.1)
    trip_avg_speed += random.uniform(-0.5, 0.5)
    trip_fuel_consumption += random.uniform(-0.05, 0.05)
    trip_avg_speed = max(0, trip_avg_speed)
    trip_fuel_consumption = max(1, trip_fuel_consumption)

    if recent_obd_data:
        latest_fuel = recent_obd_data[-1].get("fuel", 0.0)
    else:
        latest_fuel = 0.0

    now = datetime.now()
    duration_minutes = (now - trip_start_time).total_seconds() / 60

    if trip_fuel_consumption > 0:
        estimated_range = max(0, (latest_fuel / trip_fuel_consumption) * 100)
    else:
        estimated_range = 0.0

    return {
        "distance": trip_distance,
        "avgSpeed": trip_avg_speed,
        "duration": duration_minutes,
        "startTime": trip_start_time,
        "avgConsumption": trip_fuel_consumption,
        "fuelRemaining": latest_fuel,
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
    
    acceleration_score += random.uniform(-0.1, 0.1)
    acceleration_score = max(1.0, min(5.0, acceleration_score))
    
    braking_score += random.uniform(-0.1, 0.1)
    braking_score = max(1.0, min(5.0, braking_score))
    
    current_efficiency += random.uniform(-0.1, 0.1)
    current_efficiency = max(5.0, min(15.0, current_efficiency))
    
    if random.random() < 0.02:
        harsh_accel_current += 1
    if random.random() < 0.01:
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
    Uses our actual predictive model for fuel efficiency calculations.
    """
    global recent_obd_data, trip_fuel_consumption, acceleration_score, braking_score
    
    if recent_obd_data:
        latest_data = recent_obd_data[-1]
        processed_data = process_obd_data(latest_data)
        
        driving_style = determine_driving_style(recent_obd_data)
        
        efficiency_predictions = fuel_predictor.predict_future_efficiency(processed_data, driving_style)
        current_efficiency = efficiency_predictions['current']
    else:
        current_efficiency = trip_fuel_consumption
        efficiency_predictions = {
            'current': current_efficiency,
            'nextTrip': current_efficiency * (1 + (random.random() * 0.1 - 0.05)),
            'monthly': current_efficiency * (1 + (random.random() * 0.15 - 0.05)),
            'improvement': "Maintain steady speeds and anticipate stops to maximize efficiency."
        }
    
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
    
    monthly_km = 1200  # Assumed monthly distance
    fuel_price = 1.50  # Assumed price per liter
    
    try:
        if current_efficiency <= 0:
            raise ValueError("Invalid efficiency, using default.")
        fuel_consumption = monthly_km / current_efficiency
    except Exception:
        current_efficiency = 8.0  # fallback
        fuel_consumption = monthly_km / current_efficiency

    monthly_fuel_cost = fuel_consumption * fuel_price

    
    # Monthly costs
    monthly_maintenance = 0 
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
            "current": efficiency_predictions['current'],
            "nextTrip": efficiency_predictions['nextTrip'],
            "monthly": efficiency_predictions['monthly'],
            "improvement": efficiency_predictions['improvement']
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)