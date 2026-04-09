from app import app, EXCEL_UPLOAD_DIR
from models import db, User, Teacher, Class
import os, csv

with app.app_context():
    db.create_all()
    # create teacher and class
    if not User.query.filter_by(username='test_teacher').first():
        teacher_user = User(username='test_teacher', role='teacher')
        teacher_user.set_password('pass')
        db.session.add(teacher_user)
        db.session.flush()
        teacher = Teacher(user_id=teacher_user.id, full_name='Test Teacher')
        db.session.add(teacher)
        db.session.commit()
    else:
        teacher_user = User.query.filter_by(username='test_teacher').first()
        teacher = Teacher.query.filter_by(user_id=teacher_user.id).first()

    cls = Class(teacher_id=teacher.id, course='TestCourse', specialisation='Spec')
    db.session.add(cls); db.session.commit()

    client = app.test_client()
    # set session teacher id
    with client.session_transaction() as sess:
        sess['teacher_id'] = teacher_user.id

    # create csv file
    headers = ['USN','Name','Email','Phone number','Mother Tongue','Parent Name','Parent Email','Parent Phone','Company Name','Package (LPA)']
    rows = [headers, ['T001','Student One','s1@example.com','9999999999','Kannada','Parent','p1@example.com','8888888888','HCL','5']]
    csv_path = os.path.join(EXCEL_UPLOAD_DIR, 'test_preview.csv')
    os.makedirs(EXCEL_UPLOAD_DIR, exist_ok=True)
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    # call preview by filename
    res = client.post(f'/teacher/{cls.id}/preview_excel', json={'filename': 'test_preview.csv'})
    print('Status:', res.status_code)
    print(res.get_json())
