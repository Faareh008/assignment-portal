
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request

app = Flask(__name__)

REPORT_FILE = Path(__file__).with_name("test-report.json")
REPORT_TOKEN = os.environ.get("REPORT_RECEIVER_TOKEN", "")


@app.route("/report", methods=["POST"])
def receive_report():
    # Require a secret token before accepting a report.
    if not REPORT_TOKEN:
        return jsonify({"error": "Receiver token is not configured"}), 500

    supplied_token = request.headers.get("Authorization", "")
    expected_token = f"Bearer {REPORT_TOKEN}"

    if not hmac.compare_digest(supplied_token, expected_token):
        return jsonify({"error": "Unauthorized"}), 401

    report = request.get_json(silent=True)

    if not isinstance(report, dict):
        return jsonify({"error": "A JSON report is required"}), 400

    required_fields = [
        "repository",
        "branch",
        "commit_sha",
        "pipeline_run_id",
        "timestamp",
        "tests",
        "total",
        "passed",
        "failed",
        "status",
    ]

    missing_fields = [field for field in required_fields if field not in report]

    if missing_fields:
        return jsonify({
            "error": "Required report fields are missing",
            "missing_fields": missing_fields,
        }), 400

    # Record when this computer received the report.
    report["received_at"] = datetime.now(timezone.utc).isoformat()

    try:
        with REPORT_FILE.open("w", encoding="utf-8") as file:
            json.dump(report, file, indent=4)
            file.write("\n")
    except OSError:
        app.logger.exception("Could not save the test report")
        return jsonify({"error": "Could not save the report"}), 500

    return jsonify({
        "message": "Report received and saved successfully",
        "file": str(REPORT_FILE),
        "status": report["status"],
    }), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "receiver running"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
