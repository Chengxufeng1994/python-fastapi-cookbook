from models import UserInDB

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "hashed_password": "hashedsecret",
    },
    "janedoe": {
        "username": "janedoe",
        "hashed_password": "hashedsecret2",
    },
}


def fakely_hash_password(password: str):
    return f"hashed{password}"


def fake_token_generator(user: UserInDB) -> str:
    # This doesn't provide any security at all
    return f"tokenized{user.username}"


def get_user(db: dict, username: str) -> UserInDB | None:
    if username in fake_users_db:
        return UserInDB(**fake_users_db[username])
    return None


def fake_token_resolver(
    token: str,
) -> UserInDB | None:
    if token.startswith("tokenized"):
        user_id = token.removeprefix("tokenized")
        user = get_user(fake_users_db, user_id)
        return user

    return None
