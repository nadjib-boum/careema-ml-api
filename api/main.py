from fastapi import FastAPI, Request, Response
import patch_pickle_compat
from utils import load_models, get_prediction_results

app = FastAPI()

models = load_models()

@app.post("/predict")
async def predict(request: Request, response: Response):
  
  try:
    
    data = await request.json();
    
    print (f"data: {data}")

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
        "message": f"Prediction failed",
      }
    }
  
  