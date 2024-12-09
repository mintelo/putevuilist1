import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QDialog, QFormLayout, QComboBox, QCalendarWidget)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QDate
import sqlite3


# Инициализация базы данных
def init_db():
    conn = sqlite3.connect("../.venv/transport_system.db")
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        is_admin BOOLEAN DEFAULT FALSE
    )""")

    # Таблица водителей
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS drivers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        birth_date TEXT NOT NULL,
        experience INTEGER NOT NULL,
        phone TEXT NOT NULL,
        driver_id TEXT UNIQUE NOT NULL
    )""")

    # Таблица путевых листов
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS waybills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        driver_name TEXT NOT NULL,
        vehicle TEXT NOT NULL,
        waybill_number TEXT UNIQUE NOT NULL,
        cargo TEXT NOT NULL,
        route_from TEXT NOT NULL,
        route_to TEXT NOT NULL,
        transport_date TEXT NOT NULL
    )""")

    # Добавление администратора
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, is_admin) VALUES ('admin', 'admin123', 1)")
    conn.commit()
    conn.close()


# Главное окно
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система 'Путевой лист для перевозки груза'")
        self.setGeometry(100, 100, 800, 600)
        self.current_theme = "day"  # Текущая тема
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.title = QLabel("Система 'Путевой лист'")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        self.subtitle = QLabel("Добро пожаловать! Выберите действие:")
        self.subtitle.setStyleSheet("font-size: 18px; color: #555;")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.subtitle)

        self.buttons_layout = QHBoxLayout()

        self.login_button = QPushButton("Авторизация")
        self.login_button.setStyleSheet(self.get_button_style())
        self.login_button.clicked.connect(self.show_login)
        self.buttons_layout.addWidget(self.login_button)

        self.register_button = QPushButton("Регистрация")
        self.register_button.setStyleSheet(self.get_button_style())
        self.register_button.clicked.connect(self.show_register)
        self.buttons_layout.addWidget(self.register_button)

        self.layout.addLayout(self.buttons_layout)

        self.theme_button = QPushButton("Сменить тему")
        self.theme_button.setFixedSize(120, 40)
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setStyleSheet(self.get_button_style())
        self.layout.addWidget(self.theme_button, alignment=Qt.AlignRight)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.apply_theme(self.current_theme)

    def get_button_style(self):
        return """
        QPushButton {
            background-color: #4CAF50;
            color: white;
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        """

    def show_login(self):
        self.login_window = LoginWindow(self.current_theme)
        self.login_window.show()

    def show_register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()

    def toggle_theme(self):
        self.current_theme = "night" if self.current_theme == "day" else "day"
        self.apply_theme(self.current_theme)

    def apply_theme(self, theme):
        if theme == "day":
            self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #333;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            """)
        else:
            self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            """)


# Окно авторизации
class LoginWindow(QWidget):
    def __init__(self, current_theme):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setGeometry(300, 200, 400, 300)
        self.current_theme = current_theme
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.title = QLabel("Авторизация")
        self.title.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        self.username_label = QLabel("Логин:")
        self.layout.addWidget(self.username_label)

        self.username_input = QLineEdit()
        self.layout.addWidget(self.username_input)

        self.password_label = QLabel("Пароль:")
        self.layout.addWidget(self.password_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_input)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)

        self.setLayout(self.layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        conn = sqlite3.connect("../.venv/transport_system.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            QMessageBox.information(self, "Успех", "Добро пожаловать!")
            self.close()
            self.main_window = WaybillManager(is_admin=bool(user[3]), theme=self.current_theme)
            self.main_window.show()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")


# Окно регистрации
class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация")
        self.setGeometry(300, 200, 400, 300)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.title = QLabel("Регистрация")
        self.title.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        self.username_label = QLabel("Логин:")
        self.layout.addWidget(self.username_label)

        self.username_input = QLineEdit()
        self.layout.addWidget(self.username_input)

        self.password_label = QLabel("Пароль:")
        self.layout.addWidget(self.password_label)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_input)

        self.register_button = QPushButton("Зарегистрироваться")
        self.register_button.clicked.connect(self.register)
        self.layout.addWidget(self.register_button)

        self.setLayout(self.layout)

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        conn = sqlite3.connect("../.venv/transport_system.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", (username, password, 0))
            conn.commit()
            QMessageBox.information(self, "Успех", "Регистрация успешна!")
            self.close()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже существует!")
        finally:
            conn.close()


# Окно менеджера путевых листов
class WaybillManager(QWidget):
    def __init__(self, is_admin=False, theme="day"):
        super().__init__()
        self.setWindowTitle("Менеджер путевых листов")
        self.setGeometry(100, 100, 800, 600)
        self.is_admin = is_admin
        self.current_theme = theme
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.title = QLabel("Менеджер путевых листов")
        self.title.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.layout.addWidget(self.title)

        if self.is_admin:
            # Кнопка для добавления водителя
            self.add_driver_button = QPushButton("Добавить водителя")
            self.add_driver_button.clicked.connect(self.show_add_driver_form)
            self.layout.addWidget(self.add_driver_button)

            # Кнопка для добавления путевого листа
            self.add_waybill_button = QPushButton("Добавить путевой лист")
            self.add_waybill_button.clicked.connect(self.show_add_waybill_form)
            self.layout.addWidget(self.add_waybill_button)

        # Кнопка для просмотра базы водителей
        self.view_drivers_button = QPushButton("Просмотр базы водителей")
        self.view_drivers_button.clicked.connect(self.show_drivers)
        self.layout.addWidget(self.view_drivers_button)

        # Кнопка для работы с путевыми листами
        self.show_button = QPushButton("Показать путевые листы")
        self.show_button.clicked.connect(self.show_waybills)
        self.layout.addWidget(self.show_button)

        self.setLayout(self.layout)

    def show_add_driver_form(self):
        self.add_driver_window = AddDriverWindow()
        self.add_driver_window.show()

    def show_add_waybill_form(self):
        self.add_waybill_window = AddWaybillWindow()
        self.add_waybill_window.show()

    def show_drivers(self):
        conn = sqlite3.connect("../.venv/transport_system.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM drivers")
        rows = cursor.fetchall()

        if not rows:
            QMessageBox.information(self, "Информация", "Нет водителей для отображения.")
            return

        # Создаем таблицу для отображения данных водителей
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(len(rows))
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["ID", "ФИО", "Дата рождения", "Стаж", "Телефон"])

        for i, row in enumerate(rows):
            for j, col in enumerate(row[1:]):
                self.table_widget.setItem(i, j, QTableWidgetItem(str(col)))

        self.layout.addWidget(self.table_widget)
        conn.close()

    def show_waybills(self):
        conn = sqlite3.connect("../.venv/transport_system.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM waybills")
        rows = cursor.fetchall()

        if not rows:
            QMessageBox.information(self, "Информация", "Нет путевых листов для отображения.")
            return

        # Создаем таблицу для отображения данных путевых листов
        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(len(rows))
        self.table_widget.setColumnCount(7)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Водитель", "Транспорт", "Номер", "Груз", "Маршрут", "Дата"])

        for i, row in enumerate(rows):
            for j, col in enumerate(row[1:]):
                self.table_widget.setItem(i, j, QTableWidgetItem(str(col)))

        self.layout.addWidget(self.table_widget)
        conn.close()


# Окно для добавления водителя
class AddDriverWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить водителя")
        self.setGeometry(300, 200, 400, 400)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.title = QLabel("Добавить водителя")
        self.title.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.layout.addWidget(self.title)

        self.full_name_label = QLabel("ФИО:")
        self.layout.addWidget(self.full_name_label)

        self.full_name_input = QLineEdit()
        self.layout.addWidget(self.full_name_input)

        self.birth_date_label = QLabel("Дата рождения:")
        self.layout.addWidget(self.birth_date_label)

        self.birth_date_input = QLineEdit()
        self.layout.addWidget(self.birth_date_input)

        self.experience_label = QLabel("Стаж (в годах):")
        self.layout.addWidget(self.experience_label)

        self.experience_input = QLineEdit()
        self.layout.addWidget(self.experience_input)

        self.phone_label = QLabel("Телефон:")
        self.layout.addWidget(self.phone_label)

        self.phone_input = QLineEdit()
        self.layout.addWidget(self.phone_input)

        self.driver_id_label = QLabel("ID водителя:")
        self.layout.addWidget(self.driver_id_label)

        self.driver_id_input = QLineEdit()
        self.layout.addWidget(self.driver_id_input)

        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_driver)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)

    def add_driver(self):
        full_name = self.full_name_input.text()
        birth_date = self.birth_date_input.text()
        experience = self.experience_input.text()
        phone = self.phone_input.text()
        driver_id = self.driver_id_input.text()

        if not full_name or not birth_date or not experience or not phone or not driver_id:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        conn = sqlite3.connect("../.venv/transport_system.db")
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO drivers (full_name, birth_date, experience, phone, driver_id)
                VALUES (?, ?, ?, ?, ?)""",
                (full_name, birth_date, experience, phone, driver_id))
            conn.commit()
            QMessageBox.information(self, "Успех", "Водитель добавлен успешно!")
            self.close()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Водитель с таким ID уже существует!")
        finally:
            conn.close()


