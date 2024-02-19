from flask import Flask, Response, redirect, render_template, url_for, request, session, abort, flash, json, jsonify
from flask_mongoengine import MongoEngine, Document
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import Email, Length, InputRequired
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import urllib, json, requests
import db_data_process as dp
import uuid

#App Config
app = Flask(__name__)
Bootstrap(app)
app.config['MONGODB_SETTINGS'] = {
    'db': 'review',
    'host': 'mongodb://localhost:19823/review'
}
db = MongoEngine(app)
app.config['SECRET_KEY'] = 'secret'

#Loginmanager Config
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#Class review user
class User(UserMixin, db.Document):
    meta = {'collection': 'review'}
    email = db.StringField(max_length = 30)
    password = db.StringField()

#User Loader
@login_manager.user_loader
def load_user(user_id):
    try:
        return User.objects(pk = user_id).first()
    except Exception as e:
        print('Error in load user', e)

#Register Form
class RegForm(FlaskForm):
    email = StringField('email',  validators = [InputRequired(), Email(message = 'Invalid email'), Length(max = 30)])
    password = PasswordField('password', validators = [InputRequired(), Length(min = 8, max = 20)])

#Login-form
class LoginForm(FlaskForm):
    email = StringField('email',  validators = [InputRequired(), Email(message = 'Invalid email'), Length(max = 30)])
    password = PasswordField('password', validators = [InputRequired(), Length(min = 8, max = 20)])

#Movie-Add-form
class MovieForm(FlaskForm):
    movie_name = StringField('movie name', validators=[InputRequired(), Length(min=1, max=30)])

class HashForm(FlaskForm):
    hash_tag = StringField('hash tag', validators=[InputRequired(), Length(min=1, max=25)])

#Home
@app.route('/')
def home():
    try:
        return Response('<h1>Real Movie Review</h1>')
    except Exception as e:
        print('Error in home page', e)

#Admin
@app.route('/admin')
@login_required
def admin_page():
    try:
        return render_template('movies.html')
    except Exception as e:
        print('Error in admin page', e)

#URL Redirection
@app.route('/<path>')
def redirection(path):
    try:
        if path == 'login':
            return redirect(url_for('login'))
        elif path == 'register':
            return redirect(url_for('register'))
        elif path == 'movies':
            return redirect(url_for('movie_page'))
        elif path == 'logout':
            return redirect(url_for('logout'))
    except Exception as e:
        print('Error in redirection', e)

#Register User
@app.route('/admin/register', methods = ['GET', 'POST'])
def register():
    try:
        form = RegForm()
        if request.method == 'POST':
            if form.validate():
                if User.objects(email=form.email.data).first() is None:
                    gen_hash_pass = generate_password_hash(form.password.data, method = 'sha256')
                    h_key = User(form.email.data,gen_hash_pass,str(uuid.uuid4())).save()
                    login_user(h_key)
                    return redirect(url_for('movie_page'))
        return render_template('register.html', form = form)
    except Exception as e:
        print('Error in register page', e)

#Login User
@app.route('/admin/login', methods = ['GET', 'POST'])
def login():
    try:
        if current_user.is_authenticated == True:
            return redirect(url_for('admin_page'))
        form = RegForm()
        if request.method == 'POST':
            if form.validate():
                user_check = User.objects(email = form.email.data).first()
                if user_check:
                    if check_password_hash(user_check['password'], form.password.data):
                        login_user(user_check)
                        return redirect(url_for('admin_page'))
        return render_template('login.html', form = form)
    except Exception as e:
        print('Error in login page', e)

#Movie
@app.route('/admin/movies', methods = ['GET', 'POST'])
@login_required
def movie_page():
    try:
        page = request.args.get("page") or 1
        upcoming, t_pages = dp.movie_data(page)
        return render_template('view_movie.html', data = upcoming, pages = t_pages)
    except Exception as e:
        print('Error in movies page', e)

#Movie/process
@app.route('/admin/movies/<movie_id>/process', methods = ['GET', 'POST'])
@login_required
def process(movie_id,req):
    try:
        if request.method == 'POST':
            p_data = dp.movie_tags_insert(int(movie_id), req, current_user.u_id)
            print current_user.u_id
            if p_data != None:
                return jsonify(p_data)
            else:
                return 'No Data Found'            

        data = dp.movie_tags_update(int(movie_id), current_user.u_id, m_status = request.args.get('m_status'))
        if data != None:
            return jsonify(data)
        else:
            return 'No Data Found'
    except Exception as e:
        print ('Error in process', e)

@app.route('/admin/movies/<movie_id>', methods = ['GET', 'POST'])
@login_required
def movie_view(movie_id):
    try:
        form = HashForm()     
        view_logs = dp.movie_log(movie_id, current_user.u_id)
        if form.validate_on_submit():
            req = {}
            hash_tag =form.hash_tag.data
            req.update({'movie_id':movie_id,'status':'start','tags':[each.strip() for each in hash_tag.split(',')]})
            p_data = dp.movie_tags_insert(int(movie_id), req, current_user.u_id)
            if p_data != None:
                return render_template('view_specific_movie_1.html', data = p_data, form = form)
            else:
                return 'No Data Found' 
        else:
            data = dp.movie_tags_update(int(movie_id), current_user.u_id, m_status = request.args.get("m_status"))            
            view_logs = dp.movie_log(movie_id, current_user.u_id)
            if view_logs != None: 
                return render_template('view_specific_movie_1.html', data = view_logs,form = form)
            else:
                return 'No Data Found'
        return render_template('view_specific_movie_1.html', data = view_logs, form = form)
    except Exception as e:
        print ('Error in movie path', e)

#Add Movie
@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add_movie():
    try:
        form = MovieForm()
        if form.validate_on_submit():
            return 'ok'
        return render_template('add_form.html', form = form)
    except Exception as e:
        print ('Error in add movie', e)

#Log-Out
@app.route('/admin/logout', methods = ['GET'])
@login_required
def logout():
    try:
        logout_user()
        return redirect(url_for('home'))
    except Exception as e:
        print ('Error in logout', e)

#Unauthorized User Handling
@login_manager.unauthorized_handler
def unauthorized():
    try:
        return redirect(url_for('login'))
    except Exception as e:
        print ('Error in unauthorized handling', e)

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 4000, debug = True)