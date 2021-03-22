from flask import Blueprint

endpoints_bp = Blueprint("endpoints", __name__, template_folder="templates")

from . import endpoints
