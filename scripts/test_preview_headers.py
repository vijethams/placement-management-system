import sys, os
# Ensure project root is on sys.path for imports when running this script directly
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app, EXCEL_UPLOAD_DIR
from models import db, User, Teacher, Class
import os, csv

with app.app_context():
    db.create_all()
    # ensure teacher exists
    teacher_user = User.query.filter_by(username='test_teacher').first()
    if not teacher_user:
        teacher_user = User(username='test_teacher', role='teacher')
        teacher_user.set_password('pass')
        db.session.add(teacher_user)
        db.session.flush()
        teacher = Teacher(user_id=teacher_user.id, full_name='Test Teacher')
        db.session.add(teacher)
        db.session.commit()
    else:
        teacher = Teacher.query.filter_by(user_id=teacher_user.id).first()

    cls = Class(teacher_id=teacher.id, course='TestCourse', specialisation='Spec')
    db.session.add(cls); db.session.commit()

    client = app.test_client()
    with client.session_transaction() as sess:
        sess['teacher_id'] = teacher_user.id

    # Good CSV
    good_csv = os.path.join(EXCEL_UPLOAD_DIR, 'test_preview.csv')
    # Missing USN CSV
    bad_csv = os.path.join(EXCEL_UPLOAD_DIR, 'test_preview_missing_usn.csv')

    headers_good = ['USN','Name','Email','Phone number','Mother Tongue','Parent Name','Parent Email','Parent Phone','Company Name','Package (LPA)']
    rows_good = [headers_good, ['T002','Student Two','s2@example.com','9999990000','Hindi','Parent','p2@example.com','8888880000','TCS','6']]
    with open(good_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows_good)

    headers_bad = ['Name','Email','Phone number','Mother Tongue','Parent Name','Parent Email','Parent Phone','Company Name','Package (LPA)']
    rows_bad = [headers_bad, ['T003','Student Three','s3@example.com','9999991111','English','Parent','p3@example.com','8888881111','INFY','7']]
    with open(bad_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows_bad)

    # Test good file by filename
    res_good = client.post(f'/teacher/{cls.id}/preview_excel', json={'filename': os.path.basename(good_csv)})
    print('Good status:', res_good.status_code, res_good.get_json())

    # Test bad file
    res_bad = client.post(f'/teacher/{cls.id}/preview_excel', json={'filename': os.path.basename(bad_csv)})
    print('Bad status:', res_bad.status_code, res_bad.get_json())
    # Test update (upload file) with notify disabled
    with open(good_csv, 'rb') as f:
        data = {
            'excel_file': (f, os.path.basename(good_csv)),
            'notify': '0'
        }
        res_update = client.post(f'/teacher/{cls.id}/update_excel', data=data, content_type='multipart/form-data')
        print('Update status:', res_update.status_code, res_update.get_json())