from flask import current_app, jsonify
from ..common.response import standard_response

def handle_500_error(e):
    # Log the error and return a JSON response
    current_app.logger.error(f"Internal Server Error: {str(e)}")
    if current_app.config['DEBUG']:
        current_app.logger.exception(e)
    return standard_response(500, 'Internal Server Error')
