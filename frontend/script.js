async function runForecast() {

    console.log("Button clicked");

    let fileInput = document.getElementById("file");

    // Check file
    if (!fileInput.files.length) {
        alert("Please upload a CSV file first.");
        return;
    }

    let formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {

        // 🔥 IMPORTANT: Replace with YOUR Render URL
        let response = await fetch("https://ncr-prediction.onrender.com", {
            method: "POST",
            body: formData
        });

        let data = await response.json();

        if (data.error) {
            document.getElementById("result").innerHTML = "❌ " + data.error;
            return;
        }

        document.getElementById("result").innerHTML = `
            <h3>Forecast Output</h3>

            <b>Year:</b> ${data.year}<br>
            <b>Projected Enrollees:</b> ${data.enrollees}<br><br>

            <h4>Resource Allocation</h4>
            🏫 Academic Rooms: ${data.academic_rooms}<br>
            🏫 TVL Rooms: ${data.tvl_rooms}<br><br>

            👩‍🏫 Academic Teachers: ${data.academic_teachers}<br>
            👩‍🏫 TVL Teachers: ${data.tvl_teachers}
        `;

    } catch (error) {

        console.error(error);

        document.getElementById("result").innerHTML = `
            ❌ Failed to connect to server.<br>
            Please check your backend deployment.
        `;
    }
}
