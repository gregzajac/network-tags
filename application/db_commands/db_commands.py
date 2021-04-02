from flask import current_app

from application.models import NetworkTag, db
from application.utils import prepare_data_to_db

from . import db_commands_bp


@db_commands_bp.cli.group()
def db_manage():
    """Database management commands"""
    pass


@db_manage.command()
def add_data():
    """Add data to the database from env_var `DB_JSON_PATH`"""

    # Files over 500k records are loaded partially
    try:
        prepared_data_to_db = prepare_data_to_db(current_app.config["DB_JSON_PATH"])
        all_network_tags_objects = [NetworkTag(**el) for el in prepared_data_to_db]
        tags_length = len(all_network_tags_objects)

        if tags_length > 500000:
            # inserting every 500k records
            parts_500k_number = tags_length // 500000
            for i in range(0, parts_500k_number):
                partial_data = all_network_tags_objects[i * 500000 : (i + 1) * 500000]
                db.session.add_all(partial_data)
                db.session.commit()

            # last partial data
            partial_data = all_network_tags_objects[parts_500k_number * 500000 :]
            db.session.add_all(partial_data)
            db.session.commit()

        else:
            db.session.add_all(all_network_tags_objects)
            db.session.commit()

        msg = (
            "Data has been added to database"
            + f"(file: {current_app.config['DB_JSON_PATH']})"
        )
        current_app.logger.info(msg)

    except Exception:
        msg = (
            "Error during importing data to database"
            + f"(file: {current_app.config['DB_JSON_PATH']})"
        )
        current_app.logger.error(msg, exc_info=True)


@db_manage.command()
def remove_data():
    """Remove all data from the database"""

    try:
        db.session.execute("DELETE FROM network_tags;")
        db.session.commit()

        msg = "All data has been deleted from database"
        current_app.logger.info(msg)
        print(msg)

    except Exception as exc:
        msg = f"Error during removing data from the database: {exc}"
        current_app.logger.error(msg)
