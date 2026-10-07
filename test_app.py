from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.certificate_generator import generate_certificate


client = TestClient(app)


def test_create_generation_job():
    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Test Workshop",
            "event_date": "2026-10-10",
            "recipients": [
                {
                    "name": "Test User",
                    "email": "test@example.com"
                }
            ]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "job_id" in data
    assert data["total"] == 1
    assert data["status"] == "queued"


def test_invalid_email():
    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Test Workshop",
            "event_date": "2026-10-10",
            "recipients": [
                {
                    "name": "Test User",
                    "email": "not-an-email"
                }
            ]
        }
    )

    assert response.status_code == 422


def test_certificate_generation():
    file_path = generate_certificate(
        certificate_id=9999,
        recipient_name="Test User",
        event_name="Test Workshop",
        event_date="2026-10-10"
    )

    assert Path(file_path).exists()

    Path(file_path).unlink()


def test_job_status():
    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Status Test",
            "event_date": "2026-10-10",
            "recipients": [
                {
                    "name": "Test User",
                    "email": "status@example.com"
                }
            ]
        }
    )

    job_id = response.json()["job_id"]

    response = client.get(f"/api/jobs/{job_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == job_id
    assert data["total"] == 1


def test_certificate_retrieval():
    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Retrieval Test",
            "event_date": "2026-10-10",
            "recipients": [
                {
                    "name": "Test User",
                    "email": "retrieve@example.com"
                }
            ]
        }
    )

    job_id = response.json()["job_id"]

    # Get the certificate created for this job
    from app.database import SessionLocal
    from app.models import Certificate

    db = SessionLocal()

    certificate = db.query(Certificate).filter(
        Certificate.job_id == job_id
    ).first()

    db.close()

    response = client.get(
        f"/api/certificates/{certificate.id}"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"