from flask import Flask, Response, redirect, render_template, url_for, request, session, abort, flash, json, jsonify
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import Email, Length, InputRequired
import pymongo
from pymongo import MongoClient
import datetime

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = 'secret'
client = MongoClient('localhost', 19823)
db = client.m_data

class MovieForm(FlaskForm):
    movie_tags = StringField('movie_tags', validators=[InputRequired(), Length(min=1, max=30)])
    movie_id = IntegerField('movie_id', validators=[InputRequired()])

class StatusForm(FlaskForm):
    movie_id = IntegerField('movie_id', validators=[InputRequired()])

@app.route('/home')
def home():
    return Response('<h1>Welcome</h1>')

# @app.route('/', methods = ['GET', 'POST'])
# def start():
#     form = MovieForm()
#     if request.method == 'POST':
#         if form.validate_on_submit():
#             movie_id = form.movie_id.data
#             movie_tags = form.movie_tags.data
#             db.mname.insert_one({'movie_id':movie_id, 'movie_tags':movie_tags, 'start_time':datetime.datetime.now()})
#             return redirect(url_for('stop'))
#     return render_template('movie.html', form = form)

# @app.route('/stopped', methods = ['GET', 'POST'])
# def stop():
#     form = StatusForm()
#     if request.method == 'POST':
#         if form.validate_on_submit():
#             data = db.mname.find()
#             movie_id = form.movie_id.data
#             db.mname.update_one({'movie_id': movie_id}, {'$set':{'end_time':datetime.datetime.now()}})
#             return render_template('stop.html', result = data)
#     return render_template('view_result.html', form = form)

# @app.route('/relaunch')
# def re_launch():
#     return redirect(url_for('start'))

# /movieID?process=stop/relauch
@app.route('/process', methods = ['GET', 'POST'])
def process():
    try:
        if request.method == 'POST':
            req_data = request.get_json()
            db.mname.insert({'movie_id':req_data['m_id'],'movie_tags':req_data['tags'],'status':req_data['status']})
            return '''
            Movie Id: {}
            Movie Tags: {}
            Status:{}
            '''.format(req_data['m_id'],req_data['tags'],req_data['status'])
            
        if request.method == 'GET':
            m_details = []
            m_id = request.args.get('m_id')
            m_status = request.args.get('m_status')
            
            if m_status == 'stop': 
                db.mname.update({'movie_id': int(m_id)},{'$set':{'status':m_status}})
                data = db.mname.find({'movie_id': int(m_id)})
                for each in data:
                    m_details.append(each['status'])
                return jsonify(m_details)
            
            elif m_status == 'relaunch':
                db.mname.update({'movie_id': int(m_id)},{'$set':{'status':m_status}})
                data = db.mname.find({'movie_id': int(m_id)})
                for each in data:
                    m_details.append(each['status'])
                return jsonify(m_details)
                return 'relaunch'
    
    except Exception as e:
        print (e)
# def add_hastags('/add', methods = ['GET', 'POST'])
#     # initial new movie hastag collection





if __name__ == "__main__":
    app.run(debug = True)
