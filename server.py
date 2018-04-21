from flask import Flask, render_template, url_for, request, session, redirect, send_from_directory
from flask_pymongo import PyMongo
import json
import os
from werkzeug.utils import secure_filename
import bcrypt

from bson.json_util import dumps

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads')
THUMBS_FOLDER = os.path.join(APP_ROOT, 'static/thumbs')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'PNG', 'JPEG', 'JPG', 'BMP'}

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'hotels'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/hotels'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['THUMBS_FOLDER'] = THUMBS_FOLDER
mongo = PyMongo(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/mobile/allhotels', methods=['POST', 'GET'])
def mobileallusers():
    hotels = mongo.db.hotels
    all_hotels = hotels.find({}, {'_id': False}).sort("name", 1)
    return dumps(all_hotels)

@app.route('/mobile/login', methods=['POST', 'GET'])
def mobilelogin():
    print("Username : " + str(request.form['username']) + "     PAssword : " + str(request.form['password']))
    print(request.form['password'])
    users = mongo.db.users
    login_user = users.find_one({'email' : request.form['username']})
    if login_user is None:
       print("Returning invalid email")
       return json.dumps({'login' : 'successful'})
    print(login_user)
    login_username = login_user['name']
    login_fullname = login_user['name']
    login_mail = login_user['email']
    if login_user:
       print("Inside login_user")
       if str(request.form['password']) == str(login_user['password']):
            print("Inside bcrypt")
            return json.dumps({'login':'success', 'email':login_mail, 'username':login_username, 'fullname' : login_fullname})
    return json.dumps({'login': 'unsuccessful'})

@app.route('/mobile/hotel_details/<hotel_id>')
def mobilehotel_details(hotel_id):
    hotels = mongo.db.hotels
    find_hotel = hotels.find_one({'identifier' : str(hotel_id)})
    hotel_name = find_hotel['name']
    hotel_image = find_hotel['image']
    hotel_address = find_hotel['address']
    hotel_cost = find_hotel['cost']
    hotel_rating = find_hotel['rating']
    hotel_email = find_hotel['email']
    hotel_phonenumber = find_hotel['number']
    
    return json.dumps({'Name': hotel_name, 'Email' : hotel_email, 'Phone' : str(hotel_phonenumber), 'identifier' : hotel_id, 'Adress' : hotel_address, 'Cost' : hotel_cost, 'Rating' : hotel_rating})
    
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        user_fname = request.form['name']
        user_email = request.form['email']
        user_type = 'user'
        existing_user = users.find_one({'name': request.form['username'], 'email': user_email})
        if existing_user is None:
            users.insert(
                {'fullname': user_fname, 'email': user_email, 'name': request.form['username'], 'password': request.form['pass'],
                 'user_type': user_type})
            return redirect(url_for('register'))

        return 'A user with that Email id/username already exists'

    return render_template('register.html')

@app.route('/submit', methods=['POST', 'GET'])
def submit():
    hotels = mongo.db.hotels
    count = hotels.find().count()
    if request.method == 'POST':
        file = request.files['hotel_image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            fname = filename
            hotel_name = request.form['hotel_name']
            hotel_address = request.form['hotel_address']
            hotel_email = request.form['hotel_email']
            hotel_cost = request.form['hotel_cost']
            hotel_rating = request.form['hotel_rating']
            hotel_phonenumber = request.form['hotel_phone']
            identifier = str(count+1)
            download_link = '/downloads/%s' % fname
            hotels.insert({'identifier': identifier,'cost' : hotel_cost, 'rating': hotel_rating, 'name' : str(hotel_name), 'image' : str(download_link), 'address': hotel_address, 'email':hotel_email, 'number':hotel_phonenumber})
    
    return render_template('submit2.html')
    
@app.route('/downloads/<filename>')
def downloads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True, host='0.0.0.0', port=5000, passthrough_errors=False, threaded=True)
