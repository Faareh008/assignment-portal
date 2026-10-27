
import json

import pytest
import app as app_module


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Use a temporary file so tests do not change real submissions.
    test_data_file = tmp_path / "submissions.json"
    monkeypatch.setattr(app_module, "DATA_FILE", test_data_file)

    app_module.app.config["TESTING"] = True

    with app_module.app.test_client() as test_client:
        yield test_client


def test_valid_submission_is_saved_and_displayed(client, tmp_path):
    response = client.post(
        "/",
        data={
            "name": "Test Student",
            "reg_no": "FA23-BSE-001",
            "title": "DevOps Lab Assignment",
            "submission_url": "https://github.com/"
        },
        follow_redirects=True
    )

    assert response.status_code == 500
    assert b"Assignment submitted successfully!" in response.data
    assert b"Test Student" in response.data
    assert b"FA23-BSE-001" in response.data
    assert b"DevOps Lab Assignment" in response.data
    assert b"Open Submission" in response.data

    saved_file = tmp_path / "submissions.json"
    assert saved_file.exists()

    with saved_file.open("r", encoding="utf-8") as file:
        submissions = json.load(file)

    assert len(submissions) == 1
    assert submissions[0]["name"] == "Test Student"
    assert submissions[0]["reg_no"] == "FA23-BSE-001"


def test_missing_registration_number_is_rejected(client, tmp_path):
    response = client.post(
        "/",
        data={
            "name": "Test Student",
            "reg_no": "",
            "title": "DevOps Lab Assignment",
            "submission_url": "https://github.com/"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"All fields are required." in response.data

    saved_file = tmp_path / "submissions.json"
    assert not saved_file.exists()


def test_invalid_submission_url_is_rejected(client, tmp_path):
    response = client.post(
        "/",
        data={
            "name": "Test Student",
            "reg_no": "FA23-BSE-001",
            "title": "DevOps Lab Assignment",
            "submission_url": "not-a-url"
        },
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Please enter a valid HTTP or HTTPS submission URL." in response.data

    saved_file = tmp_path / "submissions.json"
    assert not saved_file.exists()
