import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

# -------------------- LỚP SINH VIÊN --------------------
class Student:
    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name

    def __str__(self):
        return f"{self.student_id} - {self.name}"


# -------------------- LỚP BẢN GHI ĐIỂM DANH --------------------
class AttendanceRecord:
    def __init__(self, student_id, class_name, timestamp=None):
        self.student_id = student_id
        self.class_name = class_name
        self.timestamp = timestamp if timestamp else datetime.now()

    def __str__(self):
        return f"{self.student_id} - {self.class_name} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


# -------------------- LỚP HỆ THỐNG ĐIỂM DANH --------------------
class AttendanceSystem:
    def __init__(self, db_name="attendance.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL
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
        cursor.execute('INSERT OR IGNORE INTO students (student_id, name) VALUES (?, ?)',
                       (student.student_id, student.name))
        self.conn.commit()

    def mark_attendance(self, student_id, class_name):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO attendance (student_id, class_name, timestamp) VALUES (?, ?, ?)',
                       (student_id, class_name, timestamp))
        self.conn.commit()

    def get_attendance_records(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT s.student_id, s.name, a.class_name, a.timestamp
            FROM attendance a JOIN students s ON a.student_id = s.student_id
            ORDER BY a.timestamp DESC
        ''')
        return cursor.fetchall()


# -------------------- GIAO DIỆN TKINTER --------------------
class AttendanceApp:
    def __init__(self, root):
        self.system = AttendanceSystem()
        self.root = root
        self.root.title("Ứng dụng điểm danh sinh viên")

        # Entry thêm sinh viên
        self.name_entry = tk.Entry(root)
        self.name_entry.grid(row=0, column=1)
        self.id_entry = tk.Entry(root)
        self.id_entry.grid(row=1, column=1)

        tk.Label(root, text="Tên sinh viên:").grid(row=0, column=0)
        tk.Label(root, text="MSSV:").grid(row=1, column=0)
        tk.Button(root, text="Thêm sinh viên", command=self.add_student).grid(row=2, column=0, columnspan=2, pady=5)

        # Entry điểm danh
        self.class_entry = tk.Entry(root)
        self.class_entry.grid(row=3, column=1)
        tk.Label(root, text="Tên lớp:").grid(row=3, column=0)

        self.attend_id_entry = tk.Entry(root)
        self.attend_id_entry.grid(row=4, column=1)
        tk.Label(root, text="MSSV cần điểm danh:").grid(row=4, column=0)

        tk.Button(root, text="Điểm danh", command=self.mark_attendance).grid(row=5, column=0, columnspan=2, pady=5)

        # Nút xem lịch sử
        tk.Button(root, text="Xem danh sách điểm danh", command=self.show_attendance_records).grid(row=6, column=0, columnspan=2, pady=10)

        # Bảng hiển thị
        self.tree = ttk.Treeview(root, columns=("MSSV", "Tên", "Lớp", "Thời gian"), show="headings")
        for col in ("MSSV", "Tên", "Lớp", "Thời gian"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.grid(row=7, column=0, columnspan=2)

    def add_student(self):
        name = self.name_entry.get()
        student_id = self.id_entry.get()
        if name and student_id:
            student = Student(student_id, name)
            self.system.add_student(student)
            messagebox.showinfo("Thành công", "Đã thêm sinh viên.")
            self.name_entry.delete(0, tk.END)
            self.id_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Lỗi", "Nhập đầy đủ tên và MSSV!")

    def mark_attendance(self):
        class_name = self.class_entry.get()
        student_id = self.attend_id_entry.get()
        if class_name and student_id:
            self.system.mark_attendance(student_id, class_name)
            messagebox.showinfo("Thành công", "Đã điểm danh.")
            self.class_entry.delete(0, tk.END)
            self.attend_id_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Lỗi", "Nhập MSSV và tên lớp!")

    def show_attendance_records(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        records = self.system.get_attendance_records()
        for rec in records:
            self.tree.insert("", "end", values=rec)


# -------------------- CHẠY CHƯƠNG TRÌNH --------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
