async function runForecast() {
    let fileInput = document.getElementById("file");

    if (!fileInput.files.length) {
        alert("Please upload a CSV file.");
        return;
    }

    let formData = new FormData();
    formData.append("file", fileInput.files[0]);

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
        <b>Year:</b> ${data.year}<br>
        <b>Enrollees:</b> ${data.enrollees}<br><br>
        <b>Academic Rooms:</b> ${data.academic_rooms}<br>
        <b>TVL Rooms:</b> ${data.tvl_rooms}<br><br>
        <b>Academic Teachers:</b> ${data.academic_teachers}<br>
        <b>TVL Teachers:</b> ${data.tvl_teachers}
    `;
}
