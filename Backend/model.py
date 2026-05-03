import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import os

class PatientRiskModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self._create_dummy_model()
    
    def _create_dummy_model(self):
        """Create a realistic risk prediction model"""
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        # Features: Age, Systolic BP, Diastolic BP, Heart Rate, Temperature
        X = np.random.rand(n_samples, 5)
        X[:, 0] = X[:, 0] * 80  + 20  # Age 20-100
        X[:, 1] = X[:, 1] * 120 + 80  # SBP 80-160
        X[:, 2] = X[:, 2] * 80  + 40  # DBP 50-100
        X[:, 3] = X[:, 3] * 100 + 60  # HR 60-160
        X[:, 4] = X[:, 4] * 6 + 96   # Temp 96-100
        
        # Create risk labels based on rules
        y = []
        for age, sbp, dbp, hr, temp in X:
            risk_score = 0
            if age > 65: risk_score += 2
            if sbp > 140 or dbp > 90: risk_score += 2
            if hr > 100 or hr < 60: risk_score += 1
            if temp > 100.4: risk_score += 2
            if sbp > 180 or dbp > 120: risk_score += 3
            
            if risk_score <= 2:
                y.append(0)  # Low risk
            elif risk_score <= 4:
                y.append(1)  # Medium risk
            else:
                y.append(2)  # High risk
        
        # Train Random Forest
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        
    def predict(self, age, systolic_bp, diastolic_bp, heart_rate, temperature):
        """Predict risk level"""
        features = np.array([[age, systolic_bp, diastolic_bp, heart_rate, temperature]])
        prediction = self.model.predict(features)[0]
        
        risk_map = {0: "Low", 1: "Medium", 2: "High"}
        return risk_map[prediction]

# Singleton instance
risk_model = PatientRiskModel()