from PyQt5.QtWidgets import *

import sys

"""

class App(QWidget):

    def __init__(self, IBM_analyzer, azure_client):
        super().__init__()
        self.IBM_analyzer = IBM_analyzer
        self.azure_client = azure_client
        self.initUI()

    def initialize_label(self,):
        self.label = QPlainTextEdit()
        self.label.setReadOnly(True)
        self.label.setFixedWidth(300)
        #self.label.setWordWrap(True)
        return self.label

    def initialize_textbox(self):
        self.textbox = QPlainTextEdit()
        self.textbox.setFixedHeight(350)
        return self.textbox

    def initialize_button(self):
        self.button = QPushButton(text='Analyze')
        self.button.clicked.connect(self.buttonClicked)
        return self.button

    def initialize_engine_selection(self):
        self.ibm_button = QRadioButton("IBM")
        self.azure_button = QRadioButton("MS Azure")
        self.ibm_button.setChecked(True)
        return self.ibm_button, self.azure_button

    def buttonClicked(self):
        text = self.textbox.toPlainText()

        if self.ibm_button.isChecked():
            text_type = detect_type(text)
            if text_type == 'S':
                self.label.setPlainText('IBM engine is analysing your string')
                self.label.repaint()
                result = analyze_string_IBM(text, self.IBM_analyzer)
            else:
                self.label.setPlainText('IBM engine is analysing your url')
                self.label.repaint()
                result = analyze_url_IBM(text, self.IBM_analyzer)

        elif self.azure_button.isChecked():
            self.label.setPlainText('Azure engine is analysing your string')
            self.label.repaint()
            result = analyze_string_azure(text, self.azure_client)

        self.label.setPlainText(json.dumps(result, indent=2))

    def initUI(self):
        self.resize(600,400)
        self.setWindowTitle('Sentiment analyzer application')

        grid = QGridLayout(self)
        grid.addWidget(self.initialize_label(), 0, 0, 1, 1)
        grid.addWidget(self.initialize_textbox(), 0, 1, 1, 1)
        grid.addWidget(self.initialize_button(), 1, 1, 1, 1)

        ibm_b, azure_b = self.initialize_engine_selection()
        layout = QHBoxLayout()
        layout.addWidget(ibm_b)
        layout.addWidget(azure_b)
        grid.addLayout(layout, 1, 0, 1, 1)

        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    application = App(IBM_analyzer, azure_client)
    sys.exit(app.exec_())

"""

if __name__ == '__main__':
    from database.connection_provider import ConnectionProvider

    
    #for art in provider.get_all_articles():
    #    print(art.title)
    #provider.add_article(100, "title", "descr", "link", "provider_name", "1998-11-03 22:22:22")
    #print(provider.get_article(1).ner_title_map)
    #provider.add_article("title", "descr", "link", "provider_name", "1998-11-03 22:22:22")
