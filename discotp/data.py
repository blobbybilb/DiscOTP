from sqlitedict import SqliteDict  # type: ignore
from typing import TypedDict


class Account(TypedDict):
    name: str
    secret: str


class ServerConfig(TypedDict):
    id: int
    auth_role: int
    auth_channel: int
    accounts: list[Account]


db = SqliteDict("data.sqlite", autocommit=True)


def get_server_config(server_id: int) -> ServerConfig | None:
    try:
        return db[str(server_id)]
    except KeyError:
        return None


def set_server_config(server_id: int, config: ServerConfig):
    db[str(server_id)] = config


def is_configured(server_id: int) -> bool:
    return get_server_config(server_id) is not None


def get_account(server_id: int, account_name: str) -> Account | None:
    config = get_server_config(server_id)
    if config is None:
        return None

    for account in config["accounts"]:
        if account["name"] == account_name:
            return account

    return None


def account_exists(server_id: int, account_name: str) -> bool:
    return get_account(server_id, account_name) is not None


def add_account(server_id: int, account: Account) -> bool:
    config = get_server_config(server_id)
    if config is None:
        print(2, server_id, account)
        return False

    if account_exists(server_id, account["name"]):
        print(3)
        return False

    config["accounts"].append(account)
    set_server_config(server_id, config)
    return True


def delete_account(server_id: int, account_name: str) -> bool:
    config = get_server_config(server_id)
    if config is None:
        return False

    for i, account in enumerate(config["accounts"]):
        if account["name"] == account_name:
            del config["accounts"][i]
            set_server_config(server_id, config)
            return True

    return False


def update_account(server_id: int, account: Account) -> bool:
    config = get_server_config(server_id)
    if config is None:
        return False

    for i, a in enumerate(config["accounts"]):
        if a["name"] == account["name"]:
            config["accounts"][i] = account
            set_server_config(server_id, config)
            return True

    return False


def get_account_names(server_id: int) -> list[str]:
    config = get_server_config(server_id)
    if config is None:
        return []

    return [account["name"] for account in config["accounts"]]
