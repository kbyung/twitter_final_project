import os


from flask import Flask, jsonify, send_from_directory, request, render_template, make_response, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, create_engine
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import time


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, email):
        self.email = email

def print_debug_info():
    username = request.args.get('username')
    print('request.args.get("username")=', username)
    password = request.args.get('password')
    print('request.args.get("password")=', password)
    print('request.form.get("username")=', request.form.get("username"))
    print('request.form.get("password")=', request.form.get("password"))

    #cookies
    print('request.cookies.get("username")=', request.cookies.get("username"))
    print('request.cookies.get("password")=', request.cookies.get("password"))



def are_credentials_good(username, password):

    engine = create_engine("postgresql://hello_flask:hello_flask@db:5432/hello_flask_dev")
    with engine.connect() as connection:
        query = text("SELECT id_users FROM users WHERE screen_name = :username AND password = :password")
        result = connection.execute(query, {"username": username, "password":  password})
        signed_in= result.fetchone()

    if signed_in:
        return True
    else:
        return False



@app.route("/")
def root():
    print_debug_info()
    engine = create_engine("postgresql://hello_flask:hello_flask@db:5432/hello_flask_dev")
    messages =  []

    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * 20


    with engine.connect() as connection:
        query = text("""
            SELECT
                t.id_tweets, 
                t.created_at,
                t.text,
                u.screen_name
            FROM 
                tweets t
            JOIN
                users u ON t.id_users = u.id_users
            ORDER BY
                t.created_at DESC, t.id_tweets DESC 
            LIMIT 20
            OFFSET :offset
        """)
        result = connection.execute(query, {"offset": offset})
        messages = [dict(row._mapping) for row in result]

    # check if more pages exist
    has_next = len(messages) == 20
    has_prev = page > 1
    
    # check if logged in correctly

    username = request.cookies.get("username")
    password = request.cookies.get("password")
    good_credentials = are_credentials_good(username, password)
    print("good credentials", good_credentials)

    return render_template(
            'root.html',
            logged_in=good_credentials,
            messages=messages, 
            page=page,
            has_prev=has_prev,
            has_next=has_next
            ) 


@app.route("/login", methods=['GET', 'POST'])
def login():
    print_debug_info()
    username = request.form.get("username")
    password = request.form.get("password")
    print("username=", username)
    print("password=", password)



    # first time we've visited, no form submission

    if username is None:
        return render_template('login.html', bad_credentials=False)

    # they've submitted a form; we're on the POST method
    else:
        good_credentials = are_credentials_good(username, password)
        print('good_credentials=', good_credentials)
    
        if not good_credentials:
            return render_template('login.html', bad_credentials=True)
        else:
            # if we're here, we have successfully logged in 
            # create a cookie that contains the username/password info
#            return 'login successful'
             response = make_response(redirect(url_for('root')))
             response.set_cookie('username', username)
             response.set_cookie('password', password)
             return response 


@app.route("/logout")
def logout():
    response = make_response(redirect(url_for('root'))) 
    # remove the cookies set at login 
    response.delete_cookie('username')
    response.delete_cookie('password')
    print_debug_info()
    return response 

@app.route("/create_account", methods=['GET', 'POST'])
def create_account():
    print_debug_info()

    if request.method == "POST":

        screen_name= request.form.get("screen_name", "").strip()
        name = request.form.get("name", "").strip()
        password = request.form.get("password", "")
        retype_password = request.form.get("retype_password", "")

        print("screen_name=", screen_name)
        print("name=", name)
        print("password=", password)
        print("retype_password=", retype_password)

        # check if all fields are filled
        if not screen_name or not name or not password or not retype_password:
            return render_template(
                    "create_account.html",
                    screen_name=screen_name,
                    name=name,
                    missing_fields=True
            )

        # check for mismatch
        if password != retype_password:
            return render_template(
                    "create_account.html", 
                    screen_name=screen_name,
                    name=name,
                    password_mismatch=True
            )

        # check if username already exits in database
        engine = create_engine("postgresql://hello_flask:hello_flask@db:5432/hello_flask_dev")
        with engine.connect() as connection:
            query = text("SELECT id_users FROM users WHERE screen_name = :screen_name")
            result = connection.execute(query, {"screen_name": screen_name})
            existing_user = result.fetchone()

        if existing_user:
            return render_template(
                    "create_account.html",
                    screen_name=screen_name,
                    name=name,
                    username_exists=True
            )
        # create new user


        user_id = int(time.time() * 1000)

        with engine.connect() as connection:
            query = text("""
                INSERT INTO users (id_users, screen_name, name, password)
                VALUES (:id_users, :screen_name, :name, :password)
            """)
            connection.execute(query, {
                "id_users": user_id,
                "screen_name": screen_name,
                "name": name,
                "password": password 
            })
            connection.commit()

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))


   # GET 
    return render_template('create_account.html') 

@app.route("/create_message", methods=["GET", "POST"])
def create_message():
    # check if we're logged in

    username = request.cookies.get("username")
    password = request.cookies.get("password")
    good_credentials = are_credentials_good(username, password)
    if not good_credentials:
        return redirect(url_for("login"))


    engine = create_engine("postgresql://hello_flask:hello_flask@db:5432/hello_flask_dev")
    if request.method == "POST":
        body = request.form.get("text", "").strip()
        if body:
            with engine.connect() as conn:
                # 2) look up the current user's id
                result = conn.execute(
                    text("SELECT id_users FROM users WHERE screen_name = :u AND password = :p"),
                    {"u": username, "p": password}
                ).mappings()
                row = result.fetchone()
                user_id = row["id_users"]

                # 3) generate a new tweet ID (simple max+1 strategy)
                nxt = conn.execute(text(
                    "SELECT COALESCE(MAX(id_tweets), 0) + 1 AS next_id FROM tweets"
                )).mappings()
                nxt_row = nxt.fetchone()
                next_id = nxt_row["next_id"]

                # 4) insert with timestamp
                conn.execute(text("""
                    INSERT INTO tweets (id_tweets, id_users, created_at, text)
                    VALUES (:id, :uid, NOW(), :txt)
                """), {
                    "id":   next_id,
                    "uid":  user_id,
                    "txt":  body
                })
                conn.commit()
            # 5) send them back to home so they see their new message
        return redirect(url_for("root"))

    return render_template("create_message.html", logged_in=good_credentials ) 

@app.route("/search")
def search():
    return "search!"


@app.route("/static/<path:filename>")
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)


@app.route("/media/<path:filename>")
def mediafiles(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["MEDIA_FOLDER"], filename))
    return """
    <!doctype html>
    <title>upload new File</title>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file><input type=submit value=Upload>
    </form>
    """
