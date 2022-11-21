import requests
import json

WHY_DB_GET_URL = 'http://127.0.0.1:5000/get/totpbot/'
WHY_DB_SET_URL = 'http://127.0.0.1:5000/set/totpbot/'

ALLOWED_ROLE_KEY = '--allowed_role--'

datatype = dict[str, str]


def get(guild_id: int) -> datatype:
    return json.loads(requests.get(WHY_DB_GET_URL + str(guild_id)).text)


def set(guild_id: int, value: datatype) -> str:
    # return requests.get(WHY_DB_SET_URL + str(guild_id) + '/' + json.dumps(value)).text
    return requests.post(WHY_DB_SET_URL + str(guild_id), json=value).text


def add_account(guild_id: int, account: str, secret: str) -> str:
    data = get(guild_id)
    data[account] = secret
    return set(guild_id, data)


def remove_account(guild_id: int, account: str) -> str:
    data = get(guild_id)
    del data[account]
    return set(guild_id, data)


def set_allowed_role(guild_id: int, role_id: int) -> str:
    data = get(guild_id)
    data[ALLOWED_ROLE_KEY] = role_id
    return set(guild_id, data)


def get_allowed_role(guild_id: int) -> int:
    return get(guild_id)[ALLOWED_ROLE_KEY]


def create_guild(guild_id: int) -> str:
    return set(guild_id, {})
