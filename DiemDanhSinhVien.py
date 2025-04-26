import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime, timedelta
import csv 

#------------------------------Lop Sinh Vien---------------------------------------
class Student:
    def __init__(self, student_id, name, class_name):
        self.student_id = student_id
        self.name = name
        self.class_name = class_name
    def __str__(self):
        return f"{self.student_id} - {self.name}"

    
#-------------------------------------Ban Ghi Diem Danh--------------------------
class AttendanceRecord:
    def __init__(self, student_id, class_name, timestamp=None):
        self.student_id=student_id
        self.class_name=class_name
        self.timestamp = timestamp if timestamp else datetime.now()
    def __str__(self):
        return f"{self.student_id} - {self.class_name} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
    
#----------------------------He thong diem danh------------------------------------
class AttendanceSystem:
    def __init__(self, db_name="attendance.db"):
        self.conn=sqlite3.connect(db_name)
        self.create_tables()
    def create_tables(self):
        cursor=self.conn.cursor()
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
    def add_student(self, student:Student):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO students (student_id, name, class_name) VALUES (?, ?, ?)',
                       (student.student_id, student.name, student.class_name))
        self.conn.commit()
        
    def mark_attendance(self, student_id, class_name):
        cursor=self.conn.cursor()
    
        #Kiểm tra sinh viên có tồn tại hay ko
        cursor.execute("SELECT 1 FROM students WHERE student_id=?", (student_id,))
        if cursor.fetchone() is None:
            print("Sinh vien ko ton tai")
            return
        
        #Kiểm tra đã điểm danh hôm nay hay ko
        today=datetime.now().strftime("%Y-%m-%d")
        cursor.execute('''
            SELECT 1 FROM attendance
            WHERE student_id=? AND class_name=? AND DATE(timestamp)=?               
        ''', (student_id, class_name, today))
        if cursor.fetchone():
            print(f"SV {student_id} da diem danh hom nay")
            return
        
        #Code cũ
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO attendance (student_id, class_name, timestamp) VALUES (?, ?, ?)',
                       (student_id, class_name, timestamp))
        self.conn.commit()
        
    def get_attendance_record(self):
        cursor=self.conn.cursor()
        cursor.execute('''
            SELECT s.student_id, s.name, a.class_name, a.timestamp
            FROM attendance a JOIN students s ON a.student_id=s.student_id
            ORDER BY a.timestamp DESC               
                       ''')
        return cursor.fetchall()
    
    #Xuất file
    def export_to_csv(self, filename="attendance_export.csv"):
        records = self.get_attendance_record()
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer=csv.writer(file)
            writer.writerow(["MSSV", "Ten", "Lop", "Thoi Gian"])
            for r in records:
                writer.writerow([r[0], r[1], r[2], r[3]])
            
    #Xuất danh sách điểm danh ở 1 lớp học cụ thể 
    def get_class_attendance(self, class_name):
        cursor=self.conn.cursor()
        cursor.execute('''
            SELECT s.student_id, s.name, a.timestamp
            FROM attendance a JOIN students s ON a.student_id=s.student_id
            WHERE a.class_name=?
                       ''', (class_name,))
        return cursor.fetchall()
    
    #Xem lịch sử điểm danh cảu 1 sinh viên cụ thể 
    def get_student_attendance(self, student_id):
        cursor=self.conn.cursor()
        cursor.execute('''
            SELECT a.class_name, a.timestamp
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            WHERE a.student_id=?
                       ''', (student_id,))
        return cursor.fetchall()
    
    #Xuất danh sách ở 1 khoảng thời gian cụ thể
    def get_attendance_by_date_range(self, start_date, end_date):
        cursor=self.conn.cursor()
        cursor.execute('''
            SELECT s.student_id, s.name, a.class_name, a.timestamp
            FROM attendance a JOIN students s ON a.student_id=s.student_id
            WHERE DATE(a.timestamp) BETWEEN ? AND ?
        ''', (start_date, end_date))
        return cursor.fetchall()
    
    #Cập nhật tên 
    def update_student_name(self, student_id, new_name):
        cursor=self.conn.cursor()
        cursor.execute('UPDATE students SET name=? WHERE student_id=?',(new_name, student_id))
        self.conn.commit()
        
    #XÓa sinh viên
    def delete_student(self, student_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
        cursor.execute('DELETE FROM attendance WHERE student_id = ?', (student_id,))
        self.conn.commit()
  
# -------------------- GIAO DIỆN TKINTER --------------------
class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống điểm danh")
        self.system = AttendanceSystem()

        # --- Nhập sinh viên ---
        tk.Label(root, text="MSSV").grid(row=0, column=0)
        self.entry_id = tk.Entry(root)
        self.entry_id.grid(row=0, column=1)

        tk.Label(root, text="Tên").grid(row=1, column=0)
        self.entry_name = tk.Entry(root)
        self.entry_name.grid(row=1, column=1)

        tk.Label(root, text="Lớp").grid(row=2, column=0)
        self.entry_class = tk.Entry(root)
        self.entry_class.grid(row=2, column=1)

        # --- Nút chức năng chính ---
        tk.Button(root, text="Thêm sinh viên", command=self.add_student).grid(row=3, column=0, columnspan=2)
        tk.Button(root, text="Điểm danh", command=self.mark_attendance).grid(row=4, column=0, columnspan=2)
        tk.Button(root, text="Xem danh sách đã điểm danh", command=self.view_all_history).grid(row=5, column=0, columnspan=2)
        tk.Button(root, text="Xuất file đã điểm danh", command=self.export_csv).grid(row=6, column=0, columnspan=2)

        # --- Tính năng mở rộng ---
        tk.Button(root, text="Xem sinh viên trong lớp đã điểm danh", command=self.view_class_attendance).grid(row=7, column=0, columnspan=2)
        tk.Button(root, text="Check sinh viên", command=self.view_student_attendance).grid(row=8, column=0, columnspan=2)
        tk.Button(root, text="Danh sách đã điểm danh trong 1 khoảng thời gian cụ thể", command=self.view_by_date_range).grid(row=9, column=0, columnspan=2)
        tk.Button(root, text="Cập nhật tên", command=self.update_student_name).grid(row=10, column=0, columnspan=2)
        tk.Button(root, text="Xóa sinh viên", command=self.delete_student).grid(row=11, column=0, columnspan=2)

        # --- Vùng hiển thị kết quả ---
        self.text_area = tk.Text(root, height=15, width=60)
        self.text_area.grid(row=12, column=0, columnspan=2, pady=10)

    def add_student(self):
        sid = self.entry_id.get()
        name = self.entry_name.get()
        class_name = self.entry_class.get()
        if sid and name and class_name:
            student = Student(sid, name, class_name)
            self.system.add_student(student)
            messagebox.showinfo("Thành công", "Đã thêm sinh viên")
        else:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin sinh viên")

    def mark_attendance(self):
        sid = self.entry_id.get()
        class_name = self.entry_class.get()
        if sid and class_name:
            self.system.mark_attendance(sid, class_name)
            messagebox.showinfo("Thành công", "Đã điểm danh")
        else:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin (MSSV và lớp)")

    def view_all_history(self):
        records = self.system.get_attendance_record()
        self.display_records(records)

    def view_class_attendance(self):
        class_name = self.entry_class.get()
        if class_name:
            records = self.system.get_class_attendance(class_name) 
            self.text_area.delete("1.0", tk.END) 
            for r in records:
                self.text_area.insert(tk.END, f"{r[0]} - {r[1]} - {r[2]}\n")
        else:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên lớp")

    def view_student_attendance(self):
        sid = self.entry_id.get()
        if sid: 
            records = self.system.get_student_attendance(sid) 
            self.text_area.delete("1.0", tk.END)
            for r in records: 
                self.text_area.insert(tk.END, f"{r[0]} - {r[1]}\n")
        else:
            messagebox.showerror("Lỗi", "Vui lòng nhập MSSV")
    
    def view_by_date_range(self):
        start = tk.simpledialog.askstring("Từ ngày", "Nhập ngày bắt đầu (YYYY-MM-DD):")
        end = tk.simpledialog.askstring("Đến ngày", "Nhập ngày kết thúc (YYYY-MM-DD):")
        if start and end:
            try:
                records = self.system.get_attendance_by_date_range(start, end)
                self.display_records(records)
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
        else:
            messagebox.showerror("Lỗi", "Vui lòng nhập cả ngày bắt đầu và ngày kết thúc.")

    def update_student_name(self):
        sid = self.entry_id.get()
        new_name = self.entry_name.get()
        if sid and new_name:
            self.system.update_student_name(sid, new_name)
            messagebox.showinfo("Thành công", "Đã cập nhật tên sinh viên.")
        else:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ MSSV và tên mới.")

    def delete_student(self):
        sid = self.entry_id.get()
        if sid:
            self.system.delete_student(sid)
            messagebox.showinfo("Đã xóa", f"Đã xóa sinh viên {sid}.")

    def export_csv(self):
        self.system.export_to_csv()
        messagebox.showinfo("Xuất file", "Đã xuất file attendance_export.csv")

    def display_records(self, records):
        self.text_area.delete("1.0", tk.END)
        for r in records:
            self.text_area.insert(tk.END, " - ".join(str(x) for x in r) + "\n")

# --- Khởi chạy ---
if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
