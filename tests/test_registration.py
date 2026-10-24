import sqlite3

import pytest
from werkzeug.security import check_password_hash

import app as app_module
from database.db import create_user, get_db, get_user_by_email


def post(client, **overrides):
    data = {"name": "Ann", "email": "ann@example.com", "password": "password1"}
    data.update(overrides)
    return client.post("/register", data=data)


def user_count():
    conn = get_db()
    try:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    finally:
        conn.close()


def test_get_register_renders_form(client):
    response = client.get("/register")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'action="/register"' in html
    assert 'minlength="8"' in html


def test_valid_registration_redirects_and_stores_hash(client):
    response = post(client)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
    user = get_user_by_email("ann@example.com")
    assert user is not None
    assert user["password_hash"] != "password1"
    assert check_password_hash(user["password_hash"], "password1")


def test_success_does_not_start_session(client):
    response = post(client)
    assert "Set-Cookie" not in response.headers


def test_email_lowercased_and_name_stripped(client):
    post(client, name="  Ann  ", email="  ANN@Example.COM ")
    user = get_user_by_email("ann@example.com")
    assert user["name"] == "Ann"


@pytest.mark.parametrize("field", ["name", "email", "password"])
def test_empty_field_rejected(client, field):
    response = post(client, **{field: ""})
    assert response.status_code == 400
    assert "required" in response.get_data(as_text=True)
    assert user_count() == 0


def test_whitespace_only_name_rejected(client):
    assert post(client, name="   ").status_code == 400


def test_missing_field_rejected_not_exception(client):
    response = client.post(
        "/register", data={"name": "Ann", "email": "ann@example.com"}
    )
    assert response.status_code == 400


@pytest.mark.parametrize("email", ["annexample.com", "a.b@c", "a@b@c.com", "@x.com"])
def test_invalid_email_rejected(client, email):
    assert post(client, email=email).status_code == 400
    assert user_count() == 0


def test_short_password_rejected(client):
    assert post(client, password="1234567").status_code == 400


def test_eight_char_password_accepted(client):
    assert post(client, password="12345678").status_code == 302


def test_password_not_stripped(client):
    post(client, password="  abcdef ")
    user = get_user_by_email("ann@example.com")
    assert check_password_hash(user["password_hash"], "  abcdef ")


def test_duplicate_email_rejected_case_insensitive(client):
    post(client)
    response = post(client, email="ANN@example.com")
    assert response.status_code == 400
    assert "already exists" in response.get_data(as_text=True)
    assert user_count() == 1


def test_integrity_error_race_returns_400(client, monkeypatch):
    create_user("Ann", "ann@example.com", "x")
    monkeypatch.setattr(app_module, "get_user_by_email", lambda email: None)
    response = post(client)
    assert response.status_code == 400
    assert user_count() == 1


def test_form_repopulated_without_password(client):
    response = post(client, name="Zed", email="zed@example.com", password="short")
    html = response.get_data(as_text=True)
    assert 'value="Zed"' in html
    assert 'value="zed@example.com"' in html
    assert "short" not in html.replace("Min. 8 characters", "")


def test_create_user_returns_id_and_enforces_unique(client):
    assert create_user("Ann", "ann@example.com", "h") > 0
    with pytest.raises(sqlite3.IntegrityError):
        create_user("Ann2", "ann@example.com", "h")
