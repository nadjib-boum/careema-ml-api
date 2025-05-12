from fastapi import FastAPI, Request, Response
import asyncio
import patch_pickle_compat
from utils import load_models, get_prediction_results, is_auth_valid

app = FastAPI()

models = load_models()

@app.post("/predict")
async def predict(request: Request, response: Response):
  
  try:
    
    if not is_auth_valid(request):
      response.status_code = 401;
      return {
        "success": False,
        "error": {
          "message": "Unauthorized",
        }
      }
    
    data = await request.json();

    results = get_prediction_results(data, models)
    
    return {
      "success": True,
      "results": results,
    }
    
  except Exception as e:
    
    print (f"prediction_error: {e}")
      
    response.status_code = 400;
    
    return {
      "success": False,
      "error": {
        "message": "Prediction failed",
      }
    }
  
# ngrok http http://localhost:8080