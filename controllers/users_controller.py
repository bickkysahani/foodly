from pprint import pprint
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash


# user signup
def signup_controller(payload, db_conn):
    print("Inside signup_controller")
    try:
        # validate email if it already exists
        email_check = db_conn["users"].find_one({"email": payload["email"]})

        if email_check is None:
            password = payload["password"]
            payload["password"] = generate_password_hash(password)
            # role mapping
            pprint(payload)
            # insert the user
            result = db_conn["users"].insert_one(payload)
            print(result.inserted_id)
            print(result.acknowledged)
            return {
                "success": True,
                "message": "User created successfully",
                "_id": result.inserted_id,
            }
        else:
            return {"success": False, "message": "User already exists"}
    except Exception as e:
        return {"success": False, "message": "Error in api: " + str(e)}


# user login
def login_controller(payload, db_conn):
    print("Inside login_controller")
    try:
        user_data = db_conn["users"].find_one({"username": payload["username"]})
        print(user_data)
        print(str(user_data.get("_id")))
        if user_data:
            print("user data verified")

            if check_password_hash(user_data.get("password"), payload.get("password")):
                print("password verified")
                return {
                    "success": True,
                    "message": "successfully logged in..",
                    "_id": str(user_data.get("_id")),
                }
            else:
                return {"success": False, "message": "Incorrect Password"}

        else:
            return {"success": False, "message": "User does not exist"}
    except Exception as e:
        print(e)
        return {"success": False, "message": "Error in api: " + str(e)}


def get_user_name(userid, db_conn):
    user_data = db_conn["users"].find_one({"_id": ObjectId(userid)})
    return user_data["username"]
