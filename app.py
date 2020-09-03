from flask import Flask, json, Response, request, render_template, url_for, redirect, flash
# from flask_login import login_manager
from werkzeug.utils import secure_filename
from werkzeug.security import  generate_password_hash, check_password_hash
from os import path, getcwd
import time
from database import Database
from face_rec import Face

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ASEW123#$%chsehf09'
app.config['file_allowed'] = ['image/png', 'image/jpeg', 'image/jpg']
app.config['storage'] = path.join(getcwd(),'storage')
app.db = Database()
app.face = Face(app)


def success_handle(output, status=200, mimetype='application/json'):
    return Response(output, status=status, mimetype=mimetype)


def error_handle(error_message, status=500, mimetype='application/json'):
    return Response(json.dumps({"error": {"message": error_message}}), status=status, mimetype=mimetype)


def get_user_by_id(user_id):
    user = {}
    results = app.db.select('SELECT users.id, users.name, users.second_name ,users.national_id ,users.created, faces.id, faces.user_id, faces.national_id ,faces.filename, faces.created FROM users LEFT JOIN faces ON faces.user_id = users.id WHERE  users.id = ?', [user_id])

    index = 0
    for row in results:
        # print(row)
        face = {
            "id": row[5],
            "user_id": row[6],
            "filename": row[7],
            "created": row[8],
        }
        if index == 0:
            user ={
                "id": row[0],
                "name": row[1],
                "second_name": row[2],
                "national":row[3],
                "created":row[4],
                "faces": [],
            }
        if  row[5]:
            user["faces"].append(face)
        index = index + 1
    if "id" in  user:
        return user
    return None


def delete_user_by_id(user_id):
    app.db.delete('DELETE FROM users WHERE  users.id = ?',[user_id])
    app.db.delete('DELETE FROM faces WHERE faces.id = ?',[user_id])


# route to home page
@app.route('/', methods=["GET"])
def page_home():
    return render_template('home.html')

# route to person list
@app.route('/person', methods=["GET", "POST"])
def personlist():
    if request.method == 'GET':
        results = app.db.select("SELECT * FROM users").fetchall()
    return render_template('personlist.html', results=results)

# route to train form
@app.route('/reg', methods=["GET"])
def reg():
    return render_template('reg.html')


@app.route('/api', methods=['GET'])
def homepage():
    print("welcome home!!!")
    output = json.dumps({"api": "1.0"})
    return Response(output, mimetype='application/json')

# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # output1 = json.dumps({"success": True})
    output2 = json.dumps({"login": True})
    if request.method == 'POST':
        cert_num = request.form.get('cert_id')
        password = request.form.get('password')

        usernamedata = app.db.select('SELECT reg_user.username FROM reg_user  WHERE  reg_user.username =?',[cert_num]).fetchone()
        passworddata = app.db.select('SELECT reg_user.password FROM reg_user  WHERE  reg_user.username =?',[cert_num]).fetchone()

        if usernamedata is None:
            return error_handle("user does not exist")
        else:
            for pass_word in passworddata:
                if check_password_hash(pass_word, password):
                    print(output2)
                    return redirect(url_for('reg'))
                else:
                    return error_handle("password do not match")
    return render_template('log.html')

# register of a detective
@app.route('/register', methods=['GET', 'POST'])
def register_detective():

    output1 = json.dumps({"success": True})
    if request.method == "POST":
        name = request.form.get('name')
        cert_num = request.form.get('cert_num')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        hashpassword = generate_password_hash(password)

        if password == confirm:
            app.db.insert('INSERT INTO reg_user(name,username,password) values (?,?,?)', [name,cert_num, hashpassword])
            return success_handle(output1)
        else:
            return error_handle("password do not match")
    return render_template('reg_det.html')

@app.route('/api/train', methods=['POST'])
def train():
    output = json.dumps({"success": True})
    if 'file'not in request.files:
        print("face image is required")
    else:
        print("file request", request.files)
        file = request.files['file']
        if file.mimetype not in app.config['file_allowed']:
            print("file extension not allowed")
            return error_handle("we only upload file with *.png, *.jpg")
        else:
            # get name
            name = request.form['name']
            second_name = request.form['second_name']
            national_id = request.form['nat_id']
            parents = request.form["parent"]
            DOB = request.form["Date_of_birth"]
            place_birth = request.form["place_birth"]
            location = request.form["location"]
            phone = request.form["phone"]
            gender = request.form['gender']
            print("info of file", name)
            print("file is allowed and saved in ", app.config['storage'])
            filename = secure_filename(file.filename)
            trained_storage = path.join(app.config['storage'], 'trained')
            file.save(path.join(trained_storage,filename))
            # save to database
            created = int(time.time())
            user_id = app.db.insert('INSERT INTO users(name,second_name, national_ID,parents,DOB,created,location,phone,gender,place_birth) values (?,?,?,?,?,?,?,?,?,?)', [name,second_name, national_id,parents,DOB ,created,location,phone,gender,place_birth])

            if user_id:
                print("User {} is saved with ID {}".format( name, user_id))
                face_id = app.db.insert('INSERT INTO faces(user_id, national_id,filename, created) values (?,?,?,?) ', [user_id, national_id ,filename, created])
                if face_id:
                    print("face saved")
                    face_data = {"id":face_id, "filename":filename, "created":created}
                    return_output = json.dumps({"id":user_id, "name":name, "face":[face_data]})
                    return success_handle(return_output)
                else:
                    print("an error occurred while saving face image")
                    return error_handle("an error occurred while saving face image")
            else:
                print("something happened")
                return error_handle("An error occurred inserting new user")
        print("request contains image")

    return success_handle(output)

# user profile
@app.route('/api/users/<int:user_id>', methods=['GET', 'DELETE'])
def user_profile(user_id):
    if request.method == "GET":

        user = get_user_by_id(user_id)
        if user:
            return success_handle(json.dumps(user), 200)
        else:
            return error_handle("User not found:", 404)
    if request.method == "DELETE":
        delete_user_by_id(user_id)
        return success_handle(json.dumps({"deleted": True}))


# face recognition api
@app.route('/api/recognize', methods=['POST'])
def recognize():
    if 'file' not in request.files:
        return error_handle("image is required")
    else:
        file = request.files['file']
        # file extension
        if file.mimetype not in app.config['file_allowed']:
            return error_handle("file extension not allow")
        else:
            filename = secure_filename(file.filename)
            unknown_storage = path.join(app.config['storage'], 'unknown')
            filepath = path.join(unknown_storage, filename)
            file.save(filepath)

            user_id = app.face.recognize(filename)
            if user_id:
                user = get_user_by_id(user_id)
                message = {"message":"we found {} matched with your face image".format(user["second_name"]), "user":user}
                return json.dumps(message)
            else:
                return error_handle("No match found ")
    return success_handle(json.dumps({"found": filename}))


app.run()