from os import environ


def sudo_users():
    users = []
    _sudo_ = environ.get("SUDO_USERS", None)
    if _sudo_:
        _list_ = _sudo_.split(" ")
        for sudo in _list_:
            if sudo.isnumeric():
                users.append(int(sudo))
    return users


API_ID = environ.get("API_ID", 0)
API_HASH = environ.get("API_HASH", None)
BOT_TOKEN = environ.get("BOT_TOKEN", None)
DB_URI = environ.get("DATABASE_URL", None)
USERS = sudo_users()
