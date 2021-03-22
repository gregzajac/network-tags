import json
from itertools import chain

from flask import abort, current_app, jsonify, render_template
from sqlalchemy.sql import text

from application.models import NetworkTag
from application.utils import convert_ipv4_to_binary, is_valid_ipv4

from . import endpoints_bp


# TODO: Moving function to start just after starting app
@endpoints_bp.before_app_first_request
def fill_in_cache():
    """
    Loading data from the database to memcached
    """
    try:
        NetworkTag.fill_in_cache(100)
        current_app.logger.info("Data from `network_tags` has been initially cached")

    except:
        current_app.logger.error("Error during initial caching data", exc_info=True)


@endpoints_bp.route("/ip-tags/<string:ip>", methods=["GET"])
def get_ip_tags(ip: str):
    if not is_valid_ipv4(ip):
        abort(400, description=f"Address {ip} does not have IPv4 format")

    tags = ""
    try:
        tags = NetworkTag.get_tags_for_ip(ip)

    except:
        current_app.logger.error(f"Error: ", exc_info=True)

    return jsonify(tags)


@endpoints_bp.route("/ip-tags-report/<string:ip>", methods=["GET"])
def get_ip_tags_report(ip: str):
    if not is_valid_ipv4(ip):
        abort(400, description=f"Address {ip} does not have IPv4 format")

    tags = ""
    try:
        tags = NetworkTag.get_tags_for_ip(ip)

    except:
        current_app.logger.error(f"Error: ", exc_info=True)

    ctx = {"ip": ip, "tags": tags}
    return render_template("endpoints/ip_tags_report.html", **ctx)