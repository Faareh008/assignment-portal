
from flask import Flask, render_template, request, redirect, url_for
import json
from pathlib import Path
from urllib.parse import urlparse

app = Flask(__name__)

# File where valid submissions will be saved
DATA_FILE = Path(__file__).with_name("submissions.json")


def load_submissions():
    """Load previously saved submissions."""
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


def save_submissions(submissions):
    """Save submissions to a JSON file."""
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(submissions, file, indent=4)


def valid_url(value):
    """Accept only HTTP or HTTPS URLs with a hostname."""
    try:
        parsed = urlparse(value)
        return (
            parsed.scheme in ("http", "https")
            and bool(parsed.hostname)
            and "." in parsed.hostname
            and not any(char.isspace() for char in value)
        )
    except ValueError:
        return False


@app.route("/", methods=["GET", "POST"])
def home():
    error = None
    success = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        reg_no = request.form.get("reg_no", "").strip()
        title = request.form.get("title", "").strip()
        submission_url = request.form.get("submission_url", "").strip()

        if not all([name, reg_no, title, submission_url]):
            error = "All fields are required."

        elif not valid_url(submission_url):
            error = "Please enter a valid HTTP or HTTPS submission URL."

        else:
            submissions = load_submissions()

            submissions.append({
                "name": name,
                "reg_no": reg_no,
                "title": title,
                "submission_url": submission_url
            })

            save_submissions(submissions)

            return redirect(url_for("home", submitted="1"))

    submissions = load_submissions()

    if request.args.get("submitted") == "1":
        success = "Assignment submitted successfully!"

    return render_template(
        "index.html",
        submissions=submissions,
        error=error,
        success=success
    )


if __name__ == "__main__":
    app.run(debug=True)
