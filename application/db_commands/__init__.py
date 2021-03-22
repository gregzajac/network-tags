from flask import Blueprint

db_commands_bp = Blueprint("db_commands", __name__, cli_group=None)

from . import db_commands