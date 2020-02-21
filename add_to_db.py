import json
from app import Teacher, db

with open("teachers.json", 'r') as f:
    teachers = json.load(f)

print(teachers)
db.create_all()
for t in teachers:
    teacher = Teacher(name=t["name"], about=t["about"], rating=t["rating"], picture=t['picture'], )
    db.session.add(teacher)

db.session.commit()

teachers = db.session.query(Teacher).all()

for t in teachers:
    print(t.name)