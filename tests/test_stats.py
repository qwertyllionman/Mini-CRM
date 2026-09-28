"""
Dashboard statistics unit tests.
Verifies bonus requirement: Dashboard statistics & KPIs.
"""


def test_dashboard_stats_endpoint(client):
    # Seed leads with different statuses
    client.post("/api/leads", json={"name": "Lead A", "phone": "+998901111111", "status": "New", "source": "Telegram"})
    client.post("/api/leads", json={"name": "Lead B", "phone": "+998902222222", "status": "Won", "source": "Website"})
    client.post("/api/leads", json={"name": "Lead C", "phone": "+998903333333", "status": "Lost", "source": "Website"})

    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()

    assert data["total_leads"] >= 3
    assert data["won_leads"] >= 1
    assert data["lost_leads"] >= 1
    assert data["new_leads"] >= 1
    assert isinstance(data["conversion_rate"], float)
    assert len(data["status_distribution"]) == 5
    assert len(data["source_distribution"]) >= 1
    assert len(data["recent_activities"]) >= 1
