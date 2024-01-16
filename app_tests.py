from fastapi.testclient import TestClient

import app

client = TestClient(app.app)


def fakeredis_address_storage():
    """Function for creating fakeredis client for tests"""
    import fakeredis

    redis_client = fakeredis.FakeRedis()
    redis_client.set("9991112233", "test address")
    return redis_client


def fake_ahunt_address_suggestions(*_):
    """Function to mock processed ahunt API response"""
    return ["valid test address"]


def test_check_data_that_is_in_storage(monkeypatch):
    """Test function that checks if response is correct when checking data that
    is in storage"""
    monkeypatch.setattr(app, "address_storage", fakeredis_address_storage())
    response = client.get("/check_data/89991112233")
    assert response.status_code == 200
    assert response.json()["address"] == "test address"


def test_check_data_is_not_in_storage(monkeypatch):
    """Test function that checks if response is correct when checking data that
    is not in storage"""
    monkeypatch.setattr(app, "address_storage", fakeredis_address_storage())
    response = client.get("/check_data/89993332211")
    assert response.status_code == 200
    assert response.json() == "No such phone in storage"


def test_add_new_data_with_wrong_phone(monkeypatch):
    """Test function that checks if response is correct when trying to add data
    with wrong phone number"""
    monkeypatch.setattr(app, "address_storage", fakeredis_address_storage())
    monkeypatch.setattr(
        app, "ahunt_address_suggestions", fake_ahunt_address_suggestions
    )
    response = client.post(
        "/write_data",
        json={
            "phone": "phone_with_wrong_symbols",
            "address": "valid test address",
        },
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "Phone not validated"


def test_add_new_data_with_wrong_address(monkeypatch):
    """Test function that checks if response is correct when trying to add data
    with wrong address"""
    monkeypatch.setattr(app, "address_storage", fakeredis_address_storage())
    monkeypatch.setattr(
        app, "ahunt_address_suggestions", fake_ahunt_address_suggestions
    )
    response = client.post(
        "/write_data",
        json={"phone": "89994445566", "address": "invalid test address"},
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "Address not validated"


def test_add_new_data_correct(monkeypatch):
    """Test function that checks if response is correct when trying to add data
    with correct address and phone number"""
    monkeypatch.setattr(app, "address_storage", fakeredis_address_storage())
    monkeypatch.setattr(
        app, "ahunt_address_suggestions", fake_ahunt_address_suggestions
    )
    response = client.post(
        "/write_data",
        json={"phone": "89994445566", "address": "valid test address"},
    )
    assert response.status_code == 201
    assert response.json() == "Created"


def test_update_data_that_is_not_in_storage(monkeypatch):
    """Test function that checks if response is correct when trying to update
    data that is not in storage"""
    monkeypatch.setattr(app, "address_storage", fakeredis_address_storage())
    monkeypatch.setattr(
        app, "ahunt_address_suggestions", fake_ahunt_address_suggestions
    )
    response = client.patch(
        "/write_data",
        json={"phone": "89993332211", "address": "valid test address"},
    )
    assert response.status_code == 200
    assert response.json() == "No such phone in storage"


def test_update_data_with_wrong_address(monkeypatch):
    """Test function that checks if response is correct when trying to update
    data with wrong address"""
    monkeypatch.setattr(app, "address_storage", fakeredis_address_storage())
    monkeypatch.setattr(
        app, "ahunt_address_suggestions", fake_ahunt_address_suggestions
    )
    response = client.patch(
        "/write_data",
        json={"phone": "89991112233", "address": "new invalid test address"},
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "Address not validated"


def test_update_data_correct(monkeypatch):
    """Test function that checks if response is correct when trying to update
    data with correct address and phone number"""
    monkeypatch.setattr(app, "address_storage", fakeredis_address_storage())
    monkeypatch.setattr(
        app, "ahunt_address_suggestions", fake_ahunt_address_suggestions
    )
    response = client.patch(
        "/write_data",
        json={"phone": "89991112233", "address": "valid test address"},
    )
    assert response.status_code == 200
    assert response.json() == "Updated"


def test_phone_standard_function():
    """Test function that checks if function for standartizing phone numbers
    working correctly"""
    assert app.phone_standard("89991112233") == "9991112233"
    assert app.phone_standard("+79991112233") == "9991112233"
    assert app.phone_standard("8 999 111 22 33") == "9991112233"
    assert app.phone_standard("+7(999)111-22-33") == "9991112233"
    assert app.phone_standard("8(999)111 22-33") == "9991112233"
    assert app.phone_standard("999") is None
    assert app.phone_standard("999999999999") is None
