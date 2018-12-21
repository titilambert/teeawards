import hug


_USERNAME = ""
_PASSWORD = ""


def set_admin_auth(username, password):
    global _USERNAME
    global _PASSWORD
    _USERNAME = username
    _PASSWORD = password


def get_auth(username, password):
    if _USERNAME == username and _PASSWORD == password:
        return True
    return False
