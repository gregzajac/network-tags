import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from application import create_app
from application.db_commands.db_commands import add_data
from application.models import db


@pytest.fixture
def app_old():
    """
    Fixture app returning an instance of Flask app
    with created models in the database
    """

    app = create_app("testing")
    with app.app_context():
        db.create_all()

        yield app
        db.drop_all()


@pytest.fixture
def app():
    """Fixture app returning an instance of Flask app"""

    app = create_app("testing")
    return app


@pytest.fixture
def database(app):

    with app.app_context():
        db.drop_all()
        db.create_all()

        yield db


@pytest.fixture
def client(app):
    """
    Fixture client returns a test client for testing
    HTTP requests
    """

    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_data(app):
    """
    Fixture sample_data prowides database with
    sample_data loaded from `DB_JSON_PATH` file
    """

    runner = app.test_cli_runner()
    runner.invoke(add_data)


@pytest.fixture
def selenium():
    opts = Options()
    opts.headless = True

    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(5)

    yield driver
    driver.quit()