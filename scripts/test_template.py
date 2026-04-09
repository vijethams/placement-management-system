import importlib.util
import os

app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app.py'))
spec = importlib.util.spec_from_file_location('app', app_path)
app_mod = importlib.util.module_from_spec(spec)
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
spec.loader.exec_module(app_mod)
app = app_mod.app

with app.app_context():
    # Ensure tables
    from models import db, User, Teacher, Class
    db.create_all()

    # Create a test teacher + class
    import uuid
    uname = f"temp_teacher_{uuid.uuid4().hex[:8]}"
    test_user = User(username=uname, role='teacher')
    test_user.set_password('pass')
    db.session.add(test_user)
    db.session.commit()

    teacher = Teacher(user_id=test_user.id, full_name='Temp Teacher')
    db.session.add(teacher)
    db.session.commit()

    class_obj = Class(teacher_id=teacher.id, course='TempCourse', specialisation='Spec')
    db.session.add(class_obj)
    db.session.commit()

    with app.test_client() as c:
        # Mark session as logged-in teacher (the code expects user id in session['teacher_id'])
        with c.session_transaction() as sess:
            sess['teacher_id'] = test_user.id

        r = c.get(f'/teacher/{class_obj.id}/download_excel_template?format=csv')
        print('Status:', r.status_code)
        print('Content-Type:', r.content_type)
        print('Sample:', r.data[:200].decode('utf-8', errors='ignore'))
        r2 = c.get(f'/teacher/{class_obj.id}/download_excel_template?format=xlsx')
        print('Status (xlsx):', r2.status_code)
        print('Content-Type (xlsx):', r2.content_type)
        print('Length (xlsx):', len(r2.data))

