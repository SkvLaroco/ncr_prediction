<?php
$message = "";
$previewTable = "";

if(isset($_POST['upload'])) {

    $file = $_FILES['file']['tmp_name'];

    if($_FILES['file']['error'] !== 0){
        $message = "<div class='error'>❌ Upload failed.</div>";
    } else {

        $rows = array_map('str_getcsv', file($file));
        $header = $rows[0];

        $required = ['Year', 'Total_Enrollees'];
        $missing = array_diff($required, $header);

        if(count($missing) > 0){
            $message = "<div class='error'>❌ Missing columns: " . implode(", ", $missing) . "</div>";
        } else {

            $yearIndex = array_search('Year', $header);
            $enrollIndex = array_search('Total_Enrollees', $header);

            $isValid = true;
            $errorDetails = "";

            for($i = 1; $i < count($rows); $i++){
                $year = $rows[$i][$yearIndex];
                $enroll = $rows[$i][$enrollIndex];

                if(!is_numeric($year)){
                    $isValid = false;
                    $errorDetails = "Year must be numeric.";
                    break;
                }

                if(!is_numeric($enroll)){
                    $isValid = false;
                    $errorDetails = "Total_Enrollees must be numeric.";
                    break;
                }
            }

            if(!$isValid){
                $message = "<div class='error'>❌ Invalid data: $errorDetails</div>";
            } else {

                move_uploaded_file($file, "NCR_Total_Enrollees.csv");
                $message = "<div class='success'>✅ Dataset uploaded and validated successfully.</div>";

                // Preview
                $previewTable = "<table><tr>";
                foreach($header as $col){
                    $previewTable .= "<th>$col</th>";
                }
                $previewTable .= "</tr>";

                for($i = 1; $i < min(6, count($rows)); $i++){
                    $previewTable .= "<tr>";
                    foreach($rows[$i] as $cell){
                        $previewTable .= "<td>$cell</td>";
                    }
                    $previewTable .= "</tr>";
                }

                $previewTable .= "</table>";
            }
        }
    }
}

if(isset($_POST['run'])) {
    $output = shell_exec("python forecast.py 2>&1");

    if(strpos($output, "ERROR") !== false){
        $message = "<div class='error'>❌ Forecast failed:<br><pre>$output</pre></div>";
    } else {
        $message = "<div class='success'>✅ Forecast updated successfully.</div>";
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>NCR SHS Forecast System</title>
    <link rel="stylesheet" href="style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>

<body>

<h1>NCR SHS Enrollment Forecast System</h1>

<?php echo $message; ?>

<div class="container">

    <!-- CHART -->
    <div class="card">
        <h2>Enrollment Forecast Trend</h2>
        <canvas id="forecastChart"></canvas>
    </div>

    <!-- CONTROLS -->
    <div>

        <div class="card">
            <h3>Upload Dataset</h3>

            <form method="post" enctype="multipart/form-data">
                <input type="file" name="file" accept=".csv" required>
                <button name="upload">Upload CSV</button>
            </form>

            <hr>

            <h4>Dataset Requirements</h4>
            <p><b>File Type:</b> CSV</p>
            <ul>
                <li>Year (numeric)</li>
                <li>Total_Enrollees (numeric)</li>
            </ul>

            <pre>
Year,Total_Enrollees
2020,300000
2021,320000
            </pre>
        </div>

        <div class="card">
            <h3>Run Forecast</h3>
            <form method="post">
                <button name="run">Generate Forecast</button>
            </form>
        </div>

        <div class="card">
            <h3>Download Report</h3>
            <a href="forecast_report.pdf" download>
                <button>Download PDF</button>
            </a>
        </div>

    </div>

    <!-- PREVIEW -->
    <div class="card" style="grid-column: span 2;">
        <h2>Dataset Preview</h2>
        <?php echo $previewTable ?: "<p>No dataset uploaded yet.</p>"; ?>
    </div>

    <!-- INSIGHT -->
    <div class="card highlight" style="grid-column: span 2;">
        <h2>Recommended Resource Allocation</h2>
        <p id="insightText"></p>
    </div>

    <!-- TABLE -->
    <div class="card" style="grid-column: span 2;">
        <h2>Forecast Table</h2>
        <table id="forecastTable">
            <tr>
                <th>Year</th>
                <th>Enrollees</th>
                <th>Acad Rooms</th>
                <th>TVL Rooms</th>
                <th>Acad Teachers</th>
                <th>TVL Teachers</th>
            </tr>
        </table>
    </div>

</div>

<script>
fetch('forecast.csv')
.then(res => res.text())
.then(data => {
    let rows = data.split("\n");

    let labels = [];
    let values = [];

    let table = document.getElementById("forecastTable");

    for(let i=1; i<rows.length; i++){
        let cols = rows[i].split(",");
        if(cols.length < 6) continue;

        let year = cols[0].substring(0,4);
        let total = Math.round(cols[1]);

        labels.push(year);
        values.push(total);

        let row = table.insertRow();
        for(let j=0; j<6; j++){
            row.insertCell(j).innerText = Math.round(cols[j]);
        }
    }

    new Chart(document.getElementById("forecastChart"), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Enrollees',
                data: values
            }]
        }
    });

    let latest = rows[rows.length-2].split(",");

    document.getElementById("insightText").innerHTML = `
        📊 Enrollees: ${latest[1]}<br>
        🏫 Academic Rooms: ${latest[2]}<br>
        🏫 TVL Rooms: ${latest[3]}<br>
        👩‍🏫 Academic Teachers: ${latest[4]}<br>
        👩‍🏫 TVL Teachers: ${latest[5]}
    `;
});
</script>

</body>
</html>