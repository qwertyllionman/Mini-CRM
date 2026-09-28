"""
Leads CRUD, search, filter, pagination, and sorting unit tests.
"""


def test_create_lead_success(client, auth_headers):
    payload = {
        "name": "Alisher Navoiy",
        "email": "alisher@example.uz",
        "phone": "+998901112233",
        "source": "Website",
        "status": "New",
        "note": "Potensial yirik mijoz."
    }
    response = client.post("/api/leads", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alisher Navoiy"
    assert data["email"] == "alisher@example.uz"
    assert data["status"] == "New"
    assert "id" in data


def test_create_lead_phone_only(client):
    payload = {
        "name": "Temur Bek",
        "phone": "+998935554433",
        "source": "Telegram"
    }
    response = client.post("/api/leads", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Temur Bek"
    assert data["phone"] == "+998935554433"
    assert data["email"] is None


def test_create_lead_missing_contacts_fails(client):
    payload = {
        "name": "No Contact Person",
        "source": "Website"
    }
    response = client.post("/api/leads", json=payload)
    assert response.status_code == 422
    assert "aloqa ma'lumoti" in str(response.json())


def test_get_lead_by_id(client):
    # First create
    lead_res = client.post("/api/leads", json={
        "name": "Shahnoza Karimova",
        "phone": "+998971234567",
        "source": "Instagram"
    })
    lead_id = lead_res.json()["id"]

    response = client.get(f"/api/leads/{lead_id}")
    assert response.status_code == 200
    assert response.json()["id"] == lead_id
    assert response.json()["name"] == "Shahnoza Karimova"


def test_get_lead_not_found(client):
    response = client.get("/api/leads/999999")
    assert response.status_code == 404


def test_leads_pagination_and_filtering(client):
    # Seed 5 leads
    sources = ["Website", "Telegram", "Instagram", "Website", "Referral"]
    statuses = ["New", "Contacted", "Qualified", "Won", "Lost"]
    for i in range(5):
        client.post("/api/leads", json={
            "name": f"Lead Test {i+1}",
            "phone": f"+99890000000{i}",
            "source": sources[i],
            "status": statuses[i]
        })

    # Test pagination: page_size=2
    res_page1 = client.get("/api/leads?page=1&page_size=2")
    assert res_page1.status_code == 200
    p1_data = res_page1.json()
    assert p1_data["page"] == 1
    assert p1_data["page_size"] == 2
    assert len(p1_data["items"]) == 2
    assert p1_data["total"] >= 5

    # Test status filter: Won
    res_won = client.get("/api/leads?status=Won")
    assert res_won.status_code == 200
    won_data = res_won.json()
    assert all(item["status"] == "Won" for item in won_data["items"])
    assert won_data["total"] >= 1

    # Test source filter: Telegram
    res_tg = client.get("/api/leads?source=Telegram")
    assert res_tg.status_code == 200
    tg_data = res_tg.json()
    assert all(item["source"] == "Telegram" for item in tg_data["items"])


def test_leads_search(client):
    client.post("/api/leads", json={
        "name": "UniqueZilolaSpecialCompany",
        "phone": "+998909998877",
        "email": "zilola@unique.uz",
        "source": "Website"
    })

    # Search by unique name
    res = client.get("/api/leads?search=UniqueZilola")
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) == 1
    assert items[0]["name"] == "UniqueZilolaSpecialCompany"

    # Search by email
    res_email = client.get("/api/leads?search=zilola@unique")
    assert res_email.status_code == 200
    assert len(res_email.json()["items"]) == 1


def test_leads_sorting(client):
    # Sort by name asc
    res_asc = client.get("/api/leads?sort_by=name&order=asc")
    assert res_asc.status_code == 200
    names = [lead["name"] for lead in res_asc.json()["items"]]
    assert names == sorted(names)


def test_update_lead(client, auth_headers):
    lead_res = client.post("/api/leads", json={
        "name": "Old Name",
        "phone": "+998901110000"
    })
    lead_id = lead_res.json()["id"]

    update_payload = {
        "name": "Updated Name",
        "note": "Yangilangan izoh"
    }
    res = client.put(f"/api/leads/{lead_id}", json=update_payload, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Updated Name"
    assert data["note"] == "Yangilangan izoh"


def test_patch_lead_status(client, auth_headers):
    lead_res = client.post("/api/leads", json={
        "name": "Status Transition Lead",
        "phone": "+998907776655",
        "status": "New"
    })
    lead_id = lead_res.json()["id"]

    patch_res = client.patch(
        f"/api/leads/{lead_id}/status",
        json={"status": "Won", "note": "Mijoz shartnoma imzoladi."},
        headers=auth_headers
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "Won"


def test_delete_lead(client):
    lead_res = client.post("/api/leads", json={
        "name": "To be deleted",
        "phone": "+998900000099"
    })
    lead_id = lead_res.json()["id"]

    del_res = client.delete(f"/api/leads/{lead_id}")
    assert del_res.status_code == 200

    # Ensure it no longer exists
    get_res = client.get(f"/api/leads/{lead_id}")
    assert get_res.status_code == 404
