"""Configuration for pytest."""
import os
import pytest
from app.app import create_app
from app.models import db as _db


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    # Set test database URL
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    return app


@pytest.fixture(scope='function')
def db(app):
    """Create database for testing."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app, db):
    """Create test client."""
    return app.test_client()
