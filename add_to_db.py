import json
from app import Teacher, db, Request, Booking
#
# with open("teachers.json", 'r') as f:
#     teachers = json.load(f)
#
#
# db.create_all()
# for t in teachers:
#     teacher = Teacher(id=t['id'],
#                       name=t["name"],
#                       about=t["about"],
#                       rating=t["rating"],
#                       picture=t['picture'],
#                       price=t['price'],
#                       goals=" ".join(t['goals']),
#                       free=json.dumps(t['free']))
#     db.session.add(teacher)
#
# db.session.commit()

req = db.session.query(Teacher).all()

for t in req:
    print(t.name, t.booking)
    if t.booking:
        for b in t.booking:
            print(b.name)
