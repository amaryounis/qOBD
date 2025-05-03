import os
import sys
from fuel_efficiency_model import FuelEfficiencyPredictor

def train_model():
    """Train and save the fuel efficiency model"""
    predictor = FuelEfficiencyPredictor()
    
    # Define data file paths using the relative data directory
    data_dir = "data"
    file1_path = os.path.join(data_dir, "TestData.csv")
    file2_path = os.path.join(data_dir, "exp1_14drivers_14cars_dailyRoutes.csv")
    
    # Try to train on first dataset
    print(f"Trying to train on {file1_path}...")
    score1 = predictor.train(file1_path, 'temp_model.pkl')
    
    # Try to train on second dataset
    print(f"\nTrying to train on {file2_path}...")
    score2 = predictor.train(file2_path, 'temp_model2.pkl')
    
    # Use the best model
    if score1 > score2 and score1 > 0:
        print("\nUsing model from TestData.csv")
        final_predictor = FuelEfficiencyPredictor('temp_model.pkl')
        final_path = 'fuel_efficiency_model.pkl'
        os.rename('temp_model.pkl', final_path)
    elif score2 > 0:
        print("\nUsing model from exp1_14drivers_14cars_dailyRoutes.csv")
        final_predictor = FuelEfficiencyPredictor('temp_model2.pkl')
        final_path = 'fuel_efficiency_model.pkl'
        os.rename('temp_model2.pkl', final_path)
    else:
        print("\nError: Could not train a valid model from either dataset")
        return None
    
    # Clean up temp files
    for f in ['temp_model.pkl', 'temp_model2.pkl']:
        if os.path.exists(f):
            try:
                os.remove(f)
            except:
                pass
    
    print(f"Final model saved to {final_path}")
    
    # Test the model with some sample values
    sample_values = [
        {'rpm': 1500, 'speed': 50, 'throttle': 20, 'engine_load': 30},
        {'rpm': 2500, 'speed': 100, 'throttle': 40, 'engine_load': 50},
        {'rpm': 3500, 'speed': 120, 'throttle': 60, 'engine_load': 70}
    ]
    
    print("\nSample predictions:")
    for values in sample_values:
        try:
            efficiency = final_predictor.predict_efficiency(
                values['rpm'], values['speed'], values['throttle'], values['engine_load']
            )
            print(f"Input: {values}")
            print(f"Predicted efficiency: {efficiency:.2f} km/L")
            
            # Get future predictions
            future = final_predictor.predict_future_efficiency(values, 'normal')
            print(f"Future efficiency: Next trip: {future['nextTrip']:.2f} km/L, Monthly: {future['monthly']:.2f} km/L")
            print(f"Tip: {future['improvement']}")
            print()
        except Exception as e:
            print(f"Error making prediction: {str(e)}")
    
    return final_predictor

if __name__ == "__main__":
    train_model()