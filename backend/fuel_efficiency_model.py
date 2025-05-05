import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import pickle
import os
import random

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
    Analyse recent driving history to determine driving style
    
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

class FuelEfficiencyPredictor:
    """
    This module calculates fuel efficiency based on the stoichiometric relationship between
    air flow and fuel consumption. For gasoline engines, the ideal air-to-fuel ratio is 14.7:1
    by mass, meaning 14.7g of air is required to completely burn 1g of fuel.
    """
    
    def __init__(self, model_path=None):
        """
        Initialize the predictor by loading a trained model
        
        Args:
            model_path: Path to a saved model file (.pkl)
        """
        self.model = None
        self.scaler = StandardScaler()
        
        if model_path and os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    saved_data = pickle.load(f)
                    self.model = saved_data['model']
                    self.scaler = saved_data['scaler']
                print(f"Loaded model from {model_path}")
            except Exception as e:
                print(f"Error loading model: {str(e)}")
                self.model = None
    
    def train(self, data_path, output_model_path=None):
        """
        Train the model using data from CSV
        
        Args:
            data_path: Path to the CSV file containing OBD data
            output_model_path: Where to save the model (optional)
            
        Returns:
            Training score (R²)
        """
        # Load and preprocess data
        df = self._load_and_preprocess_data(data_path)
        
        if df is None or len(df) == 0:
            print("Error: No valid data for training")
            return 0
        
        # Extract features and target
        X, y = self._prepare_training_data(df)
        
        if len(X) == 0:
            print("Error: No valid training examples")
            return 0
        
        # Split into training and validation sets
        from sklearn.model_selection import train_test_split
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # Train model
        self.model = LinearRegression()
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        train_score = self.model.score(X_train_scaled, y_train)
        val_score = self.model.score(X_val_scaled, y_val)
        
        print(f"Model trained. R² (train): {train_score:.4f}, R² (validation): {val_score:.4f}")
        
        # Print coefficients
        feature_names = ['ENGINE_RPM', 'SPEED', 'THROTTLE_POS', 'ENGINE_LOAD']
        print("Model coefficients:")
        print(f"Intercept: {self.model.intercept_:.6f}")
        for name, coef in zip(feature_names, self.model.coef_):
            print(f"{name}: {coef:.6f}")
        
        # Save model if requested
        if output_model_path:
            with open(output_model_path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'scaler': self.scaler
                }, f)
            print(f"Model saved to {output_model_path}")
        
        return val_score
    
    def _load_and_preprocess_data(self, data_path):
        """
        Load and preprocess CSV data
        
        Args:
            data_path: Path to CSV file
            
        Returns:
            Preprocessed DataFrame
        """
        try:
            import pandas as pd
            df = pd.read_csv(data_path, low_memory=False)
            print(f"Loaded data from {data_path} with {len(df)} rows")
            
            # Check for required columns and map alternative names
            column_mapping = {
                'rpm': 'ENGINE_RPM',
                'speed': 'SPEED',
                'throttle': 'THROTTLE_POS',
                'engine_load': 'ENGINE_LOAD',
                'maf': 'MAF'
            }
            
            # Rename columns if needed
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns and new_col not in df.columns:
                    df[new_col] = df[old_col]
            
            # Check for required columns
            required_columns = ['ENGINE_RPM', 'SPEED', 'THROTTLE_POS', 'ENGINE_LOAD', 'MAF']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                print(f"Error: CSV is missing these required columns: {missing_columns}")
                # Try to detect and use alternative column names
                if 'MAF' in missing_columns and 'AIR_FLOW' in df.columns:
                    df['MAF'] = df['AIR_FLOW']
                    missing_columns.remove('MAF')
                
                if missing_columns:  # If still missing columns
                    return None
            
            # Handle string values in required fields
            for col in required_columns:
                if df[col].dtype == object:
                    # Remove % signs and other non-numeric characters
                    df[col] = df[col].str.replace('%', '').str.replace(',', '.')
                    # Convert to float
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Print column statistics for inspection
            for col in required_columns:
                if col in df.columns:
                    print(f"{col} range: {df[col].min()} to {df[col].max()}, mean: {df[col].mean()}")
            
            # Remove rows with missing values
            original_len = len(df)
            df = df.dropna(subset=required_columns)
            print(f"Removed {original_len - len(df)} rows with missing values")
            
            # Remove outliers and invalid data
            df = df[(df['SPEED'] >= 0) & (df['ENGINE_RPM'] > 0)]
            df = df[(df['THROTTLE_POS'] >= 0) & (df['THROTTLE_POS'] <= 100)]
            df = df[(df['ENGINE_LOAD'] >= 0) & (df['ENGINE_LOAD'] <= 100)]
            df = df[df['MAF'] > 0]
            
            print(f"After cleaning: {len(df)} rows")
            
            return df
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return None
    
    def _prepare_training_data(self, df):
        """
        Prepare training data by creating the derived fuel efficiency target
        
        Args:
            df: Preprocessed DataFrame
            
        Returns:
            (X, y) tuple for training
        """
        # Create a copy to avoid warnings
        df_calc = df.copy()
        
        # Only work with data where vehicle is moving
        mask = (df_calc['SPEED'] > 0) & (df_calc['MAF'] > 0)
        
        # Check if MAF is likely in g/h rather than g/s
        avg_maf = df_calc.loc[mask, 'MAF'].mean()
        if avg_maf > 100:  # Likely in g/h
            print(f"MAF average ({avg_maf}) suggests values are in g/h, converting to g/s")
            df_calc.loc[mask, 'MAF'] = df_calc.loc[mask, 'MAF'] / 3600
        
        # Calculate fuel mass flow rate (g/s) using stoichiometric ratio
        df_calc.loc[mask, 'FUEL_MASS_FLOW'] = df_calc.loc[mask, 'MAF'] / 14.7
        
        # Convert to fuel volume flow (L/h)
        # Density of gasoline ~0.75 kg/L
        df_calc.loc[mask, 'FUEL_VOLUME_FLOW'] = (df_calc.loc[mask, 'FUEL_MASS_FLOW'] / 0.75) * 3.6  # g/s to L/h
        
        # Calculate efficiency (km/L)
        df_calc.loc[mask, 'FUEL_EFFICIENCY'] = df_calc.loc[mask, 'SPEED'] / df_calc.loc[mask, 'FUEL_VOLUME_FLOW']
        
        # Check for unrealistic values and apply reasonable constraints
        efficiency_min = df_calc.loc[mask, 'FUEL_EFFICIENCY'].min()
        efficiency_max = df_calc.loc[mask, 'FUEL_EFFICIENCY'].max()
        efficiency_mean = df_calc.loc[mask, 'FUEL_EFFICIENCY'].mean()
        
        print(f"Raw efficiency stats - min: {efficiency_min:.2f}, max: {efficiency_max:.2f}, mean: {efficiency_mean:.2f} km/L")
        
        # Apply reasonable limits (5-30 km/L for most vehicles)
        df_calc = df_calc[(df_calc['FUEL_EFFICIENCY'] > 0) & (df_calc['FUEL_EFFICIENCY'] <= 30)]
        
        # Get features and target
        X = df_calc[['ENGINE_RPM', 'SPEED', 'THROTTLE_POS', 'ENGINE_LOAD']].values
        y = df_calc['FUEL_EFFICIENCY'].values
        
        print(f"Prepared {len(X)} training examples")
        print(f"Filtered efficiency stats - min: {min(y):.2f}, max: {max(y):.2f}, mean: {np.mean(y):.2f} km/L")
        
        return X, y
    
    def predict_efficiency(self, rpm, speed, throttle, engine_load):
        """
        Predict fuel efficiency from vehicle parameters
        
        Args:
            rpm: Engine RPM
            speed: Vehicle speed in km/h
            throttle: Throttle position percentage (0-100)
            engine_load: Engine load percentage (0-100)
            
        Returns:
            Predicted fuel efficiency in km/L
        """
        if self.model is None:
            # If no model is loaded, use a physics-based estimation
            if speed < 1:
                return 0
            
            # Baseline efficiency for typical vehicle
            baseline_efficiency = 12.0  # km/L
            
            # RPM factor - optimal around 1800-2200 RPM
            if rpm < 1000:
                rpm_factor = 0.8  # Low RPM is inefficient
            elif rpm <= 2200:
                rpm_factor = 1.0  # Optimal range
            else:
                rpm_factor = max(0.6, 1.0 - ((rpm - 2200) / 4000) * 0.4)  # Higher RPM reduces efficiency
            
            # Throttle factor - partial throttle most efficient
            if throttle < 15:
                throttle_factor = 0.85  # Very light throttle less efficient
            elif throttle <= 40:
                throttle_factor = 1.0  # Optimal range
            else:
                throttle_factor = max(0.7, 1.0 - ((throttle - 40) / 60) * 0.3)  # Heavy throttle less efficient
            
            # Speed factor - optimal around 70-90 km/h
            if speed < 30:
                speed_factor = 0.75  # City traffic less efficient
            elif speed <= 90:
                speed_factor = 1.0  # Highway cruising optimal
            else:
                speed_factor = max(0.8, 1.0 - ((speed - 90) / 60) * 0.2)  # Very high speeds less efficient
            
            # Load factor - higher load reduces efficiency
            load_factor = max(0.7, 1.0 - (engine_load / 100) * 0.3)
            
            # Calculate final efficiency
            efficiency = baseline_efficiency * rpm_factor * throttle_factor * speed_factor * load_factor
            
            # Ensure realistic bounds
            return max(5.0, min(30.0, efficiency))
        
        # Handle vehicle not moving
        if speed < 1:
            return 0
        
        # Use trained model for prediction
        X = np.array([[rpm, speed, throttle, engine_load]])
        X_scaled = self.scaler.transform(X)
        
        # Predict
        predicted = self.model.predict(X_scaled)[0]
        
        # Ensure realistic bounds
        return max(5.0, min(30.0, predicted))
    
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
        
        # Use reasonable default if stopped or too low
        if current_efficiency < 5.0 and current_data['speed'] > 0:
            current_efficiency = 10.0
        
        # Adjust based on driving style
        if driving_style == 'eco':
            next_trip_factor = 1.05
            monthly_factor = 1.10
        elif driving_style == 'aggressive':
            next_trip_factor = 0.90
            monthly_factor = 0.85
        else: 
            next_trip_factor = 1.0
            monthly_factor = 1.0
        
        # Small random variation for realism
        next_trip_factor *= random.uniform(0.97, 1.03)
        monthly_factor *= random.uniform(0.95, 1.05)
        
        # Apply the factors and ensure values are within realistic bounds
        next_trip = max(5.0, min(30.0, current_efficiency * next_trip_factor))
        monthly = max(5.0, min(30.0, current_efficiency * monthly_factor))
        
        return {
            'current': current_efficiency,
            'nextTrip': next_trip,
            'monthly': monthly,
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