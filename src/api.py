# src/api.py
from fastapi import FastAPI
from pydantic import BaseModel, Field
from score import predict_single

app = FastAPI(title="WeCare247 Churn Predictor")

class CaregiverPayload(BaseModel):
    caregiver_id: str
    tenure_days: int = Field(..., ge=0)
    age: int
    waiting_days: int
    total_leave_days: int
    days_worked_2025: float
    work_ratio_2025: float
    rank: int
    competency_score: float
    positive_feedback: int
    incidents: int
    avg_income_per_shift: float
    salary_band: str
    age_band: str
    current_status: str
    home_province: str

@app.post("/predict")
def predict(payload: CaregiverPayload):
    result = predict_single(payload.dict())
    return result
