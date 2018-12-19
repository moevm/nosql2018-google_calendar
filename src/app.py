from flask import Flask, request, jsonify, render_template, make_response, send_file, url_for, flash, redirect, \
    send_from_directory
from flask_pymongo import PyMongo
from .parse_to_json import createjson
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import json
import dateutil.parser
import pandas as pd
import os
from math import pi
from flask_wtf import FlaskForm
from wtforms import FileField, SelectField, SubmitField, RadioField
from wtforms.fields.html5 import DateField
from bokeh.plotting import figure
from bokeh.transform import cumsum
from bokeh.embed import components


UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = set(['ics', 'json', 'bson'])

app = Flask(__name__)
app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_json("config.json")
mongo = PyMongo(app)

current_user = "Choose the user"
mass = ["kochnevaolga74@gmail.com", "mariyabuuu@gmail.com", "olchick0923@gmail.com"]


class ChooseUser(FlaskForm):
    dbFile = FileField('')
    users = SelectField('Выберите user', choices=[(i, i) for i in mass])
    submit1 = SubmitField('Импорт в базу данных')
    submit3 = SubmitField('Выбрать пользователя')
    submit2 = SubmitField('Экспорт бд Users')
    submit21 = SubmitField('Экспорт бд Events')


class Form1(FlaskForm):
    Data = RadioField('Временной промежуток', choices=[('year', 'Год'), ('month', 'Месяц')])
    submit = SubmitField('Получить статистику')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def main():
    form = ChooseUser()
    if form.validate_on_submit():
        if form.submit1.data:
            file = form.dbFile.data
            if file and allowed_file(file.filename):
                flash('Неверный формат файла, выберите файл *.ics')
                filename = secure_filename(file.filename)
                username = createjson(file)
                parse_to_mongo_user(username)
                return render_template('main.html', form=form)
            else:
                flash('Неверный формат файла, выберите файл *.ics')
                return render_template('main.html', form=form)
        # ОЛЯ, ЗДЕСЬ ЭКСПОРТ ПО ИДЕЕ
        if form.submit2.data:
            os.system('mongoexport --db Calendars --collection users --out ./src/export/Users.json')
            os.system('mongoexport --db Calendars --collection events --out ./src/export/Events.json')
            file_export = 'Users.json'
            #return render_template('main.html', form=form)
            return redirect(url_for('download',
                                    filename=file_export))
        if form.submit21.data:
            os.system('mongoexport --db Calendars --collection users --out ./src/export/Users.json')
            os.system('mongoexport --db Calendars --collection events --out ./src/export/Events.json')
            file_export = 'Events.json'
            #return render_template('main.html', form=form)
            return redirect(url_for('download',
                                    filename=file_export))
        #  А ЗДЕСЬ ВЫБОР ПОЛЬЗОВАТЕЛЯ
        if form.submit3.data:
            choice = form.users.data
            global current_user
            current_user = choice
    return render_template('main.html', form=form)


@app.route('/download/<filename>')
def download(filename):
    return send_from_directory('./export', filename)



@app.route('/tmp/<filename>')
def uploaded_file(filename):
    return send_file(app.config['UPLOAD_FOLDER'],
                     filename)


@app.route('/statistics')
def statistics():
    return render_template('statistics.html')


@app.route('/lovelyFriend', methods=["GET", "POST"])
def lovelyFriend():
    form = Form1()
    if form.validate_on_submit():
        ans = form.Data.data
        print(ans)
        if ans == "year":
            flag = True
        if ans == "month":
            flag = False
        guests = screen_4(flag)[1]
        org = screen_4(flag)[0]
        return render_template('lovelyFriend.html', form=form, organiser=org, guests=guests)
    return render_template('lovelyFriend.html', flag=None, form=form, organiser=None)


@app.route('/organizedEvents', methods=["GET", "POST"])
def organizedEvents():
    form = Form1()
    if form.validate_on_submit():
        ans = form.Data.data
        if ans == "year":
            flag = True
        if ans == "month":
            flag = False
        plot = diagram(screen_5(flag))
        script, div = components(plot)
        return render_template('/organizedEvents.html', form=form, script=script, div=div)
    return render_template('/organizedEvents.html', flag=None, form=form)


class ChooseDate(FlaskForm):
    submit3 = SubmitField('Получить результат')
    start_time = DateField('C  ', default=datetime.today())
    end_time = DateField('По  ', default=datetime.today())


@app.route('/employment', methods=["GET", "POST"])
def employment():
    form1 = ChooseDate()
    if form1.validate_on_submit():
        if form1.submit3.data:
            start = form1.start_time.data  # даты
            finish = form1.end_time.data
            if finish < start:
                form1.end_time.errors.append('Указан не верный промежуток времени')
                return render_template('/employment.html', form=form1)
            employment = screen_6(start, finish) # выводит список строк "дата и время1 - дата и время 2"
            return render_template('/employment.html', form=form1, empl=employment)
    return render_template('/employment.html', form=form1)


