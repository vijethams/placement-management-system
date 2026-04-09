from app import app, db
from models import User, Teacher, Class, Student
import os

def test_db_ops():
    with app.app_context():
        try:
            print("--- Starting CRUD Operations Test ---")
            # 1. Create a test user for teacher
            user = User(username="test_teacher_unique", role="teacher")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            print(f"Created user: {user.username}")

            # 2. Add teacher details
            teacher = Teacher(user_id=user.id, full_name="Test Teacher", department="CS")
            db.session.add(teacher)
            db.session.commit()
            print(f"Created teacher: {teacher.full_name}")

            # 3. Create a class
            test_class = Class(course="Test BE", specialisation="CS", teacher_id=teacher.id)
            db.session.add(test_class)
            db.session.commit()
            print(f"Created class: {test_class.course}")

            # 4. Create a student
            student = Student(
                full_name="Test Student",
                usn="1TEST999",
                phone_number="+918088915514",
                email_id="student@test.com",
                parent_phone="+919107861437",
                parent_name="Test Parent",
                parent_email="parent@test.com",
                class_id=test_class.id
            )
            db.session.add(student)
            db.session.commit()
            print(f"Created student: {student.full_name}")

            # 5. Cleanup
            db.session.delete(student)
            db.session.delete(test_class)
            db.session.delete(teacher)
            db.session.delete(user)
            db.session.commit()
            print("--- Cleanup successful! ---")
            return True
        except Exception as e:
            print(f"--- FAILED: {e} ---")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == "__main__":
    if test_db_ops():
        print("Verification PASSED")
    else:
        print("Verification FAILED")
        exit(1)
