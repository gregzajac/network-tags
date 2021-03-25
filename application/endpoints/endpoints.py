from flask import abort, current_app, jsonify, render_template

from application.models import NetworkTag
from application.utils import is_valid_ipv4

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

    except Exception:
        current_app.logger.error("Error during initial caching data", exc_info=True)


@endpoints_bp.route("/ip-tags/<string:ip>", methods=["GET"])
def get_ip_tags(ip: str):
    if not is_valid_ipv4(ip):
        abort(400, description=f"Address {ip} does not have IPv4 format")

    tags = ""
    try:
        tags = NetworkTag.get_tags_for_ip(ip)

    except Exception:
        current_app.logger.error("Error in get_ip_tags: ", exc_info=True)

    return jsonify(tags)


@endpoints_bp.route("/ip-tags-report/<string:ip>", methods=["GET"])
def get_ip_tags_report(ip: str):
    if not is_valid_ipv4(ip):
        abort(400, description=f"Address {ip} does not have IPv4 format")

    tags = ""
    try:
        tags = NetworkTag.get_tags_for_ip(ip)

    except Exception:
        current_app.logger.error("Error in get_ip_tags_report: ", exc_info=True)

    ctx = {"ip": ip, "tags": tags}
    return render_template("endpoints/ip_tags_report.html", **ctx)
