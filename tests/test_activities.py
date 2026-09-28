"""
Audit trail / LeadActivity history tests.
Verifies bonus requirement: Activity / History tracking.
"""


def test_creation_activity_logged(client):
    lead_res = client.post("/api/leads", json={
        "name": "Audit Test Lead",
        "email": "audit@test.com",
        "source": "Website"
    })
    lead_id = lead_res.json()["id"]

    activities_res = client.get(f"/api/leads/{lead_id}/activities")
    assert activities_res.status_code == 200
    activities = activities_res.json()
    assert len(activities) >= 1
    assert activities[0]["action"] == "CREATED"
    assert "Audit Test Lead" in activities[0]["description"]


def test_status_change_activity_logged(client, auth_headers):
    lead_res = client.post("/api/leads", json={
        "name": "Status Audit Lead",
        "phone": "+998901239876",
        "status": "New"
    })
    lead_id = lead_res.json()["id"]

    # Transition to Contacted
    client.patch(
        f"/api/leads/{lead_id}/status",
        json={"status": "Contacted", "note": "Birinchi qo'ng'iroq amalga oshirildi."},
        headers=auth_headers
    )

    activities_res = client.get(f"/api/leads/{lead_id}/activities")
    assert activities_res.status_code == 200
    activities = activities_res.json()
    
    # Most recent activity should be STATUS_CHANGED
    latest = activities[0]
    assert latest["action"] == "STATUS_CHANGED"
    assert latest["old_status"] == "New"
    assert latest["new_status"] == "Contacted"
    assert "Birinchi qo'ng'iroq" in latest["description"]


def test_update_activity_logged(client, auth_headers):
    lead_res = client.post("/api/leads", json={
        "name": "Initial Name",
        "phone": "+998901234500"
    })
    lead_id = lead_res.json()["id"]

    client.put(
        f"/api/leads/{lead_id}",
        json={"name": "Renamed Person"},
        headers=auth_headers
    )

    activities_res = client.get(f"/api/leads/{lead_id}/activities")
    activities = activities_res.json()
    latest = activities[0]
    assert latest["action"] == "UPDATED"
    assert "Renamed Person" in latest["description"]
