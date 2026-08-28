document
    .getElementById("predictionForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const loading =
            document.getElementById("loading");

        const result =
            document.getElementById("result");

        loading.style.display = "block";
        result.style.display = "none";


        // ====================================================
        // GET FORM VALUES
        // ====================================================

        const data = {

            Gender:
                document.getElementById("Gender").value,

            Age:
                document.getElementById("Age").value,

            City:
                document.getElementById("City").value,

            Profession:
                document.getElementById("Profession").value,

            Academic_Pressure:
                document.getElementById(
                    "Academic_Pressure"
                ).value,

            Work_Pressure:
                document.getElementById(
                    "Work_Pressure"
                ).value,

            CGPA:
                document.getElementById("CGPA").value,

            Study_Satisfaction:
                document.getElementById(
                    "Study_Satisfaction"
                ).value,

            Job_Satisfaction:
                document.getElementById(
                    "Job_Satisfaction"
                ).value,

            Sleep_Duration:
                document.getElementById(
                    "Sleep_Duration"
                ).value,

            Dietary_Habits:
                document.getElementById(
                    "Dietary_Habits"
                ).value,

            Degree:
                document.getElementById("Degree").value,

            Suicidal_Thoughts:
                document.getElementById(
                    "Suicidal_Thoughts"
                ).value,

            Work_Study_Hours:
                document.getElementById(
                    "Work_Study_Hours"
                ).value,

            Financial_Stress:
                document.getElementById(
                    "Financial_Stress"
                ).value,

            Family_History:
                document.getElementById(
                    "Family_History"
                ).value
        };


        // ====================================================
        // SEND TO FASTAPI
        // ====================================================

        try {

            const response = await fetch(
                "/predict",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(data)
                }
            );


            const responseData =
                await response.json();


            // =================================================
            // HIDE LOADING
            // =================================================

            loading.style.display = "none";

            result.style.display = "block";


            // =================================================
            // ERROR
            // =================================================

            if (!responseData.success) {

                document.getElementById(
                    "resultTitle"
                ).innerText = "Error";

                document.getElementById(
                    "resultText"
                ).innerText =
                    responseData.error;

                return;
            }


            // =================================================
            // RESULT
            // =================================================

            document.getElementById(
                "resultTitle"
            ).innerText =
                responseData.result;


            document.getElementById(
                "resultText"
            ).innerText =
                "Prediction completed successfully.";


            document.getElementById(
                "depressionProbability"
            ).innerText =
                responseData.depression_probability;


            document.getElementById(
                "noDepressionProbability"
            ).innerText =
                responseData.no_depression_probability;


        } catch (error) {

            loading.style.display = "none";

            result.style.display = "block";

            document.getElementById(
                "resultTitle"
            ).innerText = "Connection Error";

            document.getElementById(
                "resultText"
            ).innerText =
                "Could not connect to the FastAPI server.";

            console.error(error);
        }

    });
