# Assignment Submission Portal with Automated Testing

## Project Overview

The Assignment Submission Portal is a Flask-based web application that allows students to submit their assignment details through an online form.

The application collects student information, validates submission details, saves submissions, and displays them on the portal.

This project also implements an automated testing and Continuous Integration (CI) pipeline using **Pytest and GitHub Actions**. Whenever code is pushed to the GitHub repository, GitHub Actions automatically installs the required dependencies and executes the test cases.

The project also includes automatic JSON test report delivery, Gmail email notifications, and a GitHub Pages deployment as bonus features.

## Objectives

- Develop a web-based assignment submission portal.
- Validate student information and submission URLs.
- Store and display assignment submissions.
- Implement automated testing using Pytest.
- Configure GitHub Actions for Continuous Integration.
- Generate JSON test reports automatically.
- Send test reports to a local computer without manual downloading.
- Send email notifications for successful and failed test runs.
- Deploy a static demonstration website using GitHub Pages.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Flask | Web application framework |
| HTML | Web form and user interface |
| Pytest | Automated testing |
| pytest-json-report | JSON test report generation |
| Git | Version control |
| GitHub | Source code repository |
| GitHub Actions | CI automation |
| Cloudflare Tunnel | Connects GitHub Actions to the local report receiver |
| Gmail SMTP | Email notifications |
| GitHub Pages | Static website deployment |

## Project Structure

```text
assignment-portal/
│
├── app.py
├── receiver.py
├── send_report.py
├── send_email.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── templates/
│   └── index.html
│
├── tests/
│   └── test_app.py
│
├── docs/
│   └── index.html
│
└── .github/
    └── workflows/
        ├── ci.yml
        └── pages.yml
```

## Application Features

1. Student assignment submission form.
2. Student name and registration number fields.
3. Assignment title and submission URL fields.
4. Required-field validation.
5. Submission URL validation.
6. Saving and displaying assignment submissions.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Faareh008/assignment-portal.git
```

Navigate to the project directory:

```bash
cd assignment-portal
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the virtual environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

## Running the Application

Start the Flask application:

```bash
python app.py
```

Open the following address in your browser:

```text
http://127.0.0.1:5000
```

The assignment submission portal will be available locally.

## Automated Testing

The project uses Pytest to verify the main application functionality.

Run all test cases:

```bash
python -m pytest -v
```

### Test Cases

| Test Case | Description |
|---|---|
| test_valid_submission_is_saved_and_displayed | Checks that a valid assignment submission is accepted, saved, and displayed. |
| test_missing_registration_number_is_rejected | Checks that a submission without a registration number is rejected. |
| test_invalid_submission_url_is_rejected | Checks that an invalid submission URL is rejected. |

The expected successful result is:

```text
3 passed
```

## Continuous Integration Using GitHub Actions

The project uses GitHub Actions to automate the testing process.

The CI workflow is configured in:

```text
.github/workflows/ci.yml
```

### Workflow Process

1. The workflow is triggered when code is pushed to the main branch or a pull request targets main.
2. GitHub Actions checks out the repository.
3. Python 3.13 is configured on the runner.
4. Required dependencies are installed.
5. Pytest executes the automated test cases.
6. A JSON test report is generated.
7. The report is sent to the local computer.
8. An email notification is sent through Gmail for push events.

If an automated test fails, the testing job is marked as failed.

## Automatic JSON Test Report Delivery

The project includes a local Flask report receiver.

Important files:

- `receiver.py`: Receives and saves JSON test reports.
- `send_report.py`: Reads the Pytest report and sends it to the local receiver.

### How It Works

1. The local report receiver runs on port 8000.
2. Cloudflare Tunnel provides a public URL to the local receiver.
3. GitHub Actions sends the test report to the receiver.
4. The receiver verifies the authentication token.
5. The report is saved locally as `test-report.json`.

### Running the Local Receiver

Set the receiver token in PowerShell:

```powershell
$env:REPORT_RECEIVER_TOKEN = "YOUR_RECEIVER_TOKEN"
```

Start the receiver:

```powershell
python receiver.py
```

### Starting Cloudflare Tunnel

Open another terminal and execute:

```bash
cloudflared tunnel --url http://localhost:8000
```

Use the generated tunnel URL in the GitHub repository secret named `RECEIVER_URL`, followed by `/report`.

The tunnel and receiver must remain running for automatic report delivery.

## Gmail Email Notifications

The project includes Gmail SMTP integration through:

```text
send_email.py
```

The script:

1. Reads the generated Pytest JSON report.
2. Calculates total, passed, and failed tests.
3. Creates an email containing the test results.
4. Includes repository, branch, commit SHA, and workflow run information.
5. Attaches the JSON test report.
6. Sends the email through Gmail SMTP using TLS.

### GitHub Repository Secrets

The following secrets are configured under:

**GitHub Repository → Settings → Secrets and variables → Actions**

| Secret Name | Purpose |
|---|---|
| RECEIVER_URL | Public URL of the local report receiver |
| RECEIVER_TOKEN | Authentication token for report delivery |
| GMAIL_ADDRESS | Gmail email address |
| GMAIL_APP_PASSWORD | Gmail App Password for SMTP authentication |

Sensitive credentials are stored as GitHub Actions secrets instead of being hardcoded in the source code.

The email notification step runs even when automated tests fail, allowing failed test reports to be delivered.

## Failure Detection Demonstration

The CI pipeline was tested with both successful and deliberately failed test cases.

### Successful Test Run

All three automated test cases passed, and the workflow completed successfully.

### Failed Test Run

One test assertion was deliberately changed to an incorrect expected status code.

Pytest detected the incorrect assertion, and GitHub Actions marked the test job as failed.

The failure report was also sent through the configured reporting mechanisms.

### Fixing the Failure

The incorrect assertion was restored to the expected HTTP status code of 200.

The tests were executed again, all three tests passed, and the workflow completed successfully.

This demonstrates that the CI pipeline can detect failures and verify fixes.

## Bonus Task: GitHub Pages Deployment

A static demonstration website is available through GitHub Pages.

Live Demo:

https://faareh008.github.io/assignment-portal/

The deployment workflow is configured in:

```text
.github/workflows/pages.yml
```

### Deployment Process

1. GitHub Actions checks out the repository.
2. Python dependencies are installed.
3. Automated tests are executed.
4. The deployment job waits for the test job to succeed.
5. The static website from the `docs` directory is uploaded.
6. GitHub Pages deploys the website.

Deployment is configured for successful pushes to the main branch.

**Note:** The GitHub Pages website is a static demonstration and is separate from the Flask backend application. It does not share the Flask application's submission storage.

## Conclusion

The Assignment Submission Portal demonstrates the use of Flask for web application development and Pytest for automated testing.

GitHub Actions provides Continuous Integration by automatically executing tests whenever code changes are pushed. The project also demonstrates automatic JSON report delivery, Gmail notifications for successful and failed test runs, and conditional GitHub Pages deployment.

Overall, the project demonstrates how automated testing, reporting, and deployment can improve software quality and simplify the development workflow.

## Repository

GitHub Repository:

https://github.com/Faareh008/assignment-portal

GitHub Pages Demo:

https://faareh008.github.io/assignment-portal/