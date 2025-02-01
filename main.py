import faulthandler
faulthandler.enable()
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
import MySQLdb
import mysql.connector
import pandas as pd
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
                             QLineEdit, QMessageBox, QComboBox, QTextEdit, QFileDialog)
from PyQt6.QtGui import QPalette, QColor
from fpdf import FPDF
from hashlib import sha256  # For password hashing


DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}
def connect_db():
    return MySQLdb.connect(**DB_CONFIG)


# Hash password for security
def hash_password(password):
    return sha256(password.encode()).hexdigest()


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 300, 200)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.authenticate_user)
        layout.addWidget(self.login_btn)

        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.open_register_window)
        layout.addWidget(self.register_btn)

        self.setLayout(layout)

    def authenticate_user(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password.")
            return

        conn = None
        cursor = None
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s AND password_hash = %s",
                           (username, hash_password(password)))
            user = cursor.fetchone()

            if user:
                print("Login successful")  # Debugging
                self.main_window = DeviceManagementApp()
                self.main_window.show()
                self.hide()  # Hide instead of closing
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
        except Exception as e:
            print(f"Error during login: {e}")  # Debugging
            QMessageBox.warning(self, "Error", f"An error occurred: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def open_register_window(self):
        self.register_window = RegisterWindow()
        self.register_window.show()


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register")
        self.setGeometry(100, 100, 300, 200)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.confirm_password_input)

        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.register_user)
        layout.addWidget(self.register_btn)

        self.setLayout(layout)

    def register_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not username or not password or not confirm_password:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Input Error", "Passwords do not match.")
            return

        conn = None
        cursor = None
        try:
            conn = connect_db()
            cursor = conn.cursor()

            # Check if the username already exists
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Registration Failed", "Username already exists.")
                return

            # Insert the new user into the database
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                           (username, hash_password(password), "user"))
            conn.commit()
            QMessageBox.information(self, "Registration Successful", "User registered successfully!")
            self.close()
        except Exception as e:
            print(f"Error during registration: {e}")  # Debugging
            QMessageBox.warning(self, "Registration Failed", f"An error occurred: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


class DeviceManagementApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Device Management System")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()

    def initUI(self):
        # Dark mode
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        self.setPalette(palette)

        layout = QVBoxLayout()

        self.device_table = QTableWidget()
        self.device_table.setColumnCount(6)
        self.device_table.setHorizontalHeaderLabels(["ID", "Name", "Type", "Count", "Serial", "Issues"])
        layout.addWidget(self.device_table)

        self.device_name = QLineEdit()
        self.device_name.setPlaceholderText("Device Name")
        layout.addWidget(self.device_name)

        self.device_type = QComboBox()
        self.device_type.addItems(["Probe-Blueetooth", "Probe-SDI-12-Side", "Probe-SDI-12-R/C", "Probe-Stage2-Side", "Probe-Stage2-R/C", "Board", "Other"])
        layout.addWidget(self.device_type)

        self.device_count = QLineEdit()
        self.device_count.setPlaceholderText("Device Count")
        layout.addWidget(self.device_count)

        self.device_serial = QLineEdit()
        self.device_serial.setPlaceholderText("Serial Number")
        layout.addWidget(self.device_serial)

        self.device_issue = QTextEdit()
        self.device_issue.setPlaceholderText("Issues/Error Details")
        layout.addWidget(self.device_issue)

        self.device_comment = QTextEdit()
        self.device_comment.setPlaceholderText("Comments")
        layout.addWidget(self.device_comment)

        self.add_device_btn = QPushButton("Add Device")
        self.add_device_btn.clicked.connect(self.add_device)
        layout.addWidget(self.add_device_btn)

        self.export_report_btn = QPushButton("Export Report (Excel)")
        self.export_report_btn.clicked.connect(self.export_report_excel)
        layout.addWidget(self.export_report_btn)

        self.export_pdf_btn = QPushButton("Export Report (PDF)")
        self.export_pdf_btn.clicked.connect(self.export_report_pdf)
        layout.addWidget(self.export_pdf_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_devices()

    def load_devices(self):
        conn = None
        cursor = None
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM devices")
            devices = cursor.fetchall()

            self.device_table.setRowCount(len(devices))
            for row_index, row_data in enumerate(devices):
                for col_index, col_data in enumerate(row_data):
                    self.device_table.setItem(row_index, col_index, QTableWidgetItem(str(col_data)))
        except Exception as e:
            print(f"Error loading devices: {e}")  # Debugging
            QMessageBox.warning(self, "Error", f"An error occurred: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def add_device(self):
        name = self.device_name.text()
        device_type = self.device_type.currentText()
        count = self.device_count.text()
        serial = self.device_serial.text()
        issues = self.device_issue.toPlainText()
        comment = self.device_comment.toPlainText()

        if not name or not device_type or not count or not serial:
            QMessageBox.warning(self, "Input Error", "Please fill in all required fields.")
            return

        conn = None
        cursor = None
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO devices (name, type, count, serial_number, comment) VALUES (%s, %s, %s, %s, %s)",
                (name, device_type, count, serial, comment)
            )
            conn.commit()
            QMessageBox.information(self, "Success", "Device added successfully!")

            #Clear input fields  after successful addition

            self.device_name.clear()
            self.device_type.setCurrentIndex(0)  # Reset to the first item in the combo box
            self.device_count.clear()
            self.device_serial.clear()
            self.device_issue.clear()
            self.device_comment.clear()

            # Refresh the device table
            self.load_devices()

        except Exception as e:
            print(f"Error adding device: {e}")  # Debugging
            QMessageBox.warning(self, "Error", f"Failed to add device: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def export_report_excel(self):
        conn = None
        try:
            conn = connect_db()
            query = "SELECT * FROM devices"
            df = pd.read_sql(query, conn)

            file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", "", "Excel Files (*.xlsx)")
            if file_path:
                df.to_excel(file_path, index=False)
                QMessageBox.information(self, "Export Successful", "Excel report saved successfully!")
        except Exception as e:
            print(f"Error exporting to Excel: {e}")  # Debugging
            QMessageBox.warning(self, "Error", f"An error occurred: {e}")
        finally:
            if conn:
                conn.close()

    def export_report_pdf(self):
        conn = None
        cursor = None
        try:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM devices")
            rows = cursor.fetchall()

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, "Device Report", ln=True, align='C')
            pdf.ln(10)
            pdf.set_font("Arial", size=11)

            for row in rows:
                pdf.cell(200, 10,
                         f"ID: {row[0]} | Name: {row[1]} | Type: {row[2]} | Count: {row[3]} | Serial: {row[4]} | Issues: {row[5]}",
                         ln=True)

            file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", "", "PDF Files (*.pdf)")
            if file_path:
                pdf.output(file_path)
                QMessageBox.information(self, "Export Successful", "PDF report saved successfully!")
        except Exception as e:
            print(f"Error exporting to PDF: {e}")  # Debugging
            QMessageBox.warning(self, "Error", f"An error occurred: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())