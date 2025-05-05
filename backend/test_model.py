from fuel_efficiency_model import FuelEfficiencyPredictor
import numpy as np
import matplotlib.pyplot as plt

def test_model_performance():
    """
    Test the performance of the fuel efficiency prediction model
    using realistic driving scenarios and generate comparative visualizations.
    """
    # Load predictor with trained model
    predictor = FuelEfficiencyPredictor("fuel_efficiency_model.pkl")
    print(f"Model loaded: {'Trained model' if predictor.model is not None else 'Using fallback calculation'}")
    
    # Define realistic test cases with proper units
    # Format: (scenario_name, rpm, speed, throttle, engine_load)
    test_cases = [
        ("City stop-and-go", 1500, 25, 35, 45),
        ("City cruising", 1800, 40, 20, 30),
        ("Suburban driving", 2200, 60, 25, 35),
        ("Highway cruising", 2000, 90, 15, 25),
        ("Highway high speed", 2500, 120, 30, 40),
        ("Aggressive acceleration", 3500, 70, 60, 70),
        ("Uphill driving", 3000, 60, 50, 80),
        ("Idle", 800, 0, 0, 10),
        ("Coasting", 1200, 45, 5, 15),
        ("Optimal efficiency", 1800, 80, 15, 20)
    ]
    
    print("\nFuel Efficiency Prediction Test:")
    print("Scenario\t\tRPM\tSpeed\tThrottle\tLoad\tEfficiency (km/L)")
    print("-" * 90)
    
    predictions = []
    
    for scenario, rpm, speed, throttle, load in test_cases:
        # Use percentage values (0-100) for throttle and load
        efficiency = predictor.predict_efficiency(rpm, speed, throttle, load)
        predictions.append(efficiency)
        
        # Format for nicer output alignment
        if len(scenario) < 15:
            scenario_pad = f"{scenario}\t\t"
        else:
            scenario_pad = f"{scenario}\t"
            
        print(f"{scenario_pad}{rpm}\t{speed}\t{throttle}\t\t{load}\t{efficiency:.2f}")
    
    # Calculate statistics (excluding idle case)
    moving_cases = [(s, p) for (s, _, speed, _, _), p in zip(test_cases, predictions) if speed > 0]
    if moving_cases:
        valid_predictions = [p for _, p in moving_cases]
        avg_efficiency = np.mean(valid_predictions)
        min_efficiency = np.min(valid_predictions)
        max_efficiency = np.max(valid_predictions)
        
        print("\nStatistics (excluding idle):")
        print(f"Average predicted efficiency: {avg_efficiency:.2f} km/L")
        print(f"Min predicted efficiency: {min_efficiency:.2f} km/L")
        print(f"Max predicted efficiency: {max_efficiency:.2f} km/L")
        
        # Find best and worst scenarios
        best_scenario = max(moving_cases, key=lambda x: x[1])
        worst_scenario = min(moving_cases, key=lambda x: x[1])
        print(f"Best scenario: {best_scenario[0]} ({best_scenario[1]:.2f} km/L)")
        print(f"Worst scenario: {worst_scenario[0]} ({worst_scenario[1]:.2f} km/L)")
    
    # Test driving style impact with multiple baseline scenarios
    baseline_scenarios = [
        ("City driving", {'rpm': 1800, 'speed': 40, 'throttle': 25, 'engine_load': 45}),
        ("Highway driving", {'rpm': 2000, 'speed': 90, 'throttle': 20, 'engine_load': 30}),
        ("Mixed driving", {'rpm': 2200, 'speed': 60, 'throttle': 30, 'engine_load': 40})
    ]
    
    print("\nDriving Style Impact Test:")
    
    for scenario_name, baseline_data in baseline_scenarios:
        print(f"\n{scenario_name} baseline:")
        base_efficiency = predictor.predict_efficiency(
            baseline_data['rpm'],
            baseline_data['speed'],
            baseline_data['throttle'],
            baseline_data['engine_load']
        )
        print(f"Baseline efficiency: {base_efficiency:.2f} km/L")
        
        # Test different driving styles
        style_results = []
        for style in ['eco', 'normal', 'aggressive']:
            try:
                future = predictor.predict_future_efficiency(baseline_data, style)
                print(f"  {style.capitalize()} style:")
                print(f"    Next trip: {future.get('nextTrip', 0):.2f} km/L ({get_percent_change(base_efficiency, future.get('nextTrip', 0)):.1f}%)")
                print(f"    Monthly: {future.get('monthly', 0):.2f} km/L ({get_percent_change(base_efficiency, future.get('monthly', 0)):.1f}%)")
                print(f"    Tip: {future.get('improvement', 'N/A')}")
                style_results.append((style, future.get('nextTrip', 0), future.get('monthly', 0)))
            except Exception as e:
                print(f"    Error testing {style} style: {e}")
    
    # Test parameter sensitivity
    print("\nParameter Sensitivity Analysis:")
    
    # Base case
    base_params = {'rpm': 2000, 'speed': 60, 'throttle': 30, 'engine_load': 40}
    base_efficiency = predictor.predict_efficiency(
        base_params['rpm'],
        base_params['speed'],
        base_params['throttle'],
        base_params['engine_load']
    )
    print(f"Base case efficiency: {base_efficiency:.2f} km/L")
    
    # Test each parameter individually
    param_ranges = {
        'rpm': list(range(1000, 4001, 500)),
        'speed': list(range(20, 141, 20)),
        'throttle': list(range(10, 101, 10)),
        'engine_load': list(range(10, 101, 10))
    }
    
    param_effects = {}
    
    for param, values in param_ranges.items():
        print(f"\nTesting {param} sensitivity:")
        print(f"{param}\tEfficiency (km/L)\tChange (%)")
        print("-" * 40)
        
        param_results = []
        for value in values:
            test_params = base_params.copy()
            test_params[param] = value
            
            efficiency = predictor.predict_efficiency(
                test_params['rpm'],
                test_params['speed'],
                test_params['throttle'],
                test_params['engine_load']
            )
            
            percent_change = get_percent_change(base_efficiency, efficiency)
            param_results.append((value, efficiency, percent_change))
            print(f"{value}\t{efficiency:.2f}\t\t{percent_change:.1f}%")
        
        param_effects[param] = param_results
    
    # Calculate overall sensitivity (avg % change per % change in parameter)
    print("\nParameter sensitivity ranking:")
    sensitivities = {}
    
    for param, results in param_effects.items():
        # Calculate average sensitivity
        base_value = base_params[param]
        sensitivity_values = []
        
        for value, _, percent_change in results:
            if value != base_value and base_value != 0:
                # Calculate % change in parameter
                param_percent_change = abs((value - base_value) / base_value * 100)
                if param_percent_change > 0:
                    sensitivity = abs(percent_change) / param_percent_change
                    sensitivity_values.append(sensitivity)
        
        if sensitivity_values:
            avg_sensitivity = np.mean(sensitivity_values)
            sensitivities[param] = avg_sensitivity
    
    # Sort parameters by sensitivity
    sorted_sensitivities = sorted(sensitivities.items(), key=lambda x: x[1], reverse=True)
    for param, sensitivity in sorted_sensitivities:
        print(f"{param}: {sensitivity:.4f} (efficiency change per 1% parameter change)")

def get_percent_change(base_value, new_value):
    """Calculate percentage change between two values"""
    if base_value == 0:
        return float('inf') if new_value > 0 else float('-inf')
    return ((new_value - base_value) / base_value) * 100

if __name__ == "__main__":
    test_model_performance()