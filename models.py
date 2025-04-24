from datetime import datetime

class Student:
    def __init__(self, student_id, name, class_name):
        self.student_id = student_id
        self.name = name
        self.class_name = class_name

    def __str__(self):
        return f"{self.student_id} - {self.name}"

class AttendanceRecord:
    def __init__(self, student_id, class_name, timestamp=None):
        self.student_id = student_id
        self.class_name = class_name
        self.timestamp = timestamp if timestamp else datetime.now()

    def __str__(self):
        return f"{self.student_id} - {self.class_name} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
