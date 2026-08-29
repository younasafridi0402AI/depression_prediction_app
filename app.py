
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import pandas as pd
import joblib
import os


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
# FASTAPI
# ============================================================

app = FastAPI(
    title="Student Depression Prediction API",
    description="Random Forest Student Depression Prediction",
    version="1.0.0"
)


# ============================================================
# TEMPLATES
# ============================================================

templates = Jinja2Templates(
    directory=TEMPLATES_DIR
)


# ============================================================
# STATIC
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)


# ============================================================
# LOAD MODEL BUNDLE
# ============================================================

try:

    bundle = joblib.load(MODEL_PATH)

    print("MODEL LOADED SUCCESSFULLY")
    print("MODEL TYPE:", type(bundle))

    # Actual Random Forest
    model = bundle["model"]

    # Encoders
    label_encoders = bundle["label_encoders"]

    # Target encoder
    target_encoder = bundle.get("target_encoder", None)

    # Features used during training
    features = bundle["features"]

    print("FEATURES:", features)
    print("LABEL ENCODERS:", label_encoders.keys())

except Exception as e:

    print("MODEL LOAD ERROR:", str(e))

    bundle = None
    model = None
    label_encoders = {}
    target_encoder = None
    features = []


# ============================================================
# INPUT DATA
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
# HOME
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


# ============================================================
# PREDICT
# ============================================================

@app.post("/predict")
async def predict(data: PredictionInput):

    try:

        # --------------------------------------------------------
        # CHECK MODEL
        # --------------------------------------------------------

        if model is None:

            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Model could not be loaded."
                }
            )


        # --------------------------------------------------------
        # CREATE DATA USING ONLY TRAINING FEATURES
        # --------------------------------------------------------

        input_data = {

            "Gender": data.Gender,

            "Age": float(data.Age),

            "Academic Pressure":
                float(data.Academic_Pressure),

            "Study Satisfaction":
                float(data.Study_Satisfaction),

            "Sleep Duration":
                data.Sleep_Duration,

            "Dietary Habits":
                data.Dietary_Habits,

            "Have you ever had suicidal thoughts ?":
                data.Suicidal_Thoughts,

            "Study Hours":
                float(data.Work_Study_Hours),

            "Financial Stress":
                float(data.Financial_Stress),

            "Family History of Mental Illness":
                data.Family_History
        }


        # --------------------------------------------------------
        # DATAFRAME
        # --------------------------------------------------------

        df = pd.DataFrame([input_data])

        print("\n================================")
        print("ORIGINAL INPUT")
        print("================================")
        print(df)


        # --------------------------------------------------------
        # APPLY LABEL ENCODERS
        # --------------------------------------------------------

        for column, encoder in label_encoders.items():

            if column in df.columns:

                value = df.loc[0, column]

                try:

                    df[column] = encoder.transform(
                        df[column].astype(str)
                    )

                except Exception as e:

                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "error":
                                f"Invalid value for {column}: {value}. "
                                f"Model expects values used during training."
                        }
                    )


        # --------------------------------------------------------
        # MAKE SURE COLUMN ORDER IS EXACTLY THE SAME
        # --------------------------------------------------------

        df = df[features]


        print("\n================================")
        print("MODEL INPUT")
        print("================================")
        print(df)


        # --------------------------------------------------------
        # PREDICTION
        # --------------------------------------------------------

        prediction = model.predict(df)[0]

        print("RAW PREDICTION:", prediction)


        # --------------------------------------------------------
        # PROBABILITY
        # --------------------------------------------------------

        probability = model.predict_proba(df)[0]

        print("PROBABILITY:", probability)


        # --------------------------------------------------------
        # RESULT LABEL
        # --------------------------------------------------------

        if target_encoder is not None:

            try:

                decoded_prediction = target_encoder.inverse_transform(
                    [prediction]
                )[0]

                result = str(decoded_prediction)

            except Exception:

                if int(prediction) == 1:
                    result = "Depression Risk Detected"
                else:
                    result = "Low Depression Risk"

        else:

            if int(prediction) == 1:
                result = "Depression Risk Detected"
            else:
                result = "Low Depression Risk"


        # --------------------------------------------------------
        # PROBABILITY VALUES
        # --------------------------------------------------------

        classes = list(model.classes_)

        depression_probability = 0.0
        no_depression_probability = 0.0

        for i, class_value in enumerate(classes):

            if str(class_value) == "1":
                depression_probability = float(probability[i]) * 100

            elif str(class_value) == "0":
                no_depression_probability = float(probability[i]) * 100


        depression_probability = round(
            depression_probability,
            2
        )

        no_depression_probability = round(
            no_depression_probability,
            2
        )


        print("\n================================")
        print("RESULT")
        print("================================")
        print("Result:", result)
        print(
            "Depression:",
            depression_probability,
            "%"
        )
        print(
            "No Depression:",
            no_depression_probability,
            "%"
        )


        # --------------------------------------------------------
        # RETURN JSON
        # --------------------------------------------------------

        return JSONResponse(
            content={

                "success": True,

                "prediction": int(prediction),

                "result": result,

                "depression_probability":
                    depression_probability,

                "no_depression_probability":
                    no_depression_probability
            }
        )


    # ------------------------------------------------------------
    # ERROR
    # ------------------------------------------------------------

    except Exception as e:

        print("\n================================")
        print("PREDICTION ERROR")
        print("================================")
        print(str(e))

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

        "model_loaded": model is not None,

        "features": features
    }

