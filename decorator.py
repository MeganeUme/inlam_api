from flask import request
from functools import wraps

def log_request_body(endpoint_function):
    @wraps(endpoint_function)
    def wrapper(*args, **kwargs):
        request_body = request.get_data(as_text=True)
        print(f"Request Body: {request_body}")
        return endpoint_function(*args, **kwargs)
    return wrapper