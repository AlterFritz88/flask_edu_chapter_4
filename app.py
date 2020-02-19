import json
import random
from flask import Flask, render_template, request
from data import goals, weekdays

app = Flask(__name__)

with open("teachers.json", 'r') as f:
    teachers = json.load(f)


@app.route('/')
def main_page():
    random.shuffle(teachers)
    return render_template("index.html", teachers=teachers[:6])


@app.route('/goals/<goal>')
def goals_render(goal: str):
    teachers_by_goal = sorted([x for x in teachers if goal in x['goals']], key=lambda x: x['rating'], reverse=True)
    return render_template("goal.html", goal=goals[goal], teachers=teachers_by_goal)


@app.route('/all_teachers')
def all_teachers():
    teachers_by_goal = sorted(teachers, key=lambda x: x['rating'], reverse=True)
    return render_template("all_teachers.html", teachers=teachers_by_goal)


@app.route('/profiles/<id_teacher>')
def profile(id_teacher: str):
    teacher = [x for x in teachers if x['id'] == int(id_teacher)][0]
    free_times = {'mon': [x for x, y in teacher['free']['mon'].items() if y == True],
                  'tue': [x for x, y in teacher['free']['tue'].items() if y == True],
                  'wed': [x for x, y in teacher['free']['wed'].items() if y == True],
                  'thu': [x for x, y in teacher['free']['thu'].items() if y == True],
                  'fri': [x for x, y in teacher['free']['fri'].items() if y == True],
                  'sat': [x for x, y in teacher['free']['sat'].items() if y == True],
                  'sun': [x for x, y in teacher['free']['sun'].items() if y == True]}
    return render_template("profile.html", teacher=teacher, goals=goals, free_times=free_times)


@app.route('/request')
def request_teacher():
    return render_template("request.html")


@app.route('/request_done', methods=['POST', 'GET'])
def request_done():
    goal = request.form.get("goal")
    time = request.form.get("time")
    name = request.form.get("name")
    phone = request.form.get("phone")
    try:
        with open("request.json", 'r') as request_file:
            requests = json.loads(request_file.read())
    except FileNotFoundError:
        requests = []
    requests.append({"name": name,
                   "phone": phone,
                   "goal": goal,
                   "time": time})
    with open("request.json", 'w') as request_file:
        json.dump(requests, request_file)
    print(goal, time, name, phone)
    return render_template("request_done.html", goal=goals[goal], time=time, name=name, phone=phone)


@app.route('/booking/<id_teacher>/<weekday>/<time>')
def booking(id_teacher, weekday, time):
    teacher = [x for x in teachers if x['id'] == int(id_teacher)][0]
    return render_template("booking.html", teacher=teacher, weekday=weekday, weekday_rus=weekdays[weekday], time=time+":00")


@app.route('/booking_done', methods=['POST', 'GET'])
def booking_done():
    name = request.form.get("clientName")
    phone = request.form.get("clientPhone")
    teacher_id = request.form.get("clientTeacher")
    weekday = request.form.get("clientWeekday")
    time = request.form.get("clientTime")
    try:
        with open("booking.json", 'r') as orders_file:
            orders = json.loads(orders_file.read())
    except FileNotFoundError:
        orders = []
    orders.append({"name": name,
                   "phone": phone,
                   "teacher_id": int(teacher_id),
                   "weekday": weekday,
                   "time": time})
    with open("booking.json", 'w') as orders_file:
        json.dump(orders, orders_file)
    return render_template("booking_done.html", weekday=weekdays[weekday], time=time, name=name, phone_number=phone)


if __name__ == "__main__":
    app.run()
