from os import environ


def sudo_users(user):
    users = []
    _sudo_ = user
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
user = environ.get("SUDO_USERS", False)
users = sudo_users(user)
OWNER_ID = environ.get("OWNER_ID", 5147897226)
USERS = users.append(OWNER_ID)
CHANNEL_ID = environ.get("CHANNEL_ID", None)
