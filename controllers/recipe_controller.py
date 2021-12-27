from bson import json_util, ObjectId
import json


# functions to add recipe to database
def add_recipe_controller(payload, db_conn):
    try:
        result = db_conn["recipes"].insert_one(payload)
        print(result.inserted_id)
        print(result.acknowledged)
        return {
            "success": True,
            "message": "Recipe created successfully",
        }

    except Exception as e:
        return {"success": False, "message": "Error in api: " + str(e)}


# function to query all recipe from database
def all_recipe_controller(filters, db_conn):
    print("from all recipe...")
    print("filter :", filters)
    try:
        result = db_conn["recipes"].find(filters).sort("createdOn", -1)
        recipe_list = map_response(result)
        return recipe_list
    except Exception as e:
        print(e)
        return {"success": False, "message": "Error in api: " + str(e)}


def single_recipe_controller(filters, db_conn):
    print("from single recipe...")
    print("filter :", filters)

    try:
        result = db_conn["recipes"].find(filters).sort("createdOn", -1).limit(1)
        recipe_list = map_response(result)
        return recipe_list

    except Exception as e:
        print(e)
        return {"success": False, "message": "Error in api: " + str(e)}


def map_response(data):
    try:
        result = []
        for d in data:
            # print("id", str(d['_id']))
            result.append(
                {
                    "id": str(d["_id"]),
                    "userid": str(d["userId"]),
                    "recipeName": d["recipeName"],
                    "createdOn": str(d["createdOn"]).split(" ")[0],
                    "imageUrl": d["imageUrl"],
                    "ingredients": str(d["ingredients"]),
                    "instructions": str(d["instructions"]),
                    "meal_type":d["meal_type"],
                }
            )
        return result
    except Exception as e:
        print("error--e", e)
        return []