# Окно для добавления путевого листа
class AddWaybillWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить путевой лист")
        self.setGeometry(300, 200, 400, 400)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.title = QLabel("Добавить путевой лист")
        self.title.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        # Форма для ввода данных путевого листа
        self.driver_label = QLabel("Водитель:")
        self.layout.addWidget(self.driver_label)

        self.driver_input = QComboBox()
        self.load_drivers()
        self.layout.addWidget(self.driver_input)

        self.vehicle_label = QLabel("Транспорт:")
        self.layout.addWidget(self.vehicle_label)

        self.vehicle_input = QLineEdit()
        self.layout.addWidget(self.vehicle_input)

        self.waybill_number_label = QLabel("Номер путевого листа:")
        self.layout.addWidget(self.waybill_number_label)

        self.waybill_number_input = QLineEdit()
        self.layout.addWidget(self.waybill_number_input)

        self.cargo_label = QLabel("Груз:")
        self.layout.addWidget(self.cargo_label)

        self.cargo_input = QLineEdit()
        self.layout.addWidget(self.cargo_input)

        self.route_from_label = QLabel("Маршрут от:")
        self.layout.addWidget(self.route_from_label)

        self.route_from_input = QLineEdit()
        self.layout.addWidget(self.route_from_input)

        self.route_to_label = QLabel("Маршрут до:")
        self.layout.addWidget(self.route_to_label)

        self.route_to_input = QLineEdit()
        self.layout.addWidget(self.route_to_input)

        self.transport_date_label = QLabel("Дата транспорта:")
        self.layout.addWidget(self.transport_date_label)

        self.transport_date_input = QCalendarWidget()
        self.layout.addWidget(self.transport_date_input)

        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_waybill)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)

    def load_drivers(self):
        conn = sqlite3.connect("../.venv/transport_system.db")
        cursor = conn.cursor()
        cursor.execute("SELECT full_name FROM drivers")
        drivers = cursor.fetchall()
        self.driver_input.addItems([driver[0] for driver in drivers])
        conn.close()

    def add_waybill(self):
        driver_name = self.driver_input.currentText()
        vehicle = self.vehicle_input.text()
        waybill_number = self.waybill_number_input.text()
        cargo = self.cargo_input.text()
        route_from = self.route_from_input.text()
        route_to = self.route_to_input.text()
        transport_date = self.transport_date_input.selectedDate().toString(Qt.ISODate)

        if not driver_name or not vehicle or not waybill_number or not cargo or not route_from or not route_to:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        conn = sqlite3.connect("../.venv/transport_system.db")
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO waybills (driver_name, vehicle, waybill_number, cargo, route_from, route_to, transport_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (driver_name, vehicle, waybill_number, cargo, route_from, route_to, transport_date))
            conn.commit()
            QMessageBox.information(self, "Успех", "Путевой лист добавлен успешно!")
            self.close()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Путевой лист с таким номером уже существует!")
        finally:
            conn.close()


# Запуск приложения
if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
