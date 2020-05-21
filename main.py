from PyQt5.QtWidgets import *
from database.connection_provider import ConnectionProvider
from search_engine.most_similar_finder import SearchEngine
import sys


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.conn_provider = ConnectionProvider()
        self.search_engine = SearchEngine(self.conn_provider, 100)
        self.title_to_article = dict()
        self.initUI()

    def initialize_new_list(self,):
        self.new_list = QListWidget(self)
        for i, new in enumerate(self.conn_provider.get_all_articles().iterator()):
            self.title_to_article[new.title] = new
            self.new_list.insertItem(i, new.title)
        self.new_list.clicked.connect(
            lambda x: self.display_new_info(
                self.new_list.currentItem().text()))
        return self.new_list

    def display_new_info(self, title):
        new = self.title_to_article[title]
        self.title_tb.setPlainText(new.title)
        #self.class_tb.setPlainText(new.category)
        #self.sent_tb.setPlainText(new.sentiment)
        self.ner_tb.setPlainText(', '.join(new.named_entities))

    def initialize_info_pannel(self):
        self.info_pannel = QGridLayout(self)

        self.info_pannel.addWidget(QLabel('Заголовок новости: '), 0, 0)
        self.title_tb = QPlainTextEdit()
        self.title_tb.setReadOnly(True)
        self.info_pannel.addWidget(self.title_tb, 0, 1)

        self.info_pannel.addWidget(QLabel('Класс новости: '), 1, 0)
        self.class_tb = QTextEdit()
        self.class_tb.setFixedHeight(35)
        self.class_tb.setReadOnly(True)
        self.info_pannel.addWidget(self.class_tb, 1, 1)

        self.info_pannel.addWidget(QLabel('Тональность новости: '), 2, 0)
        self.sent_tb = QTextEdit()
        self.sent_tb.setFixedHeight(35)
        self.sent_tb.setReadOnly(True)
        self.info_pannel.addWidget(self.sent_tb, 2, 1)

        self.info_pannel.addWidget(QLabel('Именованные сущности новости: '), 3, 0)
        self.ner_tb = QPlainTextEdit()
        self.ner_tb.setReadOnly(True)
        self.info_pannel.addWidget(self.ner_tb, 3, 1)

        self.info_pannel.addWidget(QLabel('Наиболее похожие новости: '), 4, 0)
        self.search_button = QPushButton(text='Найти')
        self.search_button.clicked.connect(self.find_most_similar_news)
        self.info_pannel.addWidget(self.search_button, 4, 1)

        return self.info_pannel

    def initialize_search_result(self):
        self.search_result = QListWidget(self)
        self.search_result.clicked.connect(
            lambda x: self.display_new_info(
                self.search_result.currentItem().text()))
        return self.search_result

    def find_most_similar_news(self):
        new = self.title_to_article[self.new_list.currentItem().text()]
        most_sim = self.search_engine.find_match(new.global_id)
        for ident, score in most_sim:
            self.search_result.insertItem(ident, self.conn_provider.get_article(ident).title)

    def initUI(self):
        self.resize(900,700)
        self.setWindowTitle('Sentiment analyzer application')

        grid = QGridLayout(self)
        grid.addWidget(self.initialize_new_list(), 0, 0, 2, 1)
        grid.addLayout(self.initialize_info_pannel(), 0, 1, 1, 1)
        grid.addWidget(self.initialize_search_result(), 1, 1, 1, 1)

        self.show()

#if __name__ == '__main__':
#    app = QApplication(sys.argv)
#    application = App()
#    sys.exit(app.exec_())

if __name__ == '__main__':

    conn_provider = ConnectionProvider()
    conn_provider.build_csv('parsed_articles.csv', '<SEP>')