class ChooseFriend(FlaskForm):
    dbFile = FileField('')
    users = SelectField(choices=[(i, i) for i in mass])
    submit1 = SubmitField('Импорт календаря друга в бд')
    submit2 = SubmitField('Выбрать друга')
    submit3 = SubmitField('Получить результат')
    start_time = DateField('C  ', default=datetime.today())
    end_time = DateField('По  ', default=datetime.today())


friend=[] # массив для списка друзей

@app.route('/synchronization', methods=['GET', 'POST'])
def synchronization():
    form = ChooseFriend()
    if form.validate_on_submit():
        if form.submit1.data:
            file = form.dbFile.data
            if file and allowed_file(file.filename):
                flash('Неверный формат файла, выберите файл *.ics')
                filename = secure_filename(file.filename)
                username = createjson(file)
                parse_to_mongo_user(username)
                global current_user
                current_user = username
                return render_template('synchronization.html', form=form, friend=friend)
            else:
                flash('Неверный формат файла, выберите файл *.ics')
                return render_template('synchronization.html', form=form, friend=friend)
        if form.submit2.data:
            friend.append(form.users.data)
            choice = form.users.data
            print(choice)
        if form.submit3.data:
            start = form.start_time.data  # даты
            finish = form.end_time.data
            if finish < start:
                form.end_time.errors.append('Указан не верный промежуток времени')
                return render_template('synchronization.html', form=form, friend=friend)
            meetting = meetings(friend, start, finish) # вывести места пересечения список строк
            print(meetting)
            f_time = free_time(friend, start, finish)  # вывести свободное время чтобы всем встретиться список строк
            return render_template('synchronization.html', form=form, friend=friend, meetting=meetting, time=f_time)
    return render_template('/synchronization.html', form=form, friend=friend)


# def screen_3
def meetings(userlist, date_start, date_end):
    date_end = datetime.combine(date_end, datetime.min.time())
    date_start = datetime.combine(date_start, datetime.min.time())
    user_event_list = []
    cursor = mongo.db.users.find({"email": current_user})
    for id in cursor:
        user_id = id.get('_id')
        # находим все даты попавшие в промежуток
        event_line = mongo.db.events.find(
            {'$and': [{"user_id": user_id}, {"start": {'$lt': date_end}}, {"end": {'$gte': date_start}}]})
        for event in event_line:
            user_event_list.append({"location": event.get("location"), "date_start": event.get("start"),
                                    "date_end": event.get("end"), "flag": 0})

    # проверяем совпадения с другими юзерами
    for user in userlist:
        if user != current_user:
            cursor = mongo.db.users.find({"email": user})
            for id in cursor:
                user_id = id.get('_id')
                # находим все даты попавшие в промежуток
                for event in user_event_list:
                    event_line = mongo.db.events.find(
                        {'$and': [{"user_id": user_id}, {"start": {'$gte': event["date_start"]}},
                              {"end": {'$lte': event["date_end"]}}, {"location": event["location"]}]})
                    for id in event_line:
                        event["flag"] = 1

    result = []
    for event in user_event_list:
        if event["flag"] == 1:
            start = date_to_string(event["date_start"])
            finish = date_to_string(event["date_end"])
            result.append("Место: " + event["location"].replace("\\", "") + "\nВремя: " + start + " - " + finish)

    return result


def free_time(userlist, date_start, date_end):
    date_end = datetime.combine(date_end, datetime.min.time())
    date_start = datetime.combine(date_start, datetime.min.time())

    event_list = []
    # складываем мероприятия всех юзеров

    for user in userlist:
        cursor = mongo.db.users.find({"email": user})
        for id in cursor:
            user_id = id.get('_id')
            # находим все даты попавшие в промежуток
            event_line = mongo.db.events.find(
                {'$and': [{"user_id": user_id}, {"start": {'$lt': date_end}}, {"end": {'$gte': date_start}}]})
            for event in event_line:
                # добавляем пары начало конец меротприятия, для сортировки
                event_list.append((event.get('start'), event.get('end')))  # возвращаем все их свободное время
    # возвращаем список свободного времени у них

    return get_free_time(date_start, date_end, event_list)  # находим свободное время


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
        cursor1 = mongo.db.events.find({"user_id": user_id, "organizer": current_user, "start": {'$gte': cur_date}})

        for vis in cursor1:
            all_visitors += vis.get('visitors')

        for vis in all_visitors:
            if vis in result_visitors.keys():
                result_visitors[vis] += 1
            else:
                result_visitors[vis] = 1

        result_visitors.pop(current_user, None)

        my_tuple = [(k, result_visitors[k]) for k in
                             sorted(result_visitors, key=result_visitors.get, reverse=True)]
        result_visitors = {}
        for i in my_tuple:
            result_visitors[i[0]] = i[1]

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

        result_organizers.pop(current_user, None)
        my_tuple = [(k, result_organizers[k]) for k in sorted(result_organizers, key=result_organizers.get, reverse=True)]
        result_organizers = {}
        for i in my_tuple:
            result_organizers[i[0]] = i[1]
    print("Результаты подсчета количества организованных мероприятий", result_organizers)

    return [result_organizers,result_visitors]


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


