from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog, QLabel, QDialogButtonBox, QVBoxLayout, QTextEdit


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("О программе")
        self.setModal(True)
        self.resize(400, 210)

        # Текст помощи
        help_label = QLabel(
            "Программа для отображения чата Boosty.to с поддержкой автоматического скроллинга, специально разработанная для стримера HellYeahPlay. По умолчанию чат Boosty может зависать при большом количестве сообщений и не прокручивается автоматически, что вызывает неудобства для стримера и зрителей. Данное приложение решает эту проблему, обеспечивая авто-скроллинг, а также возможность ручного управления.", self)
        help_label.setWordWrap(True)

        github_link = QLabel('GitHub: <a style="color: #1E90FF;" href="https://github.com/kalininDanil17Y/BoostyStreamAutoScroll">https://github.com/kalininDanil17Y/BoostyStreamAutoScroll</a>')
        github_link.setOpenExternalLinks(True)

        # Кнопка закрытия
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)

        # Размещение элементов
        layout = QVBoxLayout()
        layout.addWidget(help_label)
        layout.addWidget(github_link)
        layout.addWidget(button_box)
        self.setLayout(layout)


class CssDialog(QDialog):
    def __init__(self, browser, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Изменить CSS")
        self.resize(400, 300)
        self.browser = browser

        # Поле для ввода CSS
        self.css_text_edit = QTextEdit(self)
        self.css_text_edit.textChanged.connect(self.live_apply_css)

        # Кнопка применения CSS
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.apply_css)
        button_box.rejected.connect(self.reject)

        # Размещение элементов
        layout = QVBoxLayout()
        layout.addWidget(self.css_text_edit)
        layout.addWidget(button_box)
        self.setLayout(layout)

        # Загрузка текущего CSS из настроек
        self.settings = QSettings("BoostyChatAutoScroll", "Settings")
        self.load_css()

    def live_apply_css(self):
        # Получаем CSS и применяем к странице
        css = self.css_text_edit.toPlainText()
        self.apply_css_to_browser(css)
        self.current_css = css

    def apply_css_to_browser(self, css):
        script = f"""
        var existingStyle = document.getElementById('custom-style');
        if (existingStyle) {{
            existingStyle.innerHTML = `{css}`;
        }} else {{
            var style = document.createElement('style');
            style.type = 'text/css';
            style.id = 'custom-style';
            style.appendChild(document.createTextNode(`{css}`));
            document.head.appendChild(style);
        }}
        """
        self.browser.page().runJavaScript(script)

    def apply_css(self):
        # Сохраняем CSS и закрываем диалог
        self.current_css = self.css_text_edit.toPlainText()
        self.save_css()
        self.accept()

    def load_css(self):
        self.current_css = self.settings.value("css", "")
        self.css_text_edit.setText(self.current_css)

    def save_css(self):
        self.settings.setValue("css", self.current_css)

    def showEvent(self, event):
        # Заполнение текстового поля текущим CSS при открытии диалога
        self.css_text_edit.setText(self.current_css)
        super().showEvent(event)