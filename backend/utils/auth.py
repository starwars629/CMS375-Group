from flask import request, jsonify

def require_auth(f):
    return

def require_role(f):
    return

def get_current_user():
    return request.currect_user