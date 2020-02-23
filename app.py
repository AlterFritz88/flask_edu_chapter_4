import json
import random
from flask import Flask, render_template, request
from flask import abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import InputRequired, Length, DataRequired

from data import goals, weekdays

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teachers_app.db'
app.secret_key = 'superkey'
db = SQLAlchemy(app)


class RequestForm(FlaskForm):
    name = StringField("Вас зовут: ", [InputRequired()])
    phone = StringField("Ваш телефон: ", [InputRequired()])
    goal = RadioField('Какая цель занятий?', default='travel', choices=[("travel", "Для путешествий"),
                                                      ("study", "Для школы"),
                                                      ("work", "Для работы"),
                                                      ("relocate", "Для переезда")])
    time = RadioField('Сколько времени есть?', default="1-2", choices=[("1-2", "1-2 часа в&nbsp;неделю"),
                                                      ("3-5", "3-5 часов в&nbsp;неделю"),
                                                      ("5-7", "5-7 часов в&nbsp;неделю"),
                                                      ("7-10", "7-10 часов в&nbsp;неделю")], )
    submit = SubmitField('Найдите мне преподавателя')


class BookingForm(FlaskForm):
    name = StringField("Вас зовут: ", [InputRequired()])
    phone = StringField("Ваш телефон: ", [InputRequired()])
    submit = SubmitField('Записаться на пробный урок')


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    about = Column(String, nullable=False)
    rating = Column(Float, nullable=False)
    picture = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    goals = Column(String, nullable=False)
    free = Column(String, nullable=False)
    booking = relationship("Booking", back_populates="teacher")


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    weekday = Column(String, nullable=False)
    time = Column(String, nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    teacher = relationship("Teacher", back_populates="booking")


class Request(db.Model):
    __tablename__ = 'requests'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    goal = Column(String, nullable=False)
    time = Column(String, nullable=False)


@app.route('/')
def main_page():
    teachers = db.session.query(Teacher).all()
    random.shuffle(teachers)
    return render_template("index.html", teachers=teachers[:6])


@app.route('/goals/<goal>')
def goals_render(goal: str):
    teachers = db.session.query(Teacher).filter(Teacher.goals.contains(goal)).order_by(Teacher.rating.desc())
    return render_template("goal.html", goal=goals[goal], teachers=teachers)


@app.route('/all_teachers')
def all_teachers():
    teachers = db.session.query(Teacher).order_by(Teacher.rating.desc())
    return render_template("all_teachers.html", teachers=teachers)


@app.route('/profiles/<id_teacher>')
def profile(id_teacher: str):
    teacher = db.session.query(Teacher).get(int(id_teacher))
    if not teacher:
        abort(404)

    teacher_free = json.loads(teacher.free)
    free_times = {'mon': [x for x, y in teacher_free['mon'].items() if y == True],
                  'tue': [x for x, y in teacher_free['tue'].items() if y == True],
                  'wed': [x for x, y in teacher_free['wed'].items() if y == True],
                  'thu': [x for x, y in teacher_free['thu'].items() if y == True],
                  'fri': [x for x, y in teacher_free['fri'].items() if y == True],
                  'sat': [x for x, y in teacher_free['sat'].items() if y == True],
                  'sun': [x for x, y in teacher_free['sun'].items() if y == True]}
    return render_template("profile.html", teacher=teacher, goals=goals, free_times=free_times)


@app.route('/request')
def request_teacher():
    form = RequestForm()
    return render_template("request.html", form=form)


@app.route('/request_done', methods=['POST', 'GET'])
def request_done():
    goal = request.form.get("goal")
    time = request.form.get("time")
    name = request.form.get("name")
    phone = request.form.get("phone")
    req = Request(name=name, phone=phone, time=time, goal=goal)
    db.session.add(req)
    db.session.commit()
    return render_template("request_done.html", goal=goals[goal], time=time, name=name, phone=phone)


@app.route('/booking/<id_teacher>/<weekday>/<time>')
def booking(id_teacher, weekday, time):
    teacher = db.session.query(Teacher).get(int(id_teacher))
    form = BookingForm()
    return render_template("booking.html", teacher=teacher, weekday=weekday, weekday_rus=weekdays[weekday], time=time+":00", form=form)


@app.route('/booking_done', methods=['POST', 'GET'])
def booking_done():
    name = request.form.get("name")
    phone = request.form.get("phone")
    id_teacher = request.form.get("clientTeacher")
    weekday = request.form.get("clientWeekday")
    time = request.form.get("clientTime")
    teacher = db.session.query(Teacher).get(int(id_teacher))
    book = Booking(name=name, phone=phone, weekday=weekday, time=time, teacher_id=id_teacher, teacher=teacher)
    db.session.add(book)
    db.session.commit()
    return render_template("booking_done.html", weekday=weekdays[weekday], time=time, name=name, phone_number=phone)


@app.errorhandler(404)
def invalid_route(e):
    return render_template("error.html")


if __name__ == "__main__":
    app.run()
