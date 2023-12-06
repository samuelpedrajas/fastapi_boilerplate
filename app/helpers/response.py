from flask import jsonify

def standard_response(status, message, result=None):
    res = {
        "status": status,
        "message": message,
    }

    if result:
        res["result"] = result

    return jsonify(res), status