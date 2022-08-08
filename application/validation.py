from werkzeug.exceptions import HTTPException
from flask import make_response
import json

class NotFoundError(HTTPException):
    def __init__(self, status_statement, status_code):
        self.response = make_response(status_statement, status_code)

class DuplicationError(HTTPException):
    def __init__(self, status_statement, status_code):
        self.response = make_response(status_statement, status_code)

class BusinessValidationError(HTTPException):
    def __init__(self, error_message,  error_code, status_code):
        message = {"error_code":error_code, "error_message": error_message}
        self.response = make_response(json.dumps(message), status_code)

class ServerError(HTTPException):
    def __init__(self, status_statement):
        self.response = make_response(status_statement, 500)
