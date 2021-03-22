from pathlib import Path

from flask import Flask


def test__app(app):
    """
    GIVEN an instance of Flask app
    WHEN instance is starting
    THEN check if config settings are correct
    """

    assert isinstance(app, Flask)
    assert app.config["TESTING"] is True
    assert app.config["SECRET_KEY"]
    assert app.config["DB_JSON_PATH"].exists()
    assert app.config["ENDPOINT_CASES_PATH"].exists()


def test__database(database):
    """
    GIVEN an instance of database
    WHEN database is starting
    THEN check if request on database is correct
    """

    sql = "select count(9) from network_tags;"
    result = database.session.execute(sql).fetchone()

    assert result[0] == 0