# E018 – ECE-050
# Component Tolerance Checker

## 1. Project Overview

The Component Tolerance Checker is a Python-based web application developed as part of the ECE-050 Capstone Project.

The application is designed to check whether an electronic component operates within its specified tolerance limits. It calculates the acceptable minimum and maximum values based on the rated value and tolerance percentage.

The system compares the measured component value with the calculated limits and displays the result as PASS or FAIL.

The project uses Python, Flask, and MySQL to provide a simple web-based interface and store inspection records for future reference.

## 2. Objectives

- To develop a web-based component tolerance checking system.
- To calculate minimum and maximum tolerance limits automatically.
- To identify whether a component is within the specified tolerance range.
- To display PASS or FAIL inspection results.
- To store component inspection records in a MySQL database.
- To maintain inspection history for future reference.
- To simplify and improve the component testing process.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| HTML | Webpage structure |
| CSS | User interface styling |
| MySQL | Database management |
| MySQL Connector | Python–MySQL connectivity |
| Visual Studio Code | Development environment |
| Git & GitHub | Version control and project hosting |

## 4. Project Features

### Component Tolerance Calculation
Calculates the acceptable minimum and maximum values using the rated value and tolerance percentage.

### PASS/FAIL Detection
Compares the measured value with the acceptable tolerance range.

- PASS – Measured value is within the tolerance limits.
- FAIL – Measured value is outside the tolerance limits.

### Boundary Testing
Checks component values at the tolerance boundaries to ensure accurate results.

### Database Integration
Stores component inspection information in a MySQL database.

### Inspection History
Maintains previously saved inspection records for reviewing past results.

### Batch Processing
Supports processing component inspection data in batches.

## 5. System Requirements

### Hardware Requirements
- Computer or Laptop
- Minimum 4 GB RAM
- Internet connection for GitHub access

### Software Requirements
- Windows Operating System
- Python 3.10 or above
- Visual Studio Code
- MySQL Server 8.0
- Flask
- MySQL Connector for Python
- Git

## 6. Project Folder Structure

```text
E018-ECE-050/
│
├── Python_Project/
├── sample_data/
│
├── app.py
├── app_backup.py
├── main.py
├── database.py
├── batch_processing.py
├── batch_report.txt
├── evaluation.py
├── check_schema.py
├── dashboard_test.py
├── inspect_data.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 7. Installation and Execution

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/E018-ECE-050.git
```

### Step 2: Open the Project Folder

```bash
cd E018-ECE-050
```

### Step 3: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 4: Activate the Virtual Environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 5: Install Required Packages

```bash
pip install -r requirements.txt
```

### Step 6: Configure MySQL

- Start MySQL Server.
- Create the project database.
- Configure the required database connection settings.
- Set the MYSQL_PASSWORD environment variable securely.

Never upload database passwords or other private credentials to GitHub.

### Step 7: Run the Application

```bash
python app.py
```

Open the local Flask address displayed in the terminal in your web browser.

## 8. Working Principle

1. The user opens the Component Tolerance Checker website.
2. The user enters the component details.
3. The system receives the rated value, tolerance percentage, and measured value.
4. The application calculates the minimum and maximum acceptable limits.
5. The measured value is compared with the calculated range.
6. The system displays the PASS or FAIL result.
7. The inspection details are saved in the MySQL database.
8. The user can review previous inspection records through the history feature.

## 9. Testing

The application is tested using different component values.

| Test Case | Description | Expected Result |
|---|---|---|
| Test 1 | Measured value within tolerance | PASS |
| Test 2 | Measured value outside tolerance | FAIL |
| Test 3 | Measured value at minimum boundary | PASS |
| Test 4 | Measured value at
