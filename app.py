
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

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
# BASE DIRECTORY
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
# TEMPLATES
# ============================================================

templates = Jinja2Templates(
    directory=TEMPLATES_DIR
)


# ============================================================
# STATIC FILES
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)


# ============================================================
# LOAD MODEL
# ============================================================

model = joblib.load(MODEL_PATH)


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
# PREDICTION FORM
# ============================================================

@app.post("/predict", response_class=HTMLResponse)
async def predict_form(
    request: Request,

    Gender: str = Form(...),
    Age: int = Form(...),
    City: str = Form(...),
    Profession: str = Form(...),

    Academic_Pressure: float = Form(...),
    Work_pressure: float = Form(...),
    CGPA: float = Form(...),

    Study_Satisfaction: float = Form(...),
    Job_Satisfaction: float = Form(...),

    Sleep_Duration: str = Form(...),
    Dietary_Habits: str = Form(...),
    Degree: str = Form(...),

    Suicidal_Thoughts: str = Form(...),

    Work_Study_Hours: float = Form(...),
    Financial_Stress: float = Form(...),

    Family_History: str = Form(...)
):

    try:

        # ----------------------------------------------------
        # CREATE INPUT DATA
        # ----------------------------------------------------

        input_data = {
            "Gender": Gender,
            "Age": Age,
            "City": City,
            "Profession": Profession,

            "Academic Pressure": Academic_Pressure,
            "Work pressure": Work_pressure,

            "CGPA": CGPA,

            "Study Satisfaction": Study_Satisfaction,
            "Job Satisfaction": Job_Satisfaction,

            "Sleep Duration": Sleep_Duration,
            "Dietary Habits": Dietary_Habits,
            "Degree": Degree,

            "Have you ever had suicidal thoughts?":
                Suicidal_Thoughts,

            "Work/Study Hours": Work_Study_Hours,

            "Financial Stress": Financial_Stress,

            "Family History of Mental Illness":
                Family_History
        }


        # ----------------------------------------------------
        # DATAFRAME
        # ----------------------------------------------------

        df = pd.DataFrame([input_data])


        # ----------------------------------------------------
        # PREDICTION
        # ----------------------------------------------------

        prediction = model.predict(df)[0]


        # ----------------------------------------------------
        # PROBABILITY
        # ----------------------------------------------------

        probability = model.predict_proba(df)[0]

        depression_probability = round(
            float(probability[1]) * 100,
            2
        )

        no_depression_probability = round(
            float(probability[0]) * 100,
            2
        )


        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        if int(prediction) == 1:

            result = "Depression Risk Detected"

        else:

            result = "Low Depression Risk"


        # ----------------------------------------------------
        # RETURN RESULT TO HTML
        # ----------------------------------------------------

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "result": result,
                "depression_probability":
                    depression_probability,
                "no_depression_probability":
                    no_depression_probability
            }
        )


    except Exception as e:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "result": "Prediction Error",
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

