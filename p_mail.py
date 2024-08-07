import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib

def get_db_connection():
    return sqlite3.connect('D:\\py-temel\\personelmanagemnt\\email_system.db')

def register_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Bu kullanıcı adı zaten alınmış.")
    
    conn.close()

def login_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
    user = cursor.fetchone()
    
    conn.close()
    
    if user:
        return user[0]  # Kullanıcı ID'sini döndürüyoruz
    else:
        print("Geçersiz kullanıcı adı veya şifre.")
        return None

def send_email(sender_id, receiver_username, subject, body):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM users WHERE username = ?', (receiver_username,))
    receiver = cursor.fetchone()
    
    if receiver:
        receiver_id = receiver[0]
        cursor.execute('INSERT INTO emails (sender_id, receiver_id, subject, body) VALUES (?, ?, ?, ?)', 
                       (sender_id, receiver_id, subject, body))
        conn.commit()
    else:
        print("Alıcı bulunamadı.")
    
    conn.close()

def get_inbox(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT e.id, u.username AS sender, e.subject, e.body, e.timestamp 
    FROM emails e 
    JOIN users u ON e.sender_id = u.id 
    WHERE e.receiver_id = ? 
    ORDER BY e.timestamp DESC
    ''', (user_id,))
    
    inbox = cursor.fetchall()
    
    conn.close()
    
    return inbox

def get_sent_items(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT e.id, u.username AS receiver, e.subject, e.body, e.timestamp 
    FROM emails e 
    JOIN users u ON e.receiver_id = u.id 
    WHERE e.sender_id = ? 
    ORDER BY e.timestamp DESC
    ''', (user_id,))
    
    sent_items = cursor.fetchall()
    
    conn.close()
    
    return sent_items

class EmailSystemApp2:
    def __init__(self, root):
        self.root = root
        self.root.title("Email System")
        self.root.geometry("1920x1080")
        self.sent_listbox = None
        self.inbox_listbox = None
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        
        self.setup_login_ui()
    
    def setup_login_ui(self):
        login_frame = tk.Frame(self.root)
        login_frame.pack(pady=20)
        
        tk.Label(login_frame, text="Kullanıcı Adı:").grid(row=0, column=0, padx=10, pady=10)
        tk.Entry(login_frame, textvariable=self.username).grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(login_frame, text="Şifre:").grid(row=1, column=0, padx=10, pady=10)
        tk.Entry(login_frame, textvariable=self.password, show="*").grid(row=1, column=1, padx=10, pady=10)
        
        tk.Button(login_frame, text="Giriş Yap", command=self.login).grid(row=2, column=0, padx=10, pady=10)
    
    def login(self):
        username = self.username.get()
        password = self.password.get()
        user_id = login_user(username, password)
        
        if user_id:
            self.user_id = user_id
            self.username.set("")
            self.password.set("")
            self.setup_email_ui()
        else:
            messagebox.showerror("Error", "Invalid username or password")
    
    def register(self):
        username = self.username.get()
        password = self.password.get()
        register_user(username, password)
        messagebox.showinfo("Info", "User registered successfully")
    
    def setup_email_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        email_frame = tk.Frame(self.root)
        email_frame.pack(fill="both", expand=True)
        
        # Email sending section
        send_email_frame = tk.Frame(email_frame, border=2, relief="groove")
        send_email_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(send_email_frame, text="Send Email").pack(pady=10)
        
        tk.Label(send_email_frame, text="Receiver Username:").pack(pady=5)
        self.receiver_entry = tk.Entry(send_email_frame)
        self.receiver_entry.pack(pady=5)
        
        tk.Label(send_email_frame, text="Subject:").pack(pady=5)
        self.subject_entry = tk.Entry(send_email_frame)
        self.subject_entry.pack(pady=5)
        
        tk.Label(send_email_frame, text="Body:").pack(pady=5)
        self.body_entry = tk.Entry(send_email_frame)
        self.body_entry.pack(pady=5)
        
        send_button = tk.Button(send_email_frame, text="Send", command=self.send_email)
        send_button.pack(pady=10)
        
        # Inbox section
        inbox_frame = tk.Frame(email_frame, border=2, relief="groove")
        inbox_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(inbox_frame, text="Inbox").pack(pady=10)
        
        self.inbox_listbox = tk.Listbox(inbox_frame, height=10, width=100)
        self.inbox_listbox.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        inbox_scrollbar = ttk.Scrollbar(inbox_frame, orient=tk.VERTICAL, command=self.inbox_listbox.yview)
        inbox_scrollbar.pack(side="right", fill="y")
        self.inbox_listbox['yscrollcommand'] = inbox_scrollbar.set
        
        self.refresh_inbox()
        
        # Sent items section
        sent_frame = tk.Frame(email_frame, border=2, relief="groove")
        sent_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(sent_frame, text="Sent Items").pack(pady=10)
        
        self.sent_listbox = tk.Listbox(sent_frame, height=10, width=100)
        self.sent_listbox.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        sent_scrollbar = ttk.Scrollbar(sent_frame, orient=tk.VERTICAL, command=self.sent_listbox.yview)
        sent_scrollbar.pack(side="right", fill="y")
        self.sent_listbox['yscrollcommand'] = sent_scrollbar.set
        
        self.refresh_sent_items()
    
    def send_email(self):
        receiver_username = self.receiver_entry.get()
        subject = self.subject_entry.get()
        body = self.body_entry.get()
        
        send_email(self.user_id, receiver_username, subject, body)
        messagebox.showinfo("Info", "Email sent successfully")
        self.refresh_sent_items()
    
    def refresh_inbox(self):
        inbox_items = get_inbox(self.user_id)
        self.inbox_listbox.delete(0, tk.END)
        for item in inbox_items:
            self.inbox_listbox.insert(tk.END, f"From: {item[1]}, Subject: {item[2]}, Message: {item[3]}, Date: {item[4]}")
    
    def refresh_sent_items(self):
        sent_items = get_sent_items(self.user_id)
        self.sent_listbox.delete(0, tk.END)
        for item in sent_items:
            self.sent_listbox.insert(tk.END, f"To: {item[1]}, Subject: {item[2]}, Message: {item[3]}, Date: {item[4]}")
    

if __name__ == "__main__":
    root = tk.Tk()
    app = EmailSystemApp2(root)
    root.mainloop()