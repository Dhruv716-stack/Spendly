import pathlib
import tempfile

import pytest

import database.db as db

# app.py runs init_db()/seed_db() at import time, so point the DB at a
# throwaway file before importing it.
db.DB_PATH = str(pathlib.Path(tempfile.mkdtemp()) / "import.db")

import app as app_module  # noqa: E402


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    app_module.app.config.update(TESTING=True)
    return app_module.app


@pytest.fixture
def client(app):
    return app.test_client()
