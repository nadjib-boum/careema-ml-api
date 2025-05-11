import os
import cloudpickle as pickle
import pandas as pd
import numpy as np
from fastapi import Request
from dotenv import load_dotenv
import os

load_dotenv()

AUTH_TOKEN = os.getenv("AUTH_TOKEN")

def load_models():
    models = {}
    model_dir = './models'

    if not os.path.exists(model_dir):
        print(f"Warning: Model directory '{model_dir}' does not exist.")
        return models

    model_files = [f for f in os.listdir(model_dir) if f.endswith('.pkl')]

    if not model_files:
        print("Warning: No model files found.")
        return models

    for model_file in model_files:
        model_path = os.path.join(model_dir, model_file)
        model_name = os.path.splitext(model_file)[0]
        try:
            with open(model_path, 'rb') as f:
                models[model_name] = pickle.load(f)
            print(f"Loaded model: {model_name}")
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")

    return models

def encode_features(df):
  df_copy = df.copy()
  
  features = [ 'sex', 'chest_pain_type', 'fasting_blood_sugar', 'rest_ecg', 'exercise_induced_angina', 'slope', 'vessels_colored_by_flourosopy', 'thalassemia' ]

  code = {
    'Female': 0,
    'Male': 1,

    'Non-anginal pain': 0,
    'Typical angina': 1,
    'Atypical angina': 2,
    'Asymptomatic': 3,

    'Lower than 120 mg/ml': 0,
    'Greater than 120 mg/ml': 1,

    'ST-T wave abnormality': 0,
    'Left ventricular hypertrophy': 1,

    'No': 0,
    'Yes': 1,

    'Downsloping': 0,
    'Flat': 1,
    'Upsloping': 2,

    'Zero': 0,
    'One': 1,
    'Two': 2,
    'Three': 3,
    'Four': 4,

    'Fixed Defect': 1,
    'Normal': 2,
    'Reversable Defect': 3,
  }   
    
  for feature in features:
      df_copy[feature] = df_copy[feature].map(code)
  return df_copy

def convert_results(obj):
	if isinstance(obj, (np.integer, np.int64, np.int32)):
			return int(obj)
	elif isinstance(obj, (np.floating, np.float64, np.float32)):
			return float(obj)
	elif isinstance(obj, np.ndarray):
			return obj.tolist()
	elif isinstance(obj, dict):
			return {k: convert_results(v) for k, v in obj.items()}
	elif isinstance(obj, list):
			return [convert_results(i) for i in obj]
	else:
			return obj

def get_prediction_results (data, models):
  
    df = pd.DataFrame([data]);
    
    results = {};

    model_results = [];

    for model_name, model in models.items():
        prediction = model.predict(df)[0];
        probability = None
        try:
            proba = model.predict_proba(df)[0]
            probability = proba[1]
        except:
            probability = float(prediction)
            
        model_results.append({
          "model": model_name,
					"prediction": prediction,
					"probability": probability,
				})
        
    if model_results:
        avg_probability = sum([m['probability'] for m in model_results]) / len(model_results)
        positive_votes = sum([m['prediction'] for m in model_results])
        total_votes = len(model_results)
        positive_predictions = (positive_votes / total_votes) * 100;
        is_diseased = bool(positive_votes >= total_votes // 2 + (total_votes % 2)) 
        results = {
            "model_results": model_results,
            "avg_disease_probability": avg_probability,
            "positive_predictions": positive_predictions,
            "is_diseased": is_diseased,
        }      
    else:
      raise ValueError("No predictions made.")
 
    return convert_results(results);

def is_auth_valid (request: Request):
    
    auth_header = request.headers.get("Authorization")
  
    if not auth_header or not auth_header.startswith("Bearer "):
        return False
    
    token = auth_header.split("Bearer ")[1]
    
    print (f"token: {token}")
    print (f"AUTH_TOKEN: {AUTH_TOKEN}")
    
    if token != AUTH_TOKEN:
        return False
    
    return True