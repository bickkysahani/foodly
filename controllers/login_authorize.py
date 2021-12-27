import jwt
from jwt.exceptions import DecodeError


# login  of user is verified by querying by email and id is returned
def login_authorize(request, db_conn):
    try:
        if "Cookie" in request.headers:
            cookies = request.headers["Cookie"]
            logintoken = (
                cookies.split("logintoken=")[1].split(";")[0]
                if "logintoken" in cookies
                else "notoken"
            )
            token_data = jwt.decode(logintoken, "SECRET", algorithms="HS256")
            token_user = token_data["username"]
            user_data = db_conn["users"].find_one({"username": token_user})
            if user_data is None:
                return {"success": False, "_id": None}
            username = user_data["username"]
            if token_user == str(username):
                return {
                    "success": True,
                    "_id": str(user_data["_id"]),
                    "name": user_data["username"],
                }
        else:
            return {"success": False, "_id": None}
    except ValueError:
        return {"success": False, "_id": None}
    except DecodeError:
        return {"success": False, "_id": None}
