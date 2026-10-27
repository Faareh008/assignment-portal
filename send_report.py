
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def main():
    report_path = Path("pytest-report.json")

    receiver_url = os.environ.get("RECEIVER_URL", "").strip()
    receiver_token = os.environ.get("REPORT_RECEIVER_TOKEN", "").strip()

    if not receiver_url or not receiver_token:
        print("ERROR: RECEIVER_URL or REPORT_RECEIVER_TOKEN is missing.")
        return 1

    if not report_path.exists():
        print("ERROR: pytest-report.json was not created.")
        return 1

    with report_path.open("r", encoding="utf-8") as file:
        pytest_data = json.load(file)

    tests = []

    for test in pytest_data.get("tests", []):
        outcome = test.get("outcome", "unknown")
        failure_message = None

        for phase in ("setup", "call", "teardown"):
            phase_data = test.get(phase, {})
            if phase_data.get("outcome") == "failed":
                failure_message = phase_data.get("longrepr")
                break

        tests.append({
            "name": test.get("nodeid", "Unknown test"),
            "result": outcome,
            "failure_message": (
                str(failure_message) if failure_message else None
            ),
        })

    total = len(tests)
    passed = sum(test["result"] == "passed" for test in tests)
    failed = sum(test["result"] in ("failed", "error") for test in tests)

    overall_status = (
        "passed"
        if total > 0 and passed == total and failed == 0
        else "failed"
    )

    report = {
        "repository": os.environ.get("GITHUB_REPOSITORY", "local"),
        "branch": os.environ.get("GITHUB_REF_NAME", "local"),
        "commit_sha": os.environ.get("GITHUB_SHA", "local"),
        "pipeline_run_id": os.environ.get("GITHUB_RUN_ID", "local"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tests": tests,
        "total": total,
        "passed": passed,
        "failed": failed,
        "status": overall_status,
    }

    payload = json.dumps(report).encode("utf-8")
    request = urllib.request.Request(
        receiver_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {receiver_token}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            print(response.read().decode("utf-8"))
            print(f"Report status: {overall_status}")
    except (urllib.error.URLError, TimeoutError) as error:
        print(f"ERROR: Could not send the report: {error}")
        return 1

    # The workflow's pytest step determines whether tests passed or failed.
    return 0


if __name__ == "__main__":
    sys.exit(main())
