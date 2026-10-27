
import json
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path


def main():
    report_path = Path("pytest-report.json")
    email_address = os.environ.get("GMAIL_ADDRESS", "").strip()
    app_password = os.environ.get("GMAIL_APP_PASSWORD", "").strip()

    if not email_address or not app_password:
        print("ERROR: Gmail credentials are not configured.")
        return 1

    if not report_path.exists():
        print("ERROR: pytest-report.json was not created.")
        return 1

    with report_path.open("r", encoding="utf-8") as file:
        pytest_data = json.load(file)

    tests = pytest_data.get("tests", [])
    total = len(tests)
    passed = sum(test.get("outcome") == "passed" for test in tests)
    failed = sum(
        test.get("outcome") in ("failed", "error")
        for test in tests
    )

    status = (
        "PASSED"
        if total > 0 and passed == total and failed == 0
        else "FAILED"
    )

    repository = os.environ.get("GITHUB_REPOSITORY", "local")
    branch = os.environ.get("GITHUB_REF_NAME", "local")
    commit_sha = os.environ.get("GITHUB_SHA", "local")
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    run_url = (
        f"https://github.com/{repository}/actions/runs/{run_id}"
        if run_id != "local"
        else "Not available"
    )

    message = EmailMessage()
    message["From"] = email_address
    message["To"] = email_address
    message["Subject"] = (
        f"[Assignment Portal CI] {status}: "
        f"{passed}/{total} tests passed"
    )

    lines = [
        "Assignment Portal automated test report",
        "",
        f"Overall status: {status}",
        f"Repository: {repository}",
        f"Branch: {branch}",
        f"Commit SHA: {commit_sha}",
        f"Pipeline run ID: {run_id}",
        f"Total tests: {total}",
        f"Passed: {passed}",
        f"Failed: {failed}",
        f"Workflow run: {run_url}",
        "",
        "Individual test results:",
    ]

    for test in tests:
        name = test.get("nodeid", "Unknown test")
        outcome = test.get("outcome", "unknown")
        lines.append(f"- {name}: {outcome}")

        for phase in ("setup", "call", "teardown"):
            details = test.get(phase, {})
            if details.get("outcome") == "failed":
                failure = details.get("longrepr", "No failure details")
                lines.append(f"  Failure: {failure}")
                break

    message.set_content("\n".join(lines))

    message.add_attachment(
        report_path.read_bytes(),
        maintype="application",
        subtype="json",
        filename="pytest-report.json",
    )

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(email_address, app_password)
            server.send_message(message)

        print(f"Email report sent. Overall status: {status}")
        return 0

    except (smtplib.SMTPException, OSError) as error:
        print(f"ERROR: Email delivery failed ({type(error).__name__}).")
        return 1


if __name__ == "__main__":
    sys.exit(main())
