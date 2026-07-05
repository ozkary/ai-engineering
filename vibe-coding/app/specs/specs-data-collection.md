# Specification: Patient Data Collection Requirements
## Project: Agent for Good - Heart Disease Risk Assessment

### 1. Objective
To define the exact data features required by the downstream Heart Disease Risk Model (XGBoost/Classification) hosted via the MCP tool. The Data Collection Agent must ensure all fields are captured, validated, and formatted correctly before passing the data to the execution layer.

---

### 2. Required Feature Schema

The application must collect exactly 16 features from the user. These are categorized into numerical metrics and lifestyle indicators based on CDC/UCI datasets.

#### A. Numerical Features
| Feature Name | Type | Valid Range / Format | Description |
| :--- | :--- | :--- | :--- |
| `bmi` | Float | 10.0 - 60.0 | Body Mass Index (calculated or input directly). |
| `physical_health` | Integer | 0 - 30 | Number of days in the past 30 days physical health was "not good". |
| `mental_health` | Integer | 0 - 30 | Number of days in the past 30 days mental health was "not good". |
| `sleep_time` | Integer | 1 - 24 | Average hours of sleep in a 24-hour period. |

#### B. Categorical & Lifestyle Features
| Feature Name | Type | Allowed Values | Description / Rules |
| :--- | :--- | :--- | :--- |
| `sex` | String | `Male`, `Female` | Biological sex. |
| `age_category` | String | `18-24`, `25-29`, `30-34`, `35-39`, `40-44`, `45-49`, `50-54`, `55-59`, `60-64`, `65-69`, `70-74`, `75-79`, `80 or older` | Standard CDC age brackets. |
| `smoking` | String | `Yes`, `No` | Smoked at least 100 cigarettes in entire life. |
| `alcohol_drinking` | String | `Yes`, `No` | Heavy drinker (Men >14 drinks/week, Women >7 drinks/week). |
| `stroke` | String | `Yes`, `No` | Ever told by a doctor they had a stroke. |
| `diabetic` | String | `Yes`, `No`, `No, borderline diabetes`, `Yes (during pregnancy)` | History of diabetes. |
| `physical_activity` | String | `Yes`, `No` | Physical activity/exercise in past 30 days (outside of normal job). |
| `gen_health` | String | `Excellent`, `Very good`, `Good`, `Fair`, `Poor` | User's self-reported general health rating. |
| `diff_walking` | String | `Yes`, `No` | Serious difficulty walking or climbing stairs. |
| `asthma` | String | `Yes`, `No` | Ever told by a doctor they have asthma. |
| `kidney_disease` | String | `Yes`, `No` | Ever told by a doctor they have kidney disease. |
| `skin_cancer` | String | `Yes`, `No` | Ever told by a doctor they have skin cancer. |

---

### 3. Data Validation & Processing Rules

* **BMI Calculation Support:** If the user does not know their BMI, the application UI or Data Collection Agent must ask for `weight` (lbs or kg) and `height` (feet/inches or cm) and compute it using the standard formula:
  $$BMI = \frac{weight\_kg}{height\_m^2}$$
* **Missing Data Policy:** No data points can be passed to the MCP tool as `null` or `NaN`. Every single feature must be explicitly provided or resolved via reasonable defaults if permitted by the system architecture (to be defined in the process spec).
* **Payload Format:** Output must be generated as a flat JSON object matching the exact keys defined in the feature tables above.