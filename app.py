from flask import Flask, render_template, request, redirect, url_for, flash
import sys
import requests
import os
from flask_sqlalchemy import SQLAlchemy


api_key = 'b43b2195f05e3c015e38cee27fef3cd6'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)
app.config.update(SECRET_KEY=os.urandom(24))


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return self.name


db.create_all()


@app.route('/add', methods=['POST'])
def add_city():
    if request.method == 'POST':
        city_name = request.form['city_name']
        api_url = requests.get('http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}'.format(city_name, api_key))
        print(city_name)
        if api_url.status_code == 404:
            flash("The city doesn't exist!")
        else:
            if City.query.filter_by(name=city_name).first():
                flash('The city has already been added to the list!')
            elif city_name == '':
                flash("Field can't be empty")
            else:
                new_city = City(name=city_name)
                db.session.add(new_city)
                db.session.commit()
        return redirect(url_for('index'))


@app.route('/')
def index():
    cities_db_query = City.query.all()
    cities_db = []
    for city in cities_db_query:
        api_url = requests.get('http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}'.format(city, api_key))
        current_temp_r = api_url.json()['main']['temp']
        city_name_r = api_url.json()['name']
        weather_state = api_url.json()['weather'][0]['main']
        city_stats = [city.id, city_name_r, current_temp_r, weather_state]
        cities_db.append(city_stats)
    return render_template('index.html', cities=cities_db)


@app.route('/delete', methods=['POST'])
def delete():
    city = City.query.filter_by(id=request.form['id']).first()
    db.session.delete(city)
    db.session.commit()
    return redirect('/')


@app.route('/profile')
def profile():
    return 'This is profile page'


@app.route('/login')
def log_in():
    return 'This is login page'


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run(host='0.0.0.0', debug=True)
