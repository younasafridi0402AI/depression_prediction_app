javascript
document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("predictionForm");
    const loading = document.getElementById("loading");
    const result = document.getElementById("result");

    if (!form) {
        console.error("predictionForm not found.");
        return;
    }

    form.addEventListener("submit", async function (event) {

        event.preventDefault();

        // Show loading
        if (loading) {
            loading.style.display = "block";
        }

        if (result) {
            result.style.display = "none";
        }

        // Get form values
        const data = {
            Gender: document.getElementById("Gender").value,
            Age: parseFloat(document.getElementById("Age").value),
            City: document.getElementById("City").value,
            Profession: document.getElementById("Profession").value,

            Academic_Pressure: parseFloat(
                document.getElementById("Academic_Pressure").value
            ),

            Work_Pressure: parseFloat(
                document.getElementById("Work_Pressure").value
            ),

            CGPA: parseFloat(
                document.getElementById("CGPA").value
            ),

            Study_Satisfaction: parseFloat(
                document.getElementById("Study_Satisfaction").value
            ),

            Job_Satisfaction: parseFloat(
                document.getElementById("Job_Satisfaction").value
            ),

            Sleep_Duration:
                document.getElementById("Sleep_Duration").value,

            Dietary_Habits:
                document.getElementById("Dietary_Habits").value,

            Degree:
                document.getElementById("Degree").value,

            Suicidal_Thoughts:
                document.getElementById("Suicidal_Thoughts").value,

            Work_Study_Hours: parseFloat(
                document.getElementById("Work_Study_Hours").value
            ),

            Financial_Stress: parseFloat(
                document.getElementById("Financial_Stress").value
            ),

            Family_History:
                document.getElementById("Family_History").value
        };

        console.log("Sending data:", data);

        try {

            const response = await fetch("/predict", {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify(data)
            });

            const responseData = await response.json();

            console.log("Server response:", responseData);

            // Hide loading
            if (loading) {
                loading.style.display = "none";
            }

            // Show result
            if (result) {
                result.style.display = "block";
            }

            // Server error
            if (!response.ok || !responseData.success) {

                document.getElementById("resultTitle").innerText =
                    "Prediction Error";

                document.getElementById("resultText").innerText =
                    responseData.error ||
                    "Something went wrong while making the prediction.";

                return;
            }

            // Successful prediction
            document.getElementById("resultTitle").innerText =
                responseData.result;

            document.getElementById("resultText").innerText =
                "Prediction completed successfully.";

            document.getElementById("depressionProbability").innerText =
                responseData.depression_probability + "%";

            document.getElementById("noDepressionProbability").innerText =
                responseData.no_depression_probability + "%";

        } catch (error) {

            console.error("Prediction error:", error);

            if (loading) {
                loading.style.display = "none";
            }

            if (result) {
                result.style.display = "block";
            }

            document.getElementById("resultTitle").innerText =
                "Connection Error";

            document.getElementById("resultText").innerText =
                "Could not connect to the prediction server.";
        }

    });

});

