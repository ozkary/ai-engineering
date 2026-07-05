# Specification: ML Risk Evaluation API
## Project: Agent for Good - Heart Disease Risk Inference Engine

### Objective
To define the internal folder structure, static binary asset loading procedures, input validation constraints via Pydantic schemas, and risk threshold classification routines for the serverless inference engine.

---

### Internal Architecture Layout
The Python workspace follows an isolated module format to keep the root entry point clean:

* **`/api/main.py` (Root Endpoint)**: Acts strictly as the serverless configuration router and network listener layer. It imports the designated function execution hook `predict_risk_main` directly from the internal package directory.
* **`/api/predict/` (Module Folder)**: Encapsulates all data structures, model assets, and underlying mathematical execution logic.
  * `__init__.py`: Exposes the core execution function hooks.
  * `main.py`: Contains the primary processing pipelines and prediction algorithms.
  * `hd_xgboost_model.pkl`: The serialized binary array representing the trained classification model.
  * `hd_dictvectorizer.pkl`: The serialized DictVectorizer pipeline data file used to transform clean JSON object metrics into mathematical input vectors.

---

### Machine Learning Asset Loading & Initialization
To control execution latency and cloud resource overhead, file importing protocols adhere to the following rules:
* Both binary payloads (`hd_xgboost_model.pkl` and `hd_dictvectorizer.pkl`) must be imported using standard `pickle` loading methods.
* File read instances must be initialized **outside** of the hot-path execution loop functions. This allows the objects to remain warm inside the Cloud Function's global container memory cache across incoming network triggers.

---

### Input Data Schema Validation (Pydantic Model)
The incoming JSON payload must be validated at the door using a strict Pydantic class constraint before hitting the transformer array. The schema mirrors the properties captured by the data-collection UI:

```python
from pydantic import BaseModel, Field
from typing import Optional

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
```

### Prediction & Classification Logic Matrix
Once validated, the payload passes through two main core functional sequences inside /api/predict/main.py:

- 1. Mathematical Feature Transformation & Probability Scoring
The dictionary payload is vectorized and evaluated against the model array bounds:

```python

def predict(data):
    # Transform the raw structured dictionary into the matrix shape expected by the model
    X = loaded_dv.transform(data)
    # Extract the probability score specifically for Class 1 (High Risk Positive)
    y_pred = loaded_model.predict_proba(X)[:, 1]
    return y_pred

```

- 2. Risk Evaluation Label Classification Mapping
The extracted floating-point probability score is evaluated sequentially against hard borders to categorize patient risk profile states:

```python
def probability_label(probability):
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
```

### Structured Response Contract
Upon a successful evaluation lifecycle, the API service payload returns an HTTP 200 OK status with a clean structured response:

status: "success"

raw_probability: The direct floating-point probability array result extracted from the prediction loop.

risk_category: The descriptive string tag generated from the label classification map (none, low, medium, or high).