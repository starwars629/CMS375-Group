from flask import request, jsonify

def require_auth(f):
    return True

def require_role(f):
    return True

def get_current_user():
    return request.currect_user