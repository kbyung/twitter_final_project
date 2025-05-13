import os


from flask import Flask, jsonify, send_from_directory, request, render_template, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, create_engine
from werkzeug.utils import secure_filename


app = Flask(__name__)
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
    if username == "haxor" and password  == '1223':
        return True 
    else:
        return False

@app.route("/")
def root():
    print_debug_info()
    engine = create_engine("postgresql://hello_flask:hello_flask@db:5432/hello_flask_dev")
    messages =  []
    with engine.connect() as connection:
        result = connection.execute(text("SELECT text FROM tweets LIMIT 20"))
        for row in result:
            messages.append(row.text) 

    # check if logged in correctly

    username = request.cookies.get("username")
    password = request.cookies.get("password")
    good_credentials = are_credentials_good(username, password)
    print("good credentials", good_credentials)

    return render_template('root.html', logged_in=good_credentials, messages=messages) 


@app.route("/login", methods=['GET', 'POST'])
def login():
    print_debug_info()
    username = request.form.get("username")
    password = request.form.get("password")
    print("username=", username)
    print("password=", password)


    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)

    # first time we've visited, no form submission

    if username is None:
        return render_template('login.html', bad_credentials=False)

    # they've submitted a form; we're on the POST method
    else:
    
        if not good_credentials:
            return render_template('login.html', bad_credentials=True)
        else:
            # if we're here, we have successfully logged in 
            # create a cookie that contains the username/password info
#            return 'login successful'
             template = render_template('login.html', bad_credentials=False, logged_in=True)
             response = make_response(template)
             response.set_cookie('username', username)
             response.set_cookie('password', password)
             return response 


@app.route("/logout")
def logout():
    print_debug_info()
    return "logout page"

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
