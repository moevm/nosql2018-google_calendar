from flask import Flask, request, jsonify, render_template, make_response, send_file, url_for, flash, redirect, \
    send_from_directory
from flask_pymongo import PyMongo
from parse_to_json import createjson
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import json
import dateutil.parser
import pandas as pd
from math import pi

from bokeh.plotting import figure
from bokeh.transform import cumsum
from bokeh.embed import components

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = set(['ics', 'json', 'bson'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_json("config.json")
mongo = PyMongo(app)

current_user = "Choose the user"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # file - это то что показывала тебе
            # filename - просто имя файла.
            username = createjson(file)
            parse_to_mongo_user(username)
            global current_user
            current_user = username
#            screen_5(True)
#            screen_4(True)

    return render_template('main.html')


@app.route('/tmp/<filename>')
def uploaded_file(filename):
    return send_file(app.config['UPLOAD_FOLDER'],
                     filename)


@app.route('/statistics')
def statistics():
    return render_template('statistics.html')


@app.route('/lovelyFriend')
def lovelyFriend():
    return render_template('lovelyFriend.html')


@app.route('/organizedEvents', methods=["GET", "POST"])
def organizedEvents():
    if request.method == "POST":
        options = request.form.get('options')
        if options=="option1":
            flag=True
        else:
            flag=False
        print(flag)
        plot = diagram(screen_5(flag))
        script, div = components(plot)
        return render_template('/organizedEvents.html', flag=flag, script=script, div=div)
    return render_template('/organizedEvents.html', flag=None)


@app.route('/employment')
def employment():
    return render_template('/employment.html')


@app.route('/synchronization')
def synchronization():
    return render_template('/synchronization.html')


def screen_4(is_year):
    cursor = mongo.db.users.find({"email": current_user})
    cur_date = datetime.now()
    if is_year:
        cur_date = cur_date - timedelta(days=365)  # если год
    else:
        cur_date = cur_date - timedelta(days=30)  # если месяц

    all_visitors = []
    all_organizers = []  # все организаторы
    result_organizers = {}  # dict - результат
    result_visitors = {}  # dict - результат

    for id in cursor:
        user_id = id.get('_id')
        # ты организатор считаем приглашенных
        cursor1 = mongo.db.events.find({"user_id": user_id, "organizer": current_user,  "start": {'$gte': cur_date}})

        for vis in cursor1:
            all_visitors += vis.get('visitors')

        for vis in all_visitors:
            if vis in result_visitors.keys():
                result_visitors[vis] += 1
            else:
                result_visitors[vis] = 1

        print("Результат количества приглашенных на мероприятия тобой", result_visitors)

        # считаем все мероприятия и ищем кто их организовывал
        cursor1 = mongo.db.events.find({"user_id": user_id, "start": {'$gte': cur_date}})
        for org in cursor1:
            if org.get('visitors'):  # если в таблице есть приглашенные то запоминаем организатора
                all_organizers.append(org.get('organizer'))

        # ищем список всех организаторов без повторений
        # записываем в словарь ключ - эмайл, значение - количество организованных мероприятий
        for org in mongo.db.events.find({"user_id": user_id, "start": {'$gte': cur_date}}).distinct("organizer"):
            result_organizers[org] = all_organizers.count(org)

        result_organizers = [(k, result_organizers[k]) for k in sorted(result_organizers, key=result_organizers.get, reverse=True)]

    print("Результаты подсчета количества организованных мероприятий", result_organizers)

    return result_organizers


def screen_5(is_year):
    cursor = mongo.db.users.find({"email": current_user})
    cur_date = datetime.now()
    if is_year:
        cur_date = cur_date - timedelta(days=365)
    else:
        cur_date = cur_date - timedelta(days=30)

    count = 0  # вернет мероприятия где ты организатор
    count2 = 0  # вернет все мероприятия
    for id in cursor:
        user_id = id.get('_id')
        count = mongo.db.events.find(
            {"user_id": user_id, "organizer": current_user, "start": {'$gte': cur_date}}).count()
        count2 = mongo.db.events.find({"user_id": user_id, "start": {'$gte': cur_date}}).count()

    print("Я организатор: ", count, "Всего мероприятий: ", count2)

    return [count, count2]


def screen_4(is_year):
    cursor = mongo.db.users.find({"email": current_user})
    cur_date = datetime.now()
    if is_year:
        cur_date = cur_date - timedelta(days=365)  # если год
    else:
        cur_date = cur_date - timedelta(days=30)  # если месяц

    all_visitors = []
    all_organizers = []  # все организаторы
    result_organizers = {}  # dict - результат
    result_visitors = {}  # dict - результат

    for id in cursor:
        user_id = id.get('_id')
        # ты организатор считаем приглашенных
        cursor1 = mongo.db.events.find({"user_id": user_id, "organizer": current_user,  "start": {'$gte': cur_date}})

        for vis in cursor1:
            all_visitors += vis.get('visitors')

        for vis in all_visitors:
            if vis in result_visitors.keys():
                result_visitors[vis] += 1
            else:
                result_visitors[vis] = 1

        print("Результат количества приглашенных на мероприятия тобой", result_visitors)

        # считаем все мероприятия и ищем кто их организовывал
        cursor1 = mongo.db.events.find({"user_id": user_id, "start": {'$gte': cur_date}})
        for org in cursor1:
            if org.get('visitors'):  # если в таблице есть приглашенные то запоминаем организатора
                all_organizers.append(org.get('organizer'))

        # ищем список всех организаторов без повторений
        # записываем в словарь ключ - эмайл, значение - количество организованных мероприятий
        for org in mongo.db.events.find({"user_id": user_id, "start": {'$gte': cur_date}}).distinct("organizer"):
            result_organizers[org] = all_organizers.count(org)

        result_organizers = [(k, result_organizers[k]) for k in sorted(result_organizers, key=result_organizers.get, reverse=True)]

    print("Результаты подсчета количества организованных мероприятий", result_organizers)

    return result_organizers


def parse_to_mongo_user(user):  # закидываем юзера в бд юзеров
    cursor = mongo.db.users.find({"email": user})
    if cursor.count() != 0:  # если данный user уже есть
        for id in cursor:
            user_id = id.get('_id')
            mongo.db.events.remove({"user_id": user_id})
        mongo.db.users.remove({"email": user})

    mongo.db.users.insert({"email": user})

    for id in mongo.db.users.find({"email": user}):
        user_id = id.get('_id')
        parse_to_mongo_events(user_id, user)  # вызываем функцию для закидывания мероприяти1


def parse_to_mongo_events(user_id, user):  # закидываем его мероприятия
    json_file = open('./data/' + user + '.json').read()
    json_file = json.loads(json_file)
    for event in json_file:
        if 'ORGANIZER' in event:
            dtstart = dateutil.parser.parse(event["DTSTART"]) + timedelta(
                hours=3)  # преобразуем в человеческий формат дату плюс 3 часа потому
            dtend = dateutil.parser.parse(event["DTEND"]) + timedelta(hours=3)
            mongo.db.events.insert({"user_id": user_id, "summary": event["SUMMARY"],
                                    "start": dtstart, "end": dtend, "location": event["LOCATION"],
                                    "organizer": event["ORGANIZER"], "visitors": event["VISITORS"]})


def diagram(a):
    x = {
        'Организованные мероприятия': a[0],
        'Гость мероприятий': a[1],
    }
    print(type(x))
    data = pd.Series(x).reset_index(name='value').rename(columns={'index':'country'})
    data['angle'] = data['value']/data['value'].sum() * 2*pi
    data['color'] = ['#feeaf5', '#ced2ff']

    p = figure(plot_height=350, title="Мероприятия", toolbar_location=None,
               tools="hover", tooltips="@country: @value", x_range=(-0.5, 1.0))

    p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend='country', source=data)

    p.axis.axis_label=None
    p.axis.visible=False
    p.grid.grid_line_color = None
    return p

if __name__ == '__main__':
    app.run(debug=True)
