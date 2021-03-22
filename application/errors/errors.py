from flask import Response, current_app, jsonify

from . import errors_bp


class ErrorResponse:
    """
    Class ErrorResponse returns an object Response with given HTTP status
    and json message (attribute error=message content)
    """

    def __init__(self, message: str, http_status: int):
        self.payload = {"error": message}
        self.http_status = http_status

    def to_response(self) -> Response:
        response = jsonify(self.payload)
        response.status_code = self.http_status
        return response


@errors_bp.app_errorhandler(400)
def bad_request_error(err):
    current_app.logger.error(str(err))
    return ErrorResponse(str(err), 400).to_response()
