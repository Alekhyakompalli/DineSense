"""
tests/test_api.py
─────────────────
Unit tests for FastAPI REST service (api.py).
Tests health, metadata, and recommendation endpoints.
"""

from unittest.mock import patch
from fastapi.testclient import TestClient
from api import app
from models.restaurant import Recommendation

client = TestClient(app)


def test_api_root():
    """Verify root endpoint returns online status and links."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "/api/health" in data["endpoints"]


def test_api_health():
    """Verify health endpoint returns status, provider, and records count."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["llm_provider"] == "gemini"
    assert data["records_loaded"] > 0


def test_api_metadata():
    """Verify metadata endpoint returns dataset information and filter choices."""
    response = client.get("/api/metadata")
    assert response.status_code == 200
    data = response.json()
    assert "top_locations" in data
    assert len(data["budget_tiers"]) == 3
    assert data["total_records"] > 0


def test_api_recommendation_validation_error():
    """Verify invalid preference submission (empty location) returns 400."""
    response = client.post("/api/recommendations", json={
        "location": "",
        "budget": "medium",
        "cuisines": [],
        "min_rating": 4.0,
    })
    assert response.status_code == 400
    data = response.json()
    assert "errors" in data["detail"]


def test_api_recommendation_success():
    """Verify successful recommendation query returns formatted output."""
    mock_recs = [
        Recommendation(
            rank=1,
            name="The Kind Roastery",
            cuisine="cafe, artisan bakery",
            rating=4.8,
            cost=950,
            explanation="Direct match for courtyard seating.",
        )
    ]

    with patch("api.get_recommendations", return_value=mock_recs):
        response = client.post("/api/recommendations", json={
            "location": "Koramangala, Bangalore",
            "budget": "medium",
            "cuisines": ["cafe"],
            "min_rating": 4.0,
            "extras": "Specialty coffee",
        })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["count"] == 1
    assert data["recommendations"][0]["name"] == "The Kind Roastery"
    assert data["recommendations"][0]["medal"] == "🥇"
    assert data["recommendations"][0]["cost_str"] == "₹950 for two"

