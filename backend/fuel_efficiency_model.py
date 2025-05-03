"""
Predictive Fuel Efficiency Model

This module implements a lightweight predictive model for fuel efficiency
based on historical driving data. It uses a simple linear regression model
to predict fuel efficiency based on RPM, speed, throttle position, and engine load.
"""

class FuelEfficiencyPredictor:
    def __init__(self):
        # Model coefficients learned from historical data
        self.intercept = -56.107451813391386
        self.coefficients = {
            'rpm': 0.010832313812210679,
            'speed': 0.1815051138980068,
            'throttle': 0.9941380321085451,
            'engineLoad': 0.357527001532968
        }
        

    
    def predict_maf(self, rpm, speed, throttle, engine_load):
        """
        Predict Mass Air Flow (MAF) based on vehicle parameters
        
        Args:
            rpm: Engine RPM
            speed: Vehicle speed in km/h
            throttle: Throttle position percentage (0-100)
            engine_load: Engine load percentage (0-100)
            
        Returns:
            Predicted MAF value
        """
        return (self.intercept + 
                (self.coefficients['rpm'] * rpm) + 
                (self.coefficients['speed'] * speed) + 
                (self.coefficients['throttle'] * throttle) + 
                (self.coefficients['engineLoad'] * engine_load))
    
    def convert_maf_to_efficiency(self, maf, speed):
        """
        Convert MAF to fuel efficiency (km/L)
        
        Args:
            maf: Mass Air Flow
            speed: Vehicle speed in km/h
            
        Returns:
            Estimated fuel efficiency in km/L
        """
        if speed < 1:
            return 0 
        
        base_efficiency = 15 
        maf_factor = 0.5
        
        efficiency = base_efficiency - (maf * maf_factor)
        
        if efficiency < 0:
            return 0
        if efficiency > 30:
            return 30
            
        return efficiency
    
    def predict_efficiency(self, rpm, speed, throttle, engine_load):
        """
        Predict fuel efficiency directly from vehicle parameters
        
        Args:
            rpm: Engine RPM
            speed: Vehicle speed in km/h
            throttle: Throttle position percentage (0-100)
            engine_load: Engine load percentage (0-100)
            
        Returns:
            Predicted fuel efficiency in km/L
        """
        predicted_maf = self.predict_maf(rpm, speed, throttle, engine_load)
        return self.convert_maf_to_efficiency(predicted_maf, speed)
    
    def predict_future_efficiency(self, current_data, driving_style):
        """
        Predict future efficiency based on current data and driving style
        
        Args:
            current_data: Dict with current rpm, speed, throttle, engine_load
            driving_style: String indicating driving style ('eco', 'normal', 'aggressive')
            
        Returns:
            Dict with efficiency predictions for next trip and monthly average
        """

        current_efficiency = self.predict_efficiency(
            current_data['rpm'],
            current_data['speed'],
            current_data['throttle'],
            current_data['engine_load']
        )
        
        if driving_style == 'eco':
            next_trip_factor = 1.05
            monthly_factor = 1.10
        elif driving_style == 'aggressive':
            next_trip_factor = 0.90
            monthly_factor = 0.85
        else: 
            next_trip_factor = 1.0
            monthly_factor = 1.0
        
        import random
        next_trip_factor *= random.uniform(0.97, 1.03)
        monthly_factor *= random.uniform(0.95, 1.05)
        
        return {
            'current': current_efficiency,
            'nextTrip': current_efficiency * next_trip_factor,
            'monthly': current_efficiency * monthly_factor,
            'improvement': self._get_improvement_tip(current_data, driving_style)
        }
    
    def _get_improvement_tip(self, data, driving_style):
        """Generate an improvement tip based on current data and driving style"""
        if data['rpm'] > 3000:
            return "Try shifting gears earlier to reduce RPM and improve efficiency."
        elif data['throttle'] > 50:
            return "Ease up on the accelerator for better fuel economy."
        elif driving_style == 'aggressive':
            return "Consider a smoother driving style with more gradual acceleration."
        elif data['speed'] > 100:
            return "Reducing highway speed by 10-20 km/h can significantly improve fuel economy."
        else:
            return "Maintain steady speeds and anticipate stops to maximize efficiency."


def process_obd_data(obd_data):
    """
    Process OBD data for use with the prediction model
    
    Args:
        obd_data: Dict with OBD data from the API
        
    Returns:
        Dict with processed data ready for the prediction model
    """

    throttle = 0
    engine_load = 0
    
    if isinstance(obd_data.get('throttle'), str):

        throttle_str = obd_data['throttle'].replace('%', '').replace(',', '.')
        try:
            throttle = float(throttle_str)
        except ValueError:
            throttle = 0
    else:
        throttle = float(obd_data.get('throttle', 0))
    
    if isinstance(obd_data.get('engine_load'), str):

        load_str = obd_data['engine_load'].replace('%', '').replace(',', '.')
        try:
            engine_load = float(load_str)
        except ValueError:
            engine_load = 0
    else:
        engine_load = float(obd_data.get('engine_load', 0))
    
    return {
        'rpm': float(obd_data.get('rpm', 0)),
        'speed': float(obd_data.get('speed', 0)),
        'throttle': throttle,
        'engine_load': engine_load
    }


def determine_driving_style(data_history):
    """
    Analyze recent driving history to determine driving style
    
    Args:
        data_history: List of recent OBD data points
        
    Returns:
        String indicating driving style ('eco', 'normal', 'aggressive')
    """
    if not data_history or len(data_history) < 5:
        return 'normal'
    
    avg_throttle = sum(d.get('throttle', 0) for d in data_history) / len(data_history)
    avg_rpm = sum(d.get('rpm', 0) for d in data_history) / len(data_history)
    
    if avg_throttle > 40 or avg_rpm > 2500:
        return 'aggressive'
    elif avg_throttle < 25 and avg_rpm < 2000:
        return 'eco'
    else:
        return 'normal'