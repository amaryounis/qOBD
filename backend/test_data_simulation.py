import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from itertools import cycle

def test_data_simulation():
    # Load the CSV data used for simulation
    csv_path = "data/drv.csv"
    df = pd.read_csv(csv_path)
    
    # Convert data to records for simulation
    data_iterator = cycle(df.to_dict(orient="records"))
    
    # Collect samples for analysis
    samples = []
    for _ in range(100):
        samples.append(next(data_iterator))
    
    # Analyse relationships between parameters
    speed_values = [sample['speed'] for sample in samples]
    rpm_values = [sample['rpm'] for sample in samples]
    throttle_values = [sample['throttle'] for sample in samples]
    
    # Calculate correlations
    speed_rpm_corr = np.corrcoef(speed_values, rpm_values)[0, 1]
    speed_throttle_corr = np.corrcoef(speed_values, throttle_values)[0, 1]
    
    # Count fault codes
    fault_codes = [sample['fault_code'] for sample in samples if sample['fault_code'] != '0']
    
    print("Data Simulation Analysis:")
    print(f"Number of samples analyzed: {len(samples)}")
    print(f"Speed-RPM correlation: {speed_rpm_corr:.4f}")
    print(f"Speed-Throttle correlation: {speed_throttle_corr:.4f}")
    print(f"Number of fault codes in samples: {len(fault_codes)}")
    print(f"Unique fault codes: {set(fault_codes)}")
    
    return {
        "speed_rpm_correlation": speed_rpm_corr,
        "speed_throttle_correlation": speed_throttle_corr,
        "fault_code_frequency": len(fault_codes) / len(samples)
    }

if __name__ == "__main__":
    test_data_simulation()