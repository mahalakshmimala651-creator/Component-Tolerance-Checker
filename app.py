from flask import Flask, request, render_template_string, send_file
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from io import BytesIO
from decimal import Decimal
from database import get_db_connection, save_inspection
from collections import defaultdict
import re

app = Flask(__name__)


# =====================================================
# 1. ENGINEERING VALUE CONVERSION
# =====================================================

def parse_engineering_value(value):

    if value is None:
        return None

    if isinstance(value, (int, float, Decimal)):
        return float(value)

    value = str(value).strip()

    if value in ("", "--", "-", "NA", "N/A"):
        return None

    match = re.match(
        r"^([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)"
        r"\s*([pnumkKMGTµμ]?)",
        value
    )

    if not match:
        return None

    number = float(match.group(1))
    prefix = match.group(2)

    multipliers = {
        "p": 1e-12,
        "n": 1e-9,
        "u": 1e-6,
        "µ": 1e-6,
        "μ": 1e-6,
        "m": 1e-3,
        "k": 1e3,
        "K": 1e3,
        "M": 1e6,
        "G": 1e9,
        "T": 1e12,
        "": 1
    }

    return number * multipliers[prefix]


# =====================================================
# 2. DATABASE CONNECTION HELPERS
# =====================================================

def get_batch_data():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        query = """
            SELECT
                m.lot_id,
                m.sample_no,
                m.measured_value,
                l.part_no,
                l.lot_size,
                p.part_type,
                p.nominal_value,
                p.unit,
                p.tolerance_pct
            FROM measurements m
            JOIN lots l
                ON m.lot_id = l.lot_id
            JOIN part_specs p
                ON l.part_no = p.part_no
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:

            nominal = parse_engineering_value(
                row["nominal_value"]
            )

            measured = parse_engineering_value(
                row["measured_value"]
            )

            tolerance = parse_engineering_value(
                row["tolerance_pct"]
            )

            if (
                nominal is None
                or measured is None
                or tolerance is None
                or nominal <= 0
                or tolerance < 0
            ):

                row["minimum"] = None
                row["maximum"] = None
                row["result"] = "SKIP"

                continue

            minimum = nominal * (1 - tolerance / 100)
            maximum = nominal * (1 + tolerance / 100)

            row["minimum"] = minimum
            row["maximum"] = maximum

            if minimum <= measured <= maximum:
                row["result"] = "PASS"
            else:
                row["result"] = "FAIL"

        return rows

    finally:

        cursor.close()
        connection.close()


def get_inspection_records():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT *
            FROM component_inspections
            ORDER BY id DESC
        """)

        return cursor.fetchall()

    finally:

        cursor.close()
        connection.close()


# =====================================================
# 3. EXCEL REPORT HELPERS
# =====================================================

def excel_safe(value):

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")

    return value


def format_excel_sheet(worksheet):

    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions

    for cell in worksheet[1]:

        cell.font = Font(
            bold=True,
            color="FFFFFF"
        )

        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="17365D"
        )

        cell.alignment = Alignment(
            horizontal="center"
        )

    for column_cells in worksheet.columns:

        max_length = 0
        column_letter = column_cells[0].column_letter

        for cell in column_cells:

            if cell.value is not None:
                max_length = max(
                    max_length,
                    len(str(cell.value))
                )

        worksheet.column_dimensions[column_letter].width = min(
            max_length + 3,
            35
        )


# =====================================================
# 4. HOME PAGE
# =====================================================

HOME_HTML = """
<!DOCTYPE html>
<html>
<head>

<title>ECE-050 Component Tolerance Checker</title>

<style>

body {
    font-family: Arial;
    background: #edf2f7;
    padding: 25px;
}

.container {
    max-width: 1000px;
    margin: auto;
    background: white;
    padding: 30px;
    border-radius: 12px;
}

h1, h2 {
    color: #17365d;
}

input {
    width: 95%;
    padding: 11px;
    margin: 8px 0 18px;
    border: 1px solid #ccc;
    border-radius: 5px;
}

button, .link {
    background: #17365d;
    color: white;
    padding: 12px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    text-decoration: none;
    margin-right: 8px;
    display: inline-block;
}

.pass {
    color: green;
    font-weight: bold;
}

.fail {
    color: red;
    font-weight: bold;
}

.result {
    background: #e8f5e9;
    padding: 18px;
    margin-top: 20px;
    border-radius: 8px;
}

.error {
    background: #ffe5e5;
    color: darkred;
    padding: 15px;
}

</style>
</head>

<body>

<div class="container">

<h1>ECE-050 Component Tolerance Checker</h1>

<p>Team E018 | Component Quality Inspection System</p>

<hr>

<a class="link" href="/">Home</a>
<a class="link" href="/history">History</a>
<a class="link" href="/dashboard">Dashboard</a>
<a class="link" href="/download-report">Download Excel Report</a>

<h2>Component Inspection</h2>

<form method="POST">

<label>Component Name</label>
<input type="text" name="component" required>

<label>Rated Value</label>
<input type="number" step="any" name="rated" required>

<label>Tolerance (%)</label>
<input type="number" step="any" name="tolerance"
       min="0" max="100" required>

<label>Measured Value</label>
<input type="number" step="any" name="measured" required>

<button type="submit">Check Component</button>

</form>

{% if result %}

<div class="result">

<h2>Inspection Result</h2>

<p>Minimum: {{ minimum }}</p>
<p>Maximum: {{ maximum }}</p>
<p>Measured: {{ measured }}</p>

<h2 class="{{ 'pass' if result == 'PASS' else 'fail' }}">
Result: {{ result }}
</h2>

<p>{{ message }}</p>

</div>

{% endif %}

{% if error %}
<div class="error">{{ error }}</div>
{% endif %}

</div>

</body>
</html>
"""


# =====================================================
# 5. INSPECTION HISTORY
# =====================================================

HISTORY_HTML = """
<!DOCTYPE html>
<html>
<head>

<title>Inspection History</title>

<style>

body {
    font-family: Arial;
    background: #edf2f7;
    padding: 25px;
}

.container {
    background: white;
    padding: 25px;
    border-radius: 12px;
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 11px;
    border: 1px solid #ccc;
    text-align: center;
}

th {
    background: #17365d;
    color: white;
}

.pass {
    color: green;
    font-weight: bold;
}

.fail {
    color: red;
    font-weight: bold;
}

.link {
    display: inline-block;
    background: #17365d;
    color: white;
    padding: 10px 15px;
    border-radius: 5px;
    text-decoration: none;
    margin: 5px;
}

</style>
</head>

<body>

<div class="container">

<h1>Inspection History</h1>

<a class="link" href="/">Home</a>
<a class="link" href="/dashboard">Dashboard</a>
<a class="link" href="/download-report">Download Excel Report</a>

<br><br>

<table>

<tr>
{% for column in columns %}
<th>{{ column }}</th>
{% endfor %}
</tr>

{% for row in records %}
<tr>
{% for column in columns %}
<td>{{ row[column] }}</td>
{% endfor %}
</tr>
{% endfor %}

</table>

{% if not records %}
<p>No inspection records available.</p>
{% endif %}

</div>

</body>
</html>
"""


# =====================================================
# 6. DASHBOARD HTML
# =====================================================

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>

<head>

<title>ECE-050 Quality Dashboard</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>

* {
    box-sizing: border-box;
}

body {
    font-family: Arial;
    background: #edf2f7;
    margin: 0;
    padding: 25px;
}

.container {
    max-width: 1250px;
    margin: auto;
}

.header {
    background: #17365d;
    color: white;
    padding: 25px;
    border-radius: 12px;
    margin-bottom: 25px;
}

.header h1 {
    margin-top: 0;
}

nav a {
    display: inline-block;
    background: white;
    color: #17365d;
    padding: 10px 16px;
    margin: 5px;
    border-radius: 5px;
    text-decoration: none;
}

.cards {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(180px, 1fr));
    gap: 18px;
    margin-bottom: 25px;
}

.card {
    background: white;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 8px #d0d7df;
}

.card h3 {
    color: #526477;
    font-size: 15px;
}

.card h2 {
    font-size: 30px;
    color: #17365d;
}

.pass-text {
    color: green !important;
}

.fail-text {
    color: red !important;
}

.chart-grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(320px, 1fr));
    gap: 20px;
    margin-bottom: 25px;
}

.chart-card {
    background: white;
    padding: 22px;
    border-radius: 10px;
    box-shadow: 0 2px 8px #d0d7df;
    min-width: 0;
}

.chart-card h2 {
    color: #17365d;
    font-size: 19px;
}

.chart-container {
    position: relative;
    height: 300px;
}

.table-card {
    background: white;
    padding: 22px;
    border-radius: 10px;
    overflow-x: auto;
    margin-bottom: 25px;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 12px;
    border: 1px solid #ddd;
    text-align: center;
}

th {
    background: #17365d;
    color: white;
}

.pass {
    color: green;
    font-weight: bold;
}

.fail {
    color: red;
    font-weight: bold;
}

.footer {
    text-align: center;
    color: #667;
    padding: 20px;
}

@media(max-width: 600px) {
    body {
        padding: 10px;
    }

    .chart-grid {
        grid-template-columns: 1fr;
    }
}

</style>

</head>

<body>

<div class="container">

<div class="header">

<h1>ECE-050 Quality Inspection Dashboard</h1>

<p>Team E018 | Component Tolerance Checker</p>

<nav>
<a href="/">Home</a>
<a href="/history">Inspection History</a>
<a href="/dashboard">Dashboard</a>
<a href="/download-report">Download Excel Report</a>
</nav>

</div>

<div class="cards">

<div class="card">
<h3>Total Measurements</h3>
<h2>{{ total }}</h2>
</div>

<div class="card">
<h3>PASS Measurements</h3>
<h2 class="pass-text">{{ passed }}</h2>
</div>

<div class="card">
<h3>FAIL Measurements</h3>
<h2 class="fail-text">{{ failed }}</h2>
</div>

<div class="card">
<h3>Skipped Measurements</h3>
<h2>{{ skipped }}</h2>
</div>

<div class="card">
<h3>Production Lots</h3>
<h2>{{ lots }}</h2>
</div>

<div class="card">
<h3>Component Specifications</h3>
<h2>{{ specifications }}</h2>
</div>

<div class="card">
<h3>Manual Inspections</h3>
<h2>{{ manual_total }}</h2>
</div>

</div>

<div class="chart-grid">

<div class="chart-card">
<h2>PASS / FAIL Distribution</h2>
<div class="chart-container">
<canvas id="donutChart"></canvas>
</div>
</div>

<div class="chart-card">
<h2>Overall Quality Analysis</h2>
<div class="chart-container">
<canvas id="qualityChart"></canvas>
</div>
</div>

<div class="chart-card">
<h2>Component-wise PASS / FAIL</h2>
<div class="chart-container">
<canvas id="componentChart"></canvas>
</div>
</div>

<div class="chart-card">
<h2>Batch-wise Inspection Results</h2>
<div class="chart-container">
<canvas id="batchChart"></canvas>
</div>
</div>

</div>

<div class="table-card">

<h2>Component Quality Summary</h2>

<table>

<tr>
<th>Part Number</th>
<th>Component</th>
<th>Total</th>
<th>PASS</th>
<th>FAIL</th>
<th>Skipped</th>
<th>Pass Percentage</th>
</tr>

{% for item in component_stats %}

<tr>
<td>{{ item.part_no }}</td>
<td>{{ item.part_type }}</td>
<td>{{ item.total }}</td>
<td class="pass">{{ item.passed }}</td>
<td class="fail">{{ item.failed }}</td>
<td>{{ item.skipped }}</td>
<td>{{ item.percentage }}%</td>
</tr>

{% endfor %}

</table>

</div>

<div class="table-card">

<h2>Production Batch Quality Summary</h2>

<table>

<tr>
<th>Lot ID</th>
<th>Part Number</th>
<th>Total</th>
<th>PASS</th>
<th>FAIL</th>
<th>Skipped</th>
<th>Pass Percentage</th>
</tr>

{% for item in batch_stats %}

<tr>
<td>{{ item.lot_id }}</td>
<td>{{ item.part_no }}</td>
<td>{{ item.total }}</td>
<td class="pass">{{ item.passed }}</td>
<td class="fail">{{ item.failed }}</td>
<td>{{ item.skipped }}</td>
<td>{{ item.percentage }}%</td>
</tr>

{% endfor %}

</table>

</div>

<div class="footer">

ECE-050 Capstone Project | Team E018

<br>

Component Quality Inspection and Tolerance Analysis

</div>

</div>

<script>

const passed = {{ passed | tojson }};
const failed = {{ failed | tojson }};
const skipped = {{ skipped | tojson }};

const componentLabels = {{ component_labels | tojson }};
const componentPass = {{ component_pass | tojson }};
const componentFail = {{ component_fail | tojson }};

const batchLabels = {{ batch_labels | tojson }};
const batchPass = {{ batch_pass | tojson }};
const batchFail = {{ batch_fail | tojson }};

new Chart(document.getElementById("donutChart"), {

    type: "doughnut",

    data: {
        labels: ["PASS", "FAIL", "SKIPPED"],

        datasets: [{
            data: [passed, failed, skipped],
            backgroundColor: [
                "#28a745",
                "#dc3545",
                "#ffc107"
            ],
            borderWidth: 2
        }]
    },

    options: {
        responsive: true,
        maintainAspectRatio: false,

        plugins: {
            legend: {
                position: "bottom"
            }
        }
    }

});

new Chart(document.getElementById("qualityChart"), {

    type: "bar",

    data: {
        labels: ["PASS", "FAIL", "SKIPPED"],

        datasets: [{
            label: "Measurements",

            data: [passed, failed, skipped],

            backgroundColor: [
                "#28a745",
                "#dc3545",
                "#ffc107"
            ]
        }]
    },

    options: {
        responsive: true,
        maintainAspectRatio: false,

        scales: {
            y: {
                beginAtZero: true
            }
        }
    }

});

new Chart(document.getElementById("componentChart"), {

    type: "bar",

    data: {
        labels: componentLabels,

        datasets: [

            {
                label: "PASS",
                data: componentPass,
                backgroundColor: "#28a745"
            },

            {
                label: "FAIL",
                data: componentFail,
                backgroundColor: "#dc3545"
            }

        ]
    },

    options: {
        responsive: true,
        maintainAspectRatio: false,

        scales: {
            y: {
                beginAtZero: true
            }
        }
    }

});

new Chart(document.getElementById("batchChart"), {

    type: "bar",

    data: {
        labels: batchLabels,

        datasets: [

            {
                label: "PASS",
                data: batchPass,
                backgroundColor: "#28a745"
            },

            {
                label: "FAIL",
                data: batchFail,
                backgroundColor: "#dc3545"
            }

        ]
    },

    options: {
        responsive: true,
        maintainAspectRatio: false,

        scales: {
            y: {
                beginAtZero: true
            }
        }
    }

});

</script>

</body>
</html>
"""


# =====================================================
# 7. HOME ROUTE
# =====================================================

@app.route("/", methods=["GET", "POST"])
def home():

    result = None
    minimum = None
    maximum = None
    measured = None
    message = None
    error = None

    if request.method == "POST":

        try:

            component = request.form["component"].strip()
            rated = float(request.form["rated"])
            tolerance = float(request.form["tolerance"])
            measured = float(request.form["measured"])

            if not component:
                raise ValueError("Enter component name.")

            if rated <= 0:
                raise ValueError("Rated value must be positive.")

            if tolerance < 0 or tolerance > 100:
                raise ValueError(
                    "Tolerance must be between 0 and 100."
                )

            minimum = rated - rated * tolerance / 100
            maximum = rated + rated * tolerance / 100

            if minimum <= measured <= maximum:
                result = "PASS"
                message = "Component is within tolerance."
            else:
                result = "FAIL"
                message = "Component is outside tolerance."

            save_inspection(
                component,
                rated,
                tolerance,
                measured,
                minimum,
                maximum,
                result
            )

        except ValueError as e:

            error = str(e)

        except Exception as e:

            error = "Inspection error: " + str(e)

    return render_template_string(
        HOME_HTML,
        result=result,
        minimum=minimum,
        maximum=maximum,
        measured=measured,
        message=message,
        error=error
    )


# =====================================================
# 8. HISTORY ROUTE
# =====================================================

@app.route("/history")
def history():

    try:

        records = get_inspection_records()

        columns = list(records[0].keys()) if records else []

        return render_template_string(
            HISTORY_HTML,
            records=records,
            columns=columns
        )

    except Exception as e:

        return "History error: " + str(e)


# =====================================================
# 9. DASHBOARD ROUTE
# =====================================================

@app.route("/dashboard")
def dashboard():

    try:

        rows = get_batch_data()

        total = len(rows)

        passed = sum(
            1 for row in rows
            if row["result"] == "PASS"
        )

        failed = sum(
            1 for row in rows
            if row["result"] == "FAIL"
        )

        skipped = sum(
            1 for row in rows
            if row["result"] == "SKIP"
        )

        manual_records = get_inspection_records()
        manual_total = len(manual_records)

        components = defaultdict(
            lambda: {
                "part_type": "",
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        )

        batches = defaultdict(
            lambda: {
                "part_no": "",
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        )

        for row in rows:

            part_no = row["part_no"]
            lot_id = row["lot_id"]

            component = components[part_no]
            component["part_type"] = row["part_type"]
            component["total"] += 1

            batch = batches[lot_id]
            batch["part_no"] = part_no
            batch["total"] += 1

            if row["result"] == "PASS":

                component["passed"] += 1
                batch["passed"] += 1

            elif row["result"] == "FAIL":

                component["failed"] += 1
                batch["failed"] += 1

            else:

                component["skipped"] += 1
                batch["skipped"] += 1

        component_stats = []

        for part_no, item in sorted(components.items()):

            percentage = (
                item["passed"] / item["total"] * 100
                if item["total"] else 0
            )

            component_stats.append({
                "part_no": part_no,
                "part_type": item["part_type"],
                "total": item["total"],
                "passed": item["passed"],
                "failed": item["failed"],
                "skipped": item["skipped"],
                "percentage": round(percentage, 2)
            })

        batch_stats = []

        for lot_id, item in sorted(batches.items()):

            percentage = (
                item["passed"] / item["total"] * 100
                if item["total"] else 0
            )

            batch_stats.append({
                "lot_id": lot_id,
                "part_no": item["part_no"],
                "total": item["total"],
                "passed": item["passed"],
                "failed": item["failed"],
                "skipped": item["skipped"],
                "percentage": round(percentage, 2)
            })

        component_labels = [
            item["part_no"] for item in component_stats
        ]

        component_pass = [
            item["passed"] for item in component_stats
        ]

        component_fail = [
            item["failed"] for item in component_stats
        ]

        batch_labels = [
            str(item["lot_id"]) for item in batch_stats
        ]

        batch_pass = [
            item["passed"] for item in batch_stats
        ]

        batch_fail = [
            item["failed"] for item in batch_stats
        ]

        connection = get_db_connection()
        cursor = connection.cursor()

        try:

            cursor.execute("SELECT COUNT(*) FROM lots")
            lots = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM part_specs")
            specifications = cursor.fetchone()[0]

        finally:

            cursor.close()
            connection.close()

        return render_template_string(
            DASHBOARD_HTML,
            total=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            lots=lots,
            specifications=specifications,
            manual_total=manual_total,
            component_stats=component_stats,
            batch_stats=batch_stats,
            component_labels=component_labels,
            component_pass=component_pass,
            component_fail=component_fail,
            batch_labels=batch_labels,
            batch_pass=batch_pass,
            batch_fail=batch_fail
        )

    except Exception as e:

        return "Dashboard error: " + str(e)


# =====================================================
# 10. EXCEL REPORT DOWNLOAD
# =====================================================

@app.route("/download-report")
def download_report():

    try:

        workbook = Workbook()

        # ---------------------------------------------
        # SHEET 1: MANUAL INSPECTIONS
        # ---------------------------------------------

        manual_sheet = workbook.active
        manual_sheet.title = "Manual Inspections"

        manual_records = get_inspection_records()

        if manual_records:

            manual_columns = list(manual_records[0].keys())

            manual_sheet.append(manual_columns)

            for record in manual_records:

                manual_sheet.append([
                    excel_safe(record.get(column))
                    for column in manual_columns
                ])

        else:

            manual_sheet.append(["No manual inspection records available"])

        format_excel_sheet(manual_sheet)

        # ---------------------------------------------
        # SHEET 2: BATCH MEASUREMENTS
        # ---------------------------------------------

        batch_sheet = workbook.create_sheet(
            title="Batch Measurements"
        )

        batch_columns = [
            "Lot ID",
            "Sample Number",
            "Part Number",
            "Component",
            "Lot Size",
            "Nominal Value",
            "Unit",
            "Tolerance Percentage",
            "Measured Value",
            "Minimum Allowed",
            "Maximum Allowed",
            "Inspection Result"
        ]

        batch_sheet.append(batch_columns)

        batch_records = get_batch_data()

        for row in batch_records:

            batch_sheet.append([

                excel_safe(row.get("lot_id")),
                excel_safe(row.get("sample_no")),
                excel_safe(row.get("part_no")),
                excel_safe(row.get("part_type")),
                excel_safe(row.get("lot_size")),
                excel_safe(row.get("nominal_value")),
                excel_safe(row.get("unit")),
                excel_safe(row.get("tolerance_pct")),
                excel_safe(row.get("measured_value")),
                excel_safe(row.get("minimum")),
                excel_safe(row.get("maximum")),
                excel_safe(row.get("result"))

            ])

        format_excel_sheet(batch_sheet)

        # ---------------------------------------------
        # CREATE EXCEL FILE IN MEMORY
        # ---------------------------------------------

        output = BytesIO()

        workbook.save(output)
        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="ECE050_Quality_Report.xlsx",
            mimetype=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )

    except Exception as e:

        return "Excel report error: " + str(e)


# =====================================================
# 11. START APPLICATION
# =====================================================

if __name__ == "__main__":

    print("ECE-050 Component Tolerance Checker")
    print("Team E018")
    print("Starting Flask Application...")

    app.run(debug=True)