import sqlite3
from tkinter import Tk, Label, Entry, Button, messagebox, Frame
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# إنشاء قاعدة بيانات SQLite
def create_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY,
        employee_id INTEGER,
        check_in_time TEXT,
        check_out_time TEXT,
        break_time TEXT,
        prayer_time TEXT,
        training_time TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees (id)
    )
    ''')
    conn.commit()
    conn.close()

# إضافة موظف (مدير) تجريبي
def add_employee(username, password, role):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO employees (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # الموظف موجود بالفعل
    conn.close()

# دالة لتسجيل الدخول
def login(username, password):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT id, role FROM employees WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    return result

# دالة لتسجيل الوقت
def log_time(employee_id, check_in=False, check_out=False, break_time=False, prayer_time=False, training_time=False):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if check_in:
        c.execute("INSERT INTO attendance (employee_id, check_in_time) VALUES (?, ?)", (employee_id, current_time))
    if check_out:
        c.execute("UPDATE attendance SET check_out_time=? WHERE employee_id=? AND check_out_time IS NULL", (current_time, employee_id))
    if break_time:
        c.execute("UPDATE attendance SET break_time=? WHERE employee_id=? AND check_out_time IS NULL", (current_time, employee_id))
    if prayer_time:
        c.execute("UPDATE attendance SET prayer_time=? WHERE employee_id=? AND check_out_time IS NULL", (current_time, employee_id))
    if training_time:
        c.execute("UPDATE attendance SET training_time=? WHERE employee_id=? AND check_out_time IS NULL", (current_time, employee_id))
    
    conn.commit()
    conn.close()

# دالة لإرسال تقرير للمدير
def send_report(manager_email):
    msg = MIMEText("تقرير الحضور اليومي للموظفين.")
    msg['Subject'] = 'تقرير الحضور اليومي'
    msg['From'] = 'your_email@example.com'  # ضع بريدك هنا
    msg['To'] = manager_email

    with smtplib.SMTP('smtp.example.com', 587) as server:  # استبدل smtp.example.com بمزود البريد الخاص بك
        server.starttls()
        server.login('your_email@example.com', 'your_password')  # ضع بيانات اعتماد البريد الإلكتروني هنا
        server.send_message(msg)

# واجهة تسجيل الدخول
def show_login():
    login_window = Tk()
    login_window.title("تسجيل الدخول")
    login_window.configure(bg='#003366')  # لون خلفية كحلي

    Label(login_window, text="اسم المستخدم:", bg='#003366', fg='white', font=("Arial", 14)).grid(row=0)
    Label(login_window, text="كلمة المرور:", bg='#003366', fg='white', font=("Arial", 14)).grid(row=1)

    username_entry = Entry(login_window, font=("Arial", 14))
    password_entry = Entry(login_window, show='*', font=("Arial", 14))
    username_entry.grid(row=0, column=1)
    password_entry.grid(row=1, column=1)

    def on_login():
        username = username_entry.get()
        password = password_entry.get()
        user = login(username, password)
        if user:
            employee_id, role = user
            login_window.destroy()
            show_employee_interface(employee_id, role)
        else:
            messagebox.showerror("خطأ", "اسم المستخدم أو كلمة المرور غير صحيحة.")

    Button(login_window, text="تسجيل الدخول", command=on_login, bg='#005580', fg='white', font=("Arial", 14)).grid(row=2, columnspan=2, pady=10)
    login_window.mainloop()

# واجهة الموظف
def show_employee_interface(employee_id, role):
    employee_window = Tk()
    employee_window.title("واجهة الموظف")
    employee_window.configure(bg='#003366')  # لون خلفية كحلي

    # زر تسجيل الخروج
    def logout():
        employee_window.destroy()
        show_login()  # العودة إلى شاشة تسجيل الدخول

    logout_button = Button(employee_window, text="تسجيل الخروج", command=logout, bg='#FF4C4C', fg='white', font=("Arial", 12))
    logout_button.pack(side='top', anchor='ne', padx=10, pady=10)  # في الزاوية العليا اليمنى

    Label(employee_window, text=f"مرحبًا، {role}", bg='#003366', fg='white', font=("Arial", 16)).pack(pady=20)

    def log_action(action_name):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        messagebox.showinfo("وقت", f"{action_name} تم في: {current_time}")
        if action_name == "دخول":
            log_time(employee_id, check_in=True)
        elif action_name == "خروج":
            log_time(employee_id, check_out=True)
            send_report('manager@example.com')  # ضع بريد المدير هنا
            employee_window.destroy()  # أغلق نافذة الموظف
            show_login()  # العودة إلى شاشة تسجيل الدخول
        elif action_name == "استراحة":
            log_time(employee_id, break_time=True)
        elif action_name == "صلاة":
            log_time(employee_id, prayer_time=True)
        elif action_name == "تدريب":
            log_time(employee_id, training_time=True)

    # إطار للأزرار
    button_frame = Frame(employee_window, bg='#003366')
    button_frame.pack(pady=20)

    # أزرار العمل
    Button(button_frame, text="🕘 دخول", command=lambda: log_action("دخول"), bg='#005580', fg='white', font=("Arial", 16), width=12).grid(row=0, column=0, padx=10, pady=10)
    Button(button_frame, text="🚪 خروج", command=lambda: log_action("خروج"), bg='#005580', fg='white', font=("Arial", 16), width=12).grid(row=0, column=1, padx=10, pady=10)
    Button(button_frame, text="☕ استراحة", command=lambda: log_action("استراحة"), bg='#005580', fg='white', font=("Arial", 16), width=12).grid(row=0, column=2, padx=10, pady=10)
    Button(button_frame, text="🙏 صلاة", command=lambda: log_action("صلاة"), bg='#005580', fg='white', font=("Arial", 16), width=12).grid(row=1, column=0, padx=10, pady=10)
    Button(button_frame, text="📚 تدريب", command=lambda: log_action("تدريب"), bg='#005580', fg='white', font=("Arial", 16), width=12).grid(row=1, column=1, padx=10, pady=10)

    employee_window.mainloop()

# إنشاء قاعدة البيانات وإضافة موظف تجريبي
create_db()
add_employee("manager", "manager123", "مدير")
add_employee("Kamal", "Kamal123", "كمال")
add_employee("Asma", "Asma123", "أسماء")
add_employee("Taghreed", "Taghreed", "تغريد")
add_employee("employee4", "employee123", "موظف")

# عرض واجهة تسجيل الدخول
show_login()
