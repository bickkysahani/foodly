from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    url_for,
    make_response,
    jsonify,
)
import jwt
from datetime import datetime, timedelta
from database import db
from controllers.login_authorize import login_authorize
from controllers.users_controller import *
from controllers.recipe_controller import *

app = Flask(__name__)
app.secret_key = "_5#y2L454brbn6567yu"

@app.route('/')
def index():
    login_data = login_authorize(request, db)
    islogin = True if login_data["success"] else False
    response = all_recipe_controller({}, db_conn=db)
    return render_template('index.html',islogin=islogin, result=response)


@app.route('/register', methods=["GET", "POST"])
def register():
    try:
        if request.method == "POST":
            checkbox = (
                request.form.get("checkbox") if "checkbox" in request.form else "off"
            )

            if checkbox == "off":
                error = "Please select terms & condition and proceed"
                return render_template("register.html", error=error)

            payload = dict(
                email=request.form["email"],
                username=request.form["username"],
                password=request.form["password"],
                creadedOn=datetime.now(),
            )
            response = signup_controller(payload=payload, db_conn=db)
            print("response----------------------------", response,payload)
            if response["success"]:
                return redirect(url_for("login"))
            else:
                error = "User already exists"
                return render_template("register.html", error=error)

        return render_template("register.html")
    except Exception as e:
        print("error: ",e)
        return render_template("404.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    try:
        if request.method == "POST":
            payload = dict(
                username=request.form["username"],
                password=request.form["password"],
            )
            # verifying the user login
            response = login_controller(payload, db)
            print("user login verified", response)
            if response["success"]:
                # creating the JWT token for user session
                print("creating JWT token")
                encode = jwt.encode(
                    {
                        "iat": datetime.now(),
                        "username": payload["username"],
                        "exp": datetime.now() + timedelta(days=3),
                    },
                    "SECRET",
                    algorithm="HS256",
                )

                resp = make_response(redirect(url_for("my_recepie")))
                print(str(encode))
                # token = str(encode).split("'")[1]
                token = str(encode)
                # setting cookie using lofin token
                resp.set_cookie("logintoken", token)
                return resp
            else:
                error = "Your email or password didn't match"
                return render_template("login.html", error=error)

        return render_template("login.html")
    except Exception as e:
        print("error: ",e)
        return render_template("404.html")


@app.route("/logout")
def logout():
    try:
        # expering token for logout
        resp = make_response(redirect(url_for("login")))
        resp.set_cookie("logintoken", expires=0)
        return resp
    except Exception as e:
        print("error: ",e)
        return render_template("404.html")


@app.route('/upload-recipe', methods=["GET", "POST"])
def upload_recipe():
    try:
        print("from add recipes...")
        # validating user before adding recipe
        login_data = login_authorize(request, db)
        islogin = True if login_data["success"] else False
        print(login_data)
        # if login is unsuccessfull redirecting to login page again
        if not login_data["success"]:
            return redirect(url_for("login"))
        # we user is logged in reading user input from form
        if request.method == "POST":
            # creating payload dictonary from form to save to database
            payload = dict(
                recipeName=request.form.get("recepiename", None),
                imageUrl=request.form.get("imageurl"),
                ingredients=request.form.get("ingredients", None),
                instructions=request.form.get("instructions", None),
                meal_type=request.form.getlist('options'),
                userId=login_data["_id"],
                createdOn=datetime.now(),
            )
            response = add_recipe_controller(payload=payload, db_conn=db)

            print("response---------", payload)
            return redirect(url_for("index"))

        return render_template("upload_recipe.html",islogin=islogin)
    except Exception as e:
        print("error: ",e)
        return render_template("404.html")

@app.route("/change_recipe/<recipieid>", methods=["GET", "POST"])
def change_recipe(recipieid):
    try:
        print("from update recipe...")
        # validating user before adding recipe
        login_data = login_authorize(request, db)
        islogin = True if login_data["success"] else False
        print(login_data)
        # if login is unsuccessfull redirecting to login page again
        if not login_data["success"]:
            return redirect(url_for("login"))

        response = single_recipe_controller({"_id": ObjectId(recipieid)}, db)[0]
        if request.method == "POST":
            imagelink = request.form.get("imageurl")
            # when image filename is available saving the uploaded image file to /static/uploaded_images/ directory
            query = {"_id": ObjectId(recipieid)}
            update = dict(
                recipeName=request.form.get("recepiename", None),
                imageUrl=request.form.get("imageurl"),
                ingredients=request.form.get("ingredients", None),
                instructions=request.form.get("instructions", None),
                meal_type=request.form.getlist('options'),
                userId=login_data["_id"],
                createdOn=datetime.now(),
            )

            db["recipes"].update_one(query, {"$set": update})
            print("Recipe updated successfully!")
            return redirect(url_for("index"))

        return render_template("change_recipe.html", result=response, hasresult=True,recipieid=recipieid,islogin=islogin)
    except Exception as e:
        print("error: ",e)
        return render_template("404.html")


@app.route("/remove_recipe/<recipieid>", methods=["GET"])
def remove_recipe(recipieid):
    try:
        print("from delete recipe...")
        # validating user before adding recipe
        login_data = login_authorize(request, db)
        print(login_data)
        # if login is unsuccessfull redirecting to login page again
        if not login_data["success"]:
            return redirect(url_for("login"))
        db["recipes"].delete_one({"_id": ObjectId(recipieid)})

        print("Recipe deleted successfully!")
        return redirect(url_for("my_recepie"))
    except Exception as e:
        print("error: ",e)
        return render_template("404.html")


@app.route('/all_recipes', methods=["GET", "POST"])
def all_recipes():
    login_data = login_authorize(request, db)
    islogin = True if login_data["success"] else False
    response = all_recipe_controller({}, db_conn=db)

    return render_template('all_recipes.html',islogin=islogin, result=response)


@app.route('/view_recipe/<recipieid>', methods=["GET", "POST"])
def view_recipe(recipieid):
    try:
        login_data = login_authorize(request, db)
        # if login is unsuccessfull redirecting to login page again
        islogin = True if login_data["success"] else False
        # this API only gives one output
        payload_filter = {"_id": ObjectId(recipieid)}
        response = single_recipe_controller(payload_filter, db_conn=db)[0]
        if islogin:
            islogin = True if response["userid"] == login_data["_id"] else False
        # print("response :", response)
        response["username"] = get_user_name(response["userid"], db)
        response['ingredients'] = response['ingredients'].split(',')

        return render_template(
            "view_recipe.html", result=response, hasresult=True, islogin=islogin
        )
    except Exception as e:
        print("Error-------------", e)
        return render_template("404.html")


@app.route("/my_recepie")
def my_recepie():
    login_data = login_authorize(request, db)
    islogin = True if login_data["success"] else False
    if not login_data["success"]:
        return redirect(url_for("login"))

    payload_filter = {"userId": login_data["_id"]}
    response = all_recipe_controller(payload_filter, db_conn=db)
    print("response---", response)
    return render_template("my_recipe.html", name=login_data["name"], result=response, islogin=islogin)



@app.route("/search", methods=["POST"])
def search_api():
    login_data = login_authorize(request, db)
    islogin = True if login_data["success"] else False

    if request.method == "POST":
        search_string = request.form.get("searchstring", "")

        if len(search_string) == 0:
            is_search = False
            return render_template("search.html", is_search=is_search)
        collection_filter = {
            "$or": [
                {"recipeName": {"$regex": search_string, "$options": "i"}},
                {"ingredients": {"$regex": search_string, "$options": "i"}},
                {"instructions": {"$regex": search_string, "$options": "i"}},
            ]
        }
        print("collection_filter", collection_filter)
        response = db["recipes"].find(collection_filter)
        result = map_response(response)
        is_search = True if len(result) > 0 else False
        return render_template("search.html", result=result, is_search=is_search,islogin=islogin)



if __name__ == "__main__":
    app.run(debug=True,threaded=True, host='0.0.0.0', port=5000)
