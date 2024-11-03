
from PyQt5.QtCore import Qt, QSettings, QTimer, QUrl
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtNetwork import QNetworkCookie
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings, QWebEnginePage
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMenu, QShortcut

from dialogs import HelpDialog, CssDialog, JsDialog
from utils import resource_path


class AutoScrollApp(QMainWindow):
    def __init__(self, url):
        super().__init__()
        self.setWindowTitle("Boosty Chat Auto Scroll")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon(resource_path("resources/app_icon.ico")))

        # Установка начальных значений
        self.scroll_enabled = False
        self.frame_hidden = False

        # Основной виджет и макет
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # WebView для отображения веб-страницы (занимает большую часть экрана)
        self.browser = QWebEngineView(self)

        profile = self.browser.page().profile()
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

        # self.set_cookie()

        if url is None:
            url = "https://boosty.to/hellyeahplay/streams/only-chat"

        self.browser.setUrl(QUrl(url))  # Укажите URL Boosty чата
        self.browser.loadFinished.connect(self.apply_saved_css)  # Применение CSS после загрузки страницы
        main_layout.addWidget(self.browser)

        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.WebRTCPublicInterfacesOnly, True)
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)

        # Загрузка и применение CSS при запуске
        self.settings = QSettings("BoostyChatAutoScroll", "Settings")

        # Панель управления
        control_panel = QHBoxLayout()
        control_panel.setContentsMargins(5, 0, 5, 5)

        # Кнопка помощи
        self.help_button = QPushButton("Помощь", self)
        self.help_button.setFixedSize(70, 25)
        self.help_button.clicked.connect(self.show_help)
        control_panel.addWidget(self.help_button)

        # Статус автоскроллинга
        self.status_label = QLabel("Scroll: Off", self)
        self.status_label.setFixedSize(70, 25)
        control_panel.addWidget(self.status_label)

        # Выравнивание панели управления
        control_panel.addStretch()
        main_layout.addLayout(control_panel)

        # Кнопка для контекстного меню
        self.menu_button = QPushButton(self)
        self.menu_button.setIcon(QIcon(resource_path("resources/menu.png")))
        self.menu_button.setFixedSize(30, 30)
        # self.menu_button.setStyleSheet("border: none;")
        self.menu_button.setCursor(Qt.PointingHandCursor)
        self.menu_button.move(self.width() - 35, self.height() - 32)
        self.menu_button.clicked.connect(self.show_context_menu)

        # Контекстное меню
        self.context_menu = QMenu(self)
        self.context_menu.addAction("Перезагрузить", self.do_reload_page)
        self.context_menu.addAction("Изменить CSS", self.show_css_dialog)
        self.context_menu.addAction("Выполнить JavaScript", self.show_js_dialog)

        # Горячие клавиши
        toggle_scroll_shortcut = QShortcut(QKeySequence("Ctrl+Shift+L"), self)
        toggle_scroll_shortcut.activated.connect(self.toggle_scroll)

        toggle_frame_shortcut = QShortcut(QKeySequence("Ctrl+Shift+K"), self)
        toggle_frame_shortcut.activated.connect(self.toggle_frame)

        open_dev_tools_shortcut = QShortcut(QKeySequence("Ctrl+Shift+I"), self)
        open_dev_tools_shortcut.activated.connect(self.open_dev_tools)

        # Таймер для плавного скроллинга
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self.perform_scroll)

        self.dev_tools_window = None

    def resizeEvent(self, event):
        # Обновление позиции кнопки меню при изменении размера окна
        self.menu_button.move(self.width() - 35, self.height() - 32)
        super().resizeEvent(event)

    def do_reload_page(self):
        self.browser.reload()

    def open_dev_tools(self):
        if self.dev_tools_window is None or not self.dev_tools_window.isVisible():
            self.dev_tools_window = QWebEngineView()
            dev_page = QWebEnginePage(self.browser.page().profile(), self.dev_tools_window)
            self.dev_tools_window.setPage(dev_page)
            dev_page.setInspectedPage(self.browser.page())

            # Настройки нового окна
            self.dev_tools_window.setWindowTitle("Developer Tools")
            self.dev_tools_window.resize(800, 600)
            self.dev_tools_window.show()
        else:
            # Если окно уже открыто, активируем его
            self.dev_tools_window.raise_()
            self.dev_tools_window.activateWindow()

    def show_js_dialog(self):
        # Открытие окна для ввода JavaScript
        js_dialog = JsDialog(self.browser, self)
        js_dialog.exec_()

    def show_context_menu(self):
        # Показ контекстного меню
        self.context_menu.exec_(self.menu_button.mapToGlobal(self.menu_button.rect().bottomRight()))

    def set_cookie(self):
        # document.cookie.split('; ').find(row => row.startsWith('auth=')).split('=')[1];

        # Установка cookie для страницы
        cookie_store = self.browser.page().profile().cookieStore()

        cookie = QNetworkCookie()
        cookie.setName(b"auth")
        cookie.setValue(
            b"{%22accessToken%22:%22194f2d895ab2de4867a1a589fecdf8f1d76c9869d6067172fe4d79c72a6ff1a2%22%2C%22refreshToken%22:%227691b7c94e7127e48fa4c99229ae86ddb90177f49679f171493af1c378e59361%22%2C%22expiresAt%22:1730835377287}")
        cookie.setDomain(".boosty.to")
        cookie.setPath("/")
        cookie.setSecure(True)
        cookie.setHttpOnly(True)

        # Установить cookie
        cookie_store.setCookie(cookie, QUrl("https://boosty.to"))

    def apply_saved_css(self):
        # Применение сохраненного CSS после загрузки страницы
        saved_css = self.settings.value("css", "")
        if saved_css:
            script = f"""
            var existingStyle = document.getElementById('custom-style');
            if (existingStyle) {{
                existingStyle.innerHTML = `{saved_css}`;
            }} else {{
                var style = document.createElement('style');
                style.type = 'text/css';
                style.id = 'custom-style';
                style.appendChild(document.createTextNode(`{saved_css}`));
                document.head.appendChild(style);
            }}
            """
            self.browser.page().runJavaScript(script)

    def show_help(self):
        # Открытие всплывающего окна с текстом помощи
        help_dialog = HelpDialog(self)
        help_dialog.exec_()

    def show_css_dialog(self):
        # Открытие окна для ввода CSS
        css_dialog = CssDialog(self.browser, self)
        css_dialog.exec_()

    def toggle_scroll(self):
        self.scroll_enabled = not self.scroll_enabled
        self.status_label.setText(f"Scroll: {'On' if self.scroll_enabled else 'Off'}")

        # Включение или отключение таймера
        if self.scroll_enabled:
            self.scroll_timer.start(10)
        else:
            self.scroll_timer.stop()

    def perform_scroll(self):
        # Выполняем JavaScript для плавной прокрутки вниз на 2 пикселя
        # self.browser.page().runJavaScript("window.scrollBy(0, 2);")
        self.browser.page().runJavaScript("document.querySelector('.ChatBoxBase_list_Kg9et').scrollBy(0, 100);")

    def toggle_frame(self):
        # Переключение между безрамочным и стандартным режимами окна
        if self.frame_hidden:
            self.setWindowFlags(Qt.Window)
            self.setWindowOpacity(1)
        else:
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setWindowOpacity(1)

        self.frame_hidden = not self.frame_hidden
        self.show()  # Необходимо обновить окно после изменения флагов