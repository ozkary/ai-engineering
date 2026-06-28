import os
import pickle
from pydantic import BaseModel, Field

# Load the models at startup (outside hot-path)
current_dir = os.path.dirname(__file__)
model_path = os.path.join(current_dir, 'hd_xgboost_model.pkl')
dv_path = os.path.join(current_dir, 'hd_dictvectorizer.pkl')

with open(model_path, 'rb') as f:
    loaded_model = pickle.load(f)

with open(dv_path, 'rb') as f:
    loaded_dv = pickle.load(f)

class HeartDiseaseFeatures(BaseModel):
    # Demographics & Key Metrics
    age_category: str = Field(..., alias="ageCategory")
    sex: str
    bmi: float
    
    # Lifestyle Indicators
    smoking: str
    alcohol_drinking: str = Field(..., alias="alcoholDrinking")
    physical_activity: str = Field(..., alias="physicalActivity")
    sleep_time: float = Field(..., alias="sleepTime")
    
    # Clinical History / Comorbidities
    stroke: str
    diff_walking: str = Field(..., alias="diffWalking")
    diabetic: str
    asthma: str
    kidney_disease: str = Field(..., alias="kidneyDisease")
    skin_cancer: str = Field(..., alias="skinCancer")
    
    # Subjective Health State Markers
    gen_health: str = Field(..., alias="genHealth")
    physical_health: float = Field(..., alias="physicalHealth")
    mental_health: float = Field(..., alias="mentalHealth")

    class Config:
        populate_by_name = True # Allows mapping snake_case to camelCase parameters smoothly


def prepare_input(features: HeartDiseaseFeatures) -> dict:
    # Convert Yes/No strings to 1/0 for binary features
    def to_binary(val: str) -> int:
        return 1 if val.strip().lower() == "yes" else 0

    return {
        "agecategory": features.age_category,
        "sex": features.sex,
        "bmi": features.bmi,
        "smoking": to_binary(features.smoking),
        "alcoholdrinking": to_binary(features.alcohol_drinking),
        "physicalactivity": to_binary(features.physical_activity),
        "sleeptime": features.sleep_time,
        "stroke": to_binary(features.stroke),
        "diffwalking": to_binary(features.diff_walking),
        "diabetic": features.diabetic,
        "asthma": to_binary(features.asthma),
        "kidneydisease": to_binary(features.kidney_disease),
        "skincancer": to_binary(features.skin_cancer),
        "genhealth": features.gen_health,
        "physicalhealth": features.physical_health,
        "mentalhealth": features.mental_health
    }


def predict(data: dict):
    # Transform the raw structured dictionary into the matrix shape expected by the model
    X = loaded_dv.transform(data)
    # Extract the probability score specifically for Class 1 (High Risk Positive)
    y_pred = loaded_model.predict_proba(X)[:, 1]
    return float(y_pred[0])


def probability_label(probability: float):
    labels = ['none', 'low', 'medium', 'high']
    label = 'unknown'

    if probability < 0.3:
        label = labels[0]
    elif probability < 0.50:
        label = labels[1]
    elif probability < 0.75:
        label = labels[2]
    elif probability >= 0.75:
        label = labels[3]
        
    return label
