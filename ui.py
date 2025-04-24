import tkinter as tk
from tkinter import simpledialog, messagebox
from models import Student
from database import AttendanceSystem

class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống điểm danh")
        self.system = AttendanceSystem()

        tk.Label(root, text="MSSV").grid(row=0, column=0)
        self.entry_id = tk.Entry(root)
        self.entry_id.grid(row=0, column=1)

        tk.Label(root, text="Tên").grid(row=1, column=0)
        self.entry_name = tk.Entry(root)
        self.entry_name.grid(row=1, column=1)

        tk.Label(root, text="Lớp").grid(row=2, column=0)
        self.entry_class = tk.Entry(root)
        self.entry_class.grid(row=2, column=1)

        tk.Button(root, text="Thêm sinh viên", command=self.add_student).grid(row=3, column=0, columnspan=2)
        tk.Button(root, text="Điểm danh", command=self.mark_attendance).grid(row=4, column=0, columnspan=2)
        tk.Button(root, text="Xem danh sách đã điểm danh", command=self.view_all_history).grid(row=5, column=0, columnspan=2)
        tk.Button(root, text="Xuất file đã điểm danh", command=self.export_csv).grid(row=6, column=0, columnspan=2)
        tk.Button(root, text="Xem sinh viên trong lớp đã điểm danh", command=self.view_class_attendance).grid(row=7, column=0, columnspan=2)
        tk.Button(root, text="Check sinh viên", command=self.view_student_attendance).grid(row=8, column=0, columnspan=2)
        tk.Button(root, text="Danh sách điểm danh theo khoảng thời gian", command=self.view_by_date_range).grid(row=9, column=0, columnspan=2)
        tk.Button(root, text="Cập nhật tên", command=self.update_student_name).grid(row=10, column=0, columnspan=2)
        tk.Button(root, text="Xóa sinh viên", command=self.delete_student).grid(row=11, column=0, columnspan=2)

        self.text_area = tk.Text(root, height=15, width=60)
        self.text_area.grid(row=12, column=0, columnspan=2, pady=10)

    def add_student(self):
        sid = self.entry_id.get()
        name = self.entry_name.get()
        class_name = self.entry_class.get()
        if sid and name and class_name:
            student = Student(sid, name, class_name)
            self.system.add_student(student)
            messagebox.showinfo("Thành công", "Đã thêm sinh viên.")

    def mark_attendance(self):
        sid = self.entry_id.get()
        class_name = self.entry_class.get()
        if sid and class_name:
            self.system.mark_attendance(sid, class_name)
            messagebox.showinfo("Thành công", "Đã điểm danh.")

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

    def view_student_attendance(self):
        sid = self.entry_id.get()
        if sid:
            records = self.system.get_student_attendance(sid)
            self.text_area.delete("1.0", tk.END)
            for r in records:
                self.text_area.insert(tk.END, f"{r[0]} - {r[1]}\n")

    def view_by_date_range(self):
        start = simpledialog.askstring("Từ ngày", "Nhập ngày bắt đầu (YYYY-MM-DD):")
        end = simpledialog.askstring("Đến ngày", "Nhập ngày kết thúc (YYYY-MM-DD):")
        if start and end:
            try:
                records = self.system.get_attendance_by_date_range(start, end)
                self.display_records(records)
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))

    def update_student_name(self):
        sid = self.entry_id.get()
        new_name = self.entry_name.get()
        if sid and new_name:
            self.system.update_student_name(sid, new_name)
            messagebox.showinfo("Thành công", "Đã cập nhật tên sinh viên.")

    def delete_student(self):
        sid = self.entry_id.get()
        if sid:
            self.system.delete_student(sid)
            messagebox.showinfo("Đã xóa", f"Đã xóa sinh viên {sid}.")

    def export_csv(self):
        self.system.export_to_csv()
        messagebox.showinfo("Xuất file", "Đã xuất file CSV.")

    def display_records(self, records):
        self.text_area.delete("1.0", tk.END)
        for r in records:
            self.text_area.insert(tk.END, " - ".join(str(x) for x in r) + "\n")
