import sqlite3
from datetime import datetime
import csv
from models import Student

class AttendanceSystem:
    def __init__(self, db_name="attendance.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                class_name TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                class_name TEXT,
                timestamp TEXT,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )
        ''')
        self.conn.commit()

    def add_student(self, student: Student):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT OR IGNORE INTO students (student_id, name, class_name) VALUES (?, ?, ?)',
            (student.student_id, student.name, student.class_name)
        )
        self.conn.commit()

    def mark_attendance(self, student_id, class_name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM students WHERE student_id=?", (student_id,))
        if cursor.fetchone() is None:
            print("Sinh viên không tồn tại.")
            return

        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute('''
            SELECT 1 FROM attendance
            WHERE student_id=? AND class_name=? AND DATE(timestamp)=?
        ''', (student_id, class_name, today))
        if cursor.fetchone():
            print(f"SV {student_id} đã điểm danh hôm nay")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            'INSERT INTO attendance (student_id, class_name, timestamp) VALUES (?, ?, ?)',
            (student_id, class_name, timestamp)
        )
        self.conn.commit()

    def get_attendance_record(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT s.student_id, s.name, a.class_name, a.timestamp
            FROM attendance a JOIN students s ON a.student_id=s.student_id
            ORDER BY a.timestamp DESC
        ''')
        return cursor.fetchall()

    def export_to_csv(self, filename="attendance_export.csv"):
        records = self.get_attendance_record()
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["MSSV", "Tên", "Lớp", "Thời Gian"])
            for r in records:
                writer.writerow(r)

    def get_class_attendance(self, class_name):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT s.student_id, s.name, a.timestamp
            FROM attendance a JOIN students s ON a.student_id=s.student_id
            WHERE a.class_name=?
        ''', (class_name,))
        return cursor.fetchall()

    def get_student_attendance(self, student_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT a.class_name, a.timestamp
            FROM attendance a
            WHERE a.student_id=?
        ''', (student_id,))
        return cursor.fetchall()

    def get_attendance_by_date_range(self, start_date, end_date):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT s.student_id, s.name, a.class_name, a.timestamp
            FROM attendance a JOIN students s ON a.student_id=s.student_id
            WHERE DATE(a.timestamp) BETWEEN ? AND ?
        ''', (start_date, end_date))
        return cursor.fetchall()

    def update_student_name(self, student_id, new_name):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE students SET name=? WHERE student_id=?', (new_name, student_id))
        self.conn.commit()

    def delete_student(self, student_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
        cursor.execute('DELETE FROM attendance WHERE student_id = ?', (student_id,))
        self.conn.commit()