def screen_6(date_start, date_end):
    global event_line
    date_end = datetime.combine(date_end, datetime.min.time())
    date_start = datetime.combine(date_start, datetime.min.time())
    event_list = []
    cursor = mongo.db.users.find({"email": current_user})
    for id in cursor:
        user_id = id.get('_id')
        # находим все даты попавшие в промежуток
        event_line = mongo.db.events.find(
            {'$and': [{"user_id": user_id}, {"start": {'$lt': date_end}}, {"end": {'$gte': date_start}}]})

    for event in event_line:
        # добавляем пары начало конец меротприятия, для сортировки
        event_list.append((event.get('start'), event.get('end')))

    return get_free_time(date_start, date_end, event_list)


def get_free_time(date_start, date_end, event_list):
    # сортируем
    event_list.sort(key=get_first)
    # оставляем только непересекающиеся даты
    tmp_list = []  # хранит непересекающиеся даты
    i = 0
    j = 0
    while i < len(event_list):
        if i == 0:
            tmp_list.append(event_list[i])
            j += 1
        else:
            date1 = tmp_list[j - 1]
            date2 = event_list[i]
            if has_overlap(date1, date2):
                tmp_list[j - 1] = (min(get_first(date1), get_first(date2)), max(get_second(date1), get_second(date2)))
            else:
                tmp_list.append(event_list[i])
                j += 1

        i += 1
    result_free = []
    i = 0
    if len(tmp_list) > 0:
        if get_first(tmp_list[i]) < date_start:
            if i + 1 < len(tmp_list):  # если в массиве больше чем одно событие
                result_free.append((get_second(tmp_list[i]), get_first(tmp_list[i + 1])))
            else:
                if date_end > get_second(tmp_list[i]):  # смотрим есть ли у нас вообще свободное время в этом промежутке
                    result_free.append((get_second(tmp_list[i]), date_end))

        else:
            if i + 1 < len(tmp_list):  # если в массиве больше чем одно событие
                result_free.append((date_start, get_first(tmp_list[i])))
                result_free.append((get_second(tmp_list[i]), get_first(tmp_list[i + 1])))
            else:
                if date_end > get_second(tmp_list[i]):  # смотрим есть ли у нас вообще свободное время в этом промежутке
                    result_free.append((date_start, get_first(tmp_list[i])))
                    result_free.append((get_second(tmp_list[i]), date_end))
    else:
        result_free.append((date_start, date_end))

    i += 1

    while i < len(tmp_list):
        if i + 1 < len(tmp_list):  # если это не последнее событие в массиве
            result_free.append((get_second(tmp_list[i]), get_first(tmp_list[i + 1])))
        else:
            if date_end > get_second(tmp_list[i]):  # если последнее событие
                result_free.append((get_second(tmp_list[i]), date_end))

        i += 1
    # преобразование в список строк
    tmp_list = []
    for time in result_free:
        start = date_to_string(get_first(time))
        finish = date_to_string(get_second(time))
        tmp_list.append(start + " - " + finish)

    return tmp_list


# проверка на пересечение дат
def has_overlap(date1, date2):
    latest_start = max(get_first(date1), get_first(date2))
    earliest_end = min(get_second(date1), get_second(date2))
    return latest_start <= earliest_end


def get_second(val):
    return val[1]


def get_first(val):
    return val[0]

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
    json_file = open('./src/data/' + user + '.json').read()
    json_file = json.loads(json_file)
    for event in json_file:
        if 'ORGANIZER' in event:
            dtstart = dateutil.parser.parse(event["DTSTART"]) + timedelta(
                hours=3)  # преобразуем в человеческий формат дату плюс 3 часа потому
            dtend = dateutil.parser.parse(event["DTEND"]) + timedelta(hours=3)
            mongo.db.events.insert({"user_id": user_id, "summary": event["SUMMARY"],
                                    "start": dtstart, "end": dtend, "location": event["LOCATION"],
                                    "organizer": event["ORGANIZER"], "visitors": event["VISITORS"]})


def date_to_string(date):
    result = date.strftime("%d-%m-%Y %H:%M")
    return result

def diagram(a):
    x = {
        'Организованные мероприятия': a[0],
        'Гость мероприятий': a[1],
    }
    print(type(x))
    data = pd.Series(x).reset_index(name='value').rename(columns={'index': 'country'})
    data['angle'] = data['value'] / data['value'].sum() * 2 * pi
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
