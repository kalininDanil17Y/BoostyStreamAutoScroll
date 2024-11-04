
from PyQt5.QtCore import Qt, QSettings, QTimer, QUrl
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtNetwork import QNetworkCookie
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings, QWebEnginePage
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMenu, QShortcut, \
    QAction

from dialogs import HelpDialog, CssDialog
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
        self.ui_hidden = False

        # Основной виджет и макет
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # WebView для отображения веб-страницы
        self.browser = QWebEngineView(self)

        profile = self.browser.page().profile()
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

        # self.set_cookie()

        if url is None:
            url = "https://boosty.to/hellyeahplay/streams/only-chat"

        self.browser.setUrl(QUrl(url))
        self.browser.loadFinished.connect(self.apply_saved_css)
        main_layout.addWidget(self.browser)

        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.WebRTCPublicInterfacesOnly, True)
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        self.browser.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)

        # Загрузка и применение CSS при запуске
        self.settings = QSettings("BoostyChatAutoScroll", "Settings")

        # Создаем контейнер для компоновщика
        self.control_panel_widget = QWidget()
        self.control_panel = QHBoxLayout(self.control_panel_widget)
        self.control_panel.setContentsMargins(5, 0, 5, 5)

        # Кнопка помощи
        self.help_button = QPushButton("Помощь", self)
        self.help_button.setFixedSize(70, 25)
        self.help_button.clicked.connect(self.show_help)
        self.control_panel.addWidget(self.help_button)

        # Статус автоскроллинга
        self.status_label = QPushButton("Scroll: Off", self)
        self.status_label.setFixedSize(70, 25)
        self.control_panel.addWidget(self.status_label)
        self.status_label.clicked.connect(self.toggle_scroll)

        # Выравнивание панели управления
        self.control_panel.addStretch()

        # Устанавливаем минимальные и максимальные размеры для контейнера панели управления
        self.control_panel_widget.setFixedHeight(30)  # Высота панели управления
        self.control_panel_widget.adjustSize()  # Подгоняем размер под содержимое

        # Добавляем контейнерный виджет с компоновщиком в основной компоновщик
        main_layout.addWidget(self.control_panel_widget)

        # Кнопка для контекстного меню
        self.menu_button = QPushButton(self)
        self.menu_button.setIcon(QIcon(resource_path("resources/menu.png")))
        self.menu_button.setFixedSize(30, 30)
        self.menu_button.setCursor(Qt.PointingHandCursor)
        self.menu_button.move(self.width() - 35, self.height() - 32)
        self.menu_button.clicked.connect(self.show_context_menu)

        # Контекстное меню
        self.context_menu = QMenu(self)
        self.context_menu.addAction("Перезагрузить (F5)", self.do_reload_page)
        self.context_menu.addAction("Открыть DevTools (Ctrl+Shift+I)", self.open_dev_tools)
        self.context_menu.addAction("Изменить CSS (Ctrl+Shift+C)", self.show_css_dialog)

        self.toggle_ui_action = self.context_menu.addAction("Скрыть UI (Ctrl+Shift+K)", self.toggle_ui)
        self.toggle_frame_action = self.context_menu.addAction("Скрыть окно (Ctrl+Shift+J)", self.toggle_frame)

        # Включить прокрутку
        toggle_scroll_shortcut = QShortcut(QKeySequence("Ctrl+Shift+L"), self)
        toggle_scroll_shortcut.activated.connect(self.toggle_scroll)

        # Скрыть рамку
        toggle_frame_shortcut = QShortcut(QKeySequence("Ctrl+Shift+K"), self)
        toggle_frame_shortcut.activated.connect(self.toggle_frame)

        # Открыть панель разработчика
        open_dev_tools_shortcut = QShortcut(QKeySequence("Ctrl+Shift+I"), self)
        open_dev_tools_shortcut.activated.connect(self.open_dev_tools)

        # Изменить CSS
        open_edit_css_shortcut = QShortcut(QKeySequence("Ctrl+Shift+С"), self)
        open_edit_css_shortcut.activated.connect(self.show_css_dialog)

        # Перезагрузить страницу
        reload_page_shortcut = QShortcut(QKeySequence("f5"), self)
        reload_page_shortcut.activated.connect(self.do_reload_page)

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

    def show_context_menu(self):
        # Показ контекстного меню
        self.context_menu.exec_(self.menu_button.mapToGlobal(self.menu_button.rect().bottomRight()))

    ### Метод отключен - Используется авторизация по номеру телефона
    def set_cookie(self):
        # Получить cookie можно командой:
        # document.cookie.split('; ').find(row => row.startsWith('auth=')).split('=')[1];
        # Установка cookie для страницы
        cookie_store = self.browser.page().profile().cookieStore()

        cookie = QNetworkCookie()
        cookie.setName(b"auth")
        cookie.setValue(b"pasteCookieValueHere")
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
        self.browser.page().runJavaScript("window.scrollBy(0, 50);") # код для любой страницы
        self.browser.page().runJavaScript("document.querySelector('.ChatBoxBase_list_Kg9et').scrollBy(0, 100);") # этот код для чата бусти

    def toggle_frame(self):
        if self.frame_hidden:
            self.setWindowFlags(Qt.Window)
            self.setWindowOpacity(1)
            self.toggle_frame_action.setText("Скрыть окно (Ctrl+Shift+J)")
        else:
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.setWindowOpacity(1)
            self.toggle_frame_action.setText("Показать окно (Ctrl+Shift+J)")

        self.frame_hidden = not self.frame_hidden
        self.show()

    def toggle_ui(self):
        if self.ui_hidden:
            self.control_panel_widget.show()
            self.toggle_ui_action.setText("Скрыть UI (Ctrl+Shift+K)")
        else:
            self.control_panel_widget.hide()
            self.toggle_ui_action.setText("Показать UI (Ctrl+Shift+K)")

        self.ui_hidden = not self.ui_hidden
        self.show()