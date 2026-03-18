#raw user database docs -> api friendly format; also used for response model
def user_helper(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
    }