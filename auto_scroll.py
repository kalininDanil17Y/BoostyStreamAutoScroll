from PyQt5.QtCore import Qt, QSettings, QTimer, QUrl
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings, QWebEnginePage
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMenu, QShortcut

from dialogs import HelpDialog, CssDialog
from utils import resource_path


class AutoScrollApp(QMainWindow):
    def __init__(self, url=None):
        super().__init__()

        self.dev_tools_window = None
        self.scroll_timer = None
        self.toggle_frame_action = None
        self.toggle_ui_action = None
        self.status_label = None
        self.control_panel = None
        self.context_menu = None
        self.menu_button = None
        self.control_panel_widget = None
        self.settings = None
        self.browser = None
        self.ui_hidden = None
        self.frame_hidden = None
        self.scroll_enabled = None
        
        
        self.init_ui(url)
        self.init_shortcuts()
        self.init_timer()

    def init_ui(self, url):
        self.setWindowTitle("Boosty Chat Auto Scroll")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon(resource_path("resources/app_icon.ico")))

        self.scroll_enabled = False
        self.frame_hidden = False
        self.ui_hidden = False

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        self.browser = QWebEngineView(self)
        self.setup_browser(url)
        main_layout.addWidget(self.browser)

        self.settings = QSettings("BoostyChatAutoScroll", "Settings")

        self.control_panel_widget = QWidget()
        self.setup_control_panel()
        main_layout.addWidget(self.control_panel_widget)

        self.menu_button = QPushButton(self)
        self.menu_button.setIcon(QIcon(resource_path("resources/menu.png")))
        self.menu_button.setFixedSize(30, 30)
        self.menu_button.setCursor(Qt.PointingHandCursor)
        self.menu_button.move(self.width() - 35, self.height() - 32)
        self.menu_button.clicked.connect(self.show_context_menu)

        self.context_menu = QMenu(self)
        self.setup_context_menu()

    def setup_browser(self, url):
        profile = self.browser.page().profile()
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

        if url is None:
            url = "https://boosty.to/hellyeahplay/streams/only-chat"
        self.browser.setUrl(QUrl(url))
        self.browser.loadFinished.connect(self.apply_saved_css)

        settings = self.browser.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebRTCPublicInterfacesOnly, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)

    def setup_control_panel(self):
        self.control_panel = QHBoxLayout(self.control_panel_widget)
        self.control_panel.setContentsMargins(5, 0, 5, 5)

        self.status_label = QPushButton("Scroll: Off", self)
        self.status_label.setFixedSize(70, 25)
        self.status_label.clicked.connect(self.toggle_scroll)
        self.control_panel.addWidget(self.status_label)

        self.control_panel.addStretch()
        self.control_panel_widget.setFixedHeight(30)
        self.control_panel_widget.adjustSize()

    def setup_context_menu(self):
        self.context_menu.addAction("О программе", self.show_help)
        self.context_menu.addAction("Авто прокрутка (Ctrl+Shift+L)", self.toggle_scroll)
        self.context_menu.addSeparator()
        self.context_menu.addAction("Перезагрузить (F5)", self.do_reload_page)
        self.context_menu.addAction("Открыть DevTools (Ctrl+Shift+I)", self.open_dev_tools)
        self.context_menu.addAction("Изменить CSS (Ctrl+Shift+C)", self.show_css_dialog)
        self.context_menu.addSeparator()
        self.toggle_ui_action = self.context_menu.addAction("Скрыть UI (Ctrl+Shift+K)", self.toggle_ui)
        self.toggle_frame_action = self.context_menu.addAction("Скрыть окно (Ctrl+Shift+J)", self.toggle_frame)

        self.context_menu.setStyleSheet("""
            QMenu::separator {
                background: #ffffff;
                height: 1px;
                margin-bottom: 5px;
            }
        """)

    def init_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Shift+L"), self).activated.connect(self.toggle_scroll)
        QShortcut(QKeySequence("Ctrl+Shift+K"), self).activated.connect(self.toggle_frame)
        QShortcut(QKeySequence("Ctrl+Shift+I"), self).activated.connect(self.open_dev_tools)
        QShortcut(QKeySequence("Ctrl+Shift+C"), self).activated.connect(self.show_css_dialog)
        QShortcut(QKeySequence("f5"), self).activated.connect(self.do_reload_page)

    def init_timer(self):
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self.perform_scroll)
        self.dev_tools_window = None

    def resizeEvent(self, event):
        self.menu_button.move(self.width() - 35, self.height() - 32)
        super().resizeEvent(event)

    def do_reload_page(self):
        self.browser.reload()

    def open_dev_tools(self):
        if not self.dev_tools_window or not self.dev_tools_window.isVisible():
            self.dev_tools_window = QWebEngineView()
            dev_page = QWebEnginePage(self.browser.page().profile(), self.dev_tools_window)
            self.dev_tools_window.setPage(dev_page)
            dev_page.setInspectedPage(self.browser.page())
            self.dev_tools_window.setWindowTitle("Developer Tools")
            self.dev_tools_window.resize(800, 600)
            self.dev_tools_window.show()
        else:
            self.dev_tools_window.raise_()
            self.dev_tools_window.activateWindow()

    def show_context_menu(self):
        self.context_menu.exec_(self.menu_button.mapToGlobal(self.menu_button.rect().bottomRight()))

    def apply_saved_css(self):
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
        HelpDialog(self).exec_()

    def show_css_dialog(self):
        CssDialog(self.browser, self).exec_()

    def toggle_scroll(self):
        self.scroll_enabled = not self.scroll_enabled
        self.status_label.setText(f"Scroll: {'On' if self.scroll_enabled else 'Off'}")
        if self.scroll_enabled:
            self.scroll_timer.start(10)
        else:
            self.scroll_timer.stop()

    def perform_scroll(self):
        self.browser.page().runJavaScript("window.scrollBy(0, 50);")
        self.browser.page().runJavaScript("document.querySelector('.ChatBoxBase_list_Kg9et').scrollBy(0, 100);")

    def toggle_frame(self):
        self.frame_hidden = not self.frame_hidden
        self.setWindowFlags(Qt.FramelessWindowHint if self.frame_hidden else Qt.Window)
        self.setWindowOpacity(1)
        self.toggle_frame_action.setText("Показать окно (Ctrl+Shift+J)" if self.frame_hidden else "Скрыть окно (Ctrl+Shift+J)")
        self.show()

    def toggle_ui(self):
        self.ui_hidden = not self.ui_hidden
        if self.ui_hidden:
            self.control_panel_widget.hide()
            self.toggle_ui_action.setText("Показать UI (Ctrl+Shift+K)")
        else:
            self.control_panel_widget.show()
            self.toggle_ui_action.setText("Скрыть UI (Ctrl+Shift+K)")
        self.show()
