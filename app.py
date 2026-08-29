from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import pandas as pd
import joblib
import os


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Student Depression Prediction API",
    description="Random Forest Student Depression Prediction",
    version="1.0.0"
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "random_forest_depression_model.pkl"
)

TEMPLATES_DIR = os.path.join(
    BASE_DIR,
    "templates"
)

STATIC_DIR = os.path.join(
    BASE_DIR,
    "static"
)


# ============================================================
# LOAD MODEL
# ============================================================

model = joblib.load(MODEL_PATH)


# ============================================================
# TEMPLATES AND STATIC
# ============================================================

templates = Jinja2Templates(
    directory=TEMPLATES_DIR
)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)


# ============================================================
# PREDICTION INPUT MODEL
# ============================================================

class PredictionInput(BaseModel):
    Gender: str
    Age: float
    City: str
    Profession: str

    Academic_Pressure: float
    Work_Pressure: float
    CGPA: float

    Study_Satisfaction: float
    Job_Satisfaction: float

    Sleep_Duration: str
    Dietary_Habits: str
    Degree: str

    Suicidal_Thoughts: str

    Work_Study_Hours: float
    Financial_Stress: float

    Family_History: str


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


# ============================================================
# PREDICTION API
# ============================================================

@app.post("/predict")
async def predict(data: PredictionInput):

    try:

        # ----------------------------------------------------
        # Convert received data into model input
        # ----------------------------------------------------

        input_data = {
            "Gender": data.Gender,
            "Age": float(data.Age),
            "City": data.City,
            "Profession": data.Profession,

            "Academic Pressure": float(
                data.Academic_Pressure
            ),

            "Work Pressure": float(
                data.Work_Pressure
            ),

            "CGPA": float(
                data.CGPA
            ),

            "Study Satisfaction": float(
                data.Study_Satisfaction
            ),

            "Job Satisfaction": float(
                data.Job_Satisfaction
            ),

            "Sleep Duration": data.Sleep_Duration,
            "Dietary Habits": data.Dietary_Habits,
            "Degree": data.Degree,

            "Have you ever had suicidal thoughts ?":
                data.Suicidal_Thoughts,

            "Work/Study Hours": float(
                data.Work_Study_Hours
            ),

            "Financial Stress": float(
                data.Financial_Stress
            ),

            "Family History of Mental Illness":
                data.Family_History
        }


        # ----------------------------------------------------
        # Create DataFrame
        # ----------------------------------------------------

        input_df = pd.DataFrame(
            [input_data]
        )


        # ----------------------------------------------------
        # Prediction
        # ----------------------------------------------------

        prediction = model.predict(
            input_df
        )[0]


        # ----------------------------------------------------
        # Probability
        # ----------------------------------------------------

        probability = model.predict_proba(
            input_df
        )[0]


        depression_probability = (
            probability[1] * 100
        )

        no_depression_probability = (
            probability[0] * 100
        )


        # ----------------------------------------------------
        # Result
        # ----------------------------------------------------

        if int(prediction) == 1:

            result = "Depression Risk Detected"

        else:

            result = "Low Depression Risk"


        # ----------------------------------------------------
        # Return Result
        # ----------------------------------------------------

        return JSONResponse(
            content={
                "success": True,

                "prediction": int(prediction),

                "result": result,

                "depression_probability":
                    round(
                        depression_probability,
                        2
                    ),

                "no_depression_probability":
                    round(
                        no_depression_probability,
                        2
                    )
            }
        )


    except Exception as e:

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": str(e)
            }
        )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "model_loaded": model is not None
    }
