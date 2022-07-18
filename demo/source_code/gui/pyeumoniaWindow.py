from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from pyeumonia import Covid19
import webbrowser
import time
from os import mkdir, remove
from getpass import getuser
from platform import system
import pickle


# 英文页面，当检测到系统语言为英文时，显示此窗口
class PyeumoniaGui(QMainWindow):
    def __init__(self, parent):
        super(PyeumoniaGui, self).__init__(
            parent, flags=Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Pyeumonia Covid-19 Datas')
        self.setWindowIcon(QIcon('pyeumonia.png'))
        self.setFixedSize(800, 600)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # 使用QTabWidget创建3个标签页，分别为“World Covid Data”、“Country Covid Data”和“About”
        self.tabs = QTabWidget()
        self.world_tab = WorldCovidTab(self)
        self.country_tab = CountryCovidTab(self)
        self.about_tab = AboutTab(self)
        self.tabs.addTab(self.world_tab, 'World Covid Data')
        self.tabs.addTab(self.country_tab, 'Country Covid Data')
        self.tabs.addTab(self.about_tab, 'About')
        # 将三个标签页添加到QMainWindow中
        self.setCentralWidget(self.tabs)


class WorldCovidTab(QTabWidget):
    def __init__(self, parent):
        # 初始化WorldCovidTab类，父窗体为PyeumoniaGui类
        super(WorldCovidTab, self).__init__(parent)
        self.data = self.get_data()
        layout = QFormLayout()
        # 新建一个下拉框，用于选择洲名
        self.continent_combo = QComboBox()
        self.continent_combo.addItems(['World', 'Africa', 'South America', 'North America',
                                       'Asia', 'Europe', 'Oceania', 'Other'])
        # 当下拉框选择值变化时，调用continent_changed()函数
        self.continent_combo.currentIndexChanged.connect(
            self.continent_changed)
        # 新建一个下拉框，用于选择国家名，可选值根据选择的洲名不同而不同
        self.country_combo = QComboBox()
        countries = [country['countryName'] for country in self.data]
        self.country_combo.addItems(countries)
        # 将两个下拉框添加到布局中
        layout.addRow('Continent:', self.continent_combo)
        layout.addRow('Country:', self.country_combo)
        # 新建一个按钮，用于更新数据
        self.update_button = QPushButton('Update')
        self.update_button.clicked.connect(self.update_data)
        # 将按钮添加到布局中
        layout.addRow(self.update_button)
        # 新建一个单选框，用于选择是否实时刷新数据
        self.realtime_check = QCheckBox(
            'Refresh Data Realtime(this may be slow)')
        self.realtime_check.setChecked(False)
        # 将单选框添加到布局中
        layout.addRow(self.realtime_check)
        # 新建一个表格，用于显示数据
        self.table = QTableWidget()
        # 设置表格的列数为国家的数量
        country_count = len(self.data)
        self.table.setRowCount(country_count)
        self.table.setColumnCount(6)
        # 设置表格的行高
        for row in range(country_count):
            self.table.setRowHeight(row, 10)
        # 设置表格的列宽
        for column in range(6):
            self.table.setColumnWidth(column, 110)
        # 禁止表格的编辑功能
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 禁止改变行高和列宽
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        # 将表格添加到布局中
        layout.addRow(self.table)
        # 设置表格的列数为国家的数量
        country_count = len(self.data)
        self.table.setRowCount(country_count)
        index = 0
        # 设置表格的标题
        self.table.setHorizontalHeaderLabels(
            ['Continent', 'Country', 'CurrentConfirmed', 'Confirmed', 'Dead', 'Cured'])
        for country in self.data:
            # 表格对应的字段名为：'continents', 'countryName', 'currentConfirmedCount', 'confirmedCount', 'deadCount',
            # 'curedCount' 将数据添加到表格中
            self.table.setItem(
                index, 0, QTableWidgetItem(country['continents']))
            self.table.setItem(
                index, 1, QTableWidgetItem(country['countryName']))
            self.table.setItem(index, 2, QTableWidgetItem(
                str(country['currentConfirmedCount'])))
            self.table.setItem(index, 3, QTableWidgetItem(
                str(country['confirmedCount'])))
            self.table.setItem(index, 4, QTableWidgetItem(
                str(country['deadCount'])))
            self.table.setItem(index, 5, QTableWidgetItem(
                str(country['curedCount'])))
            index += 1
        # 新建一个标签，用于显示数据获取时间
        self.time_label = QLabel()
        self.time_label.setText(
            'Data updated at: ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        # 将标签添加到布局中
        layout.addRow(self.time_label)
        self.setTabText(0, 'World Covid Data')
        self.setLayout(layout)

    def get_data(self):
        while True:
            try:
                covid = Covid19(auto_update=False, check_upgradable=False)
                self.data = covid.world_covid_data()
            except Exception:
                pass
            else:
                return self.data

    def continent_changed(self):
        # 获取选择的洲名
        continent = self.continent_combo.currentText()
        # 根据洲名获取国家名列表
        countries = [continent] + [country['countryName'] for country in self.data if
                                   country['continents'] == continent]
        # 更新下拉框的可选值
        self.country_combo.clear()
        self.country_combo.addItems(countries)

    def update_data(self):
        # 获取洲名和国家名
        continent_name = self.continent_combo.currentText()
        country_name = self.country_combo.currentText()
        # 判断是否实时刷新数据
        if self.realtime_check.isChecked():
            # 实时刷新数据
            self.data = self.get_data()
            # 更新时间标签
            self.time_label.setText(
                'Data updated at: ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        # 根据洲名和国家名获取数据
        if continent_name == 'World':
            # 设置表格的列数为国家的数量
            country_count = len(self.data)
            self.table.setRowCount(country_count)
            index = 0
            for country in self.data:
                # 表格对应的字段名为：'continents', 'countryName', 'currentConfirmedCount', 'confirmedCount', 'deadCount',
                # 'curedCount' 将数据添加到表格中
                self.table.setItem(
                    index, 0, QTableWidgetItem(country['continents']))
                self.table.setItem(
                    index, 1, QTableWidgetItem(country['countryName']))
                self.table.setItem(index, 2, QTableWidgetItem(
                    str(country['currentConfirmedCount'])))
                self.table.setItem(index, 3, QTableWidgetItem(
                    str(country['confirmedCount'])))
                self.table.setItem(index, 4, QTableWidgetItem(
                    str(country['deadCount'])))
                self.table.setItem(index, 5, QTableWidgetItem(
                    str(country['curedCount'])))
                index += 1
        else:
            # 设置表格的列数为当前洲的国家的数量
            country_count = len(
                [country for country in self.data if country['continents'] == continent_name])
            self.table.setRowCount(country_count)
            index = 0
            for country in self.data:
                # 表格对应的字段名为：'continents', 'countryName', 'currentConfirmedCount', 'confirmedCount', 'deadCount',
                # 'curedCount' 将数据添加到表格中
                if continent_name == country['continents']:
                    self.table.setItem(
                        index, 0, QTableWidgetItem(country['continents']))
                    self.table.setItem(
                        index, 1, QTableWidgetItem(country['countryName']))
                    self.table.setItem(index, 2, QTableWidgetItem(
                        str(country['currentConfirmedCount'])))
                    self.table.setItem(index, 3, QTableWidgetItem(
                        str(country['confirmedCount'])))
                    self.table.setItem(index, 4, QTableWidgetItem(
                        str(country['deadCount'])))
                    self.table.setItem(index, 5, QTableWidgetItem(
                        str(country['curedCount'])))
                    index += 1
        if country_name != continent_name:
            # 设置表格的列数为1
            self.table.setRowCount(1)
            country_info = [
                country for country in self.data if country['countryName'] == country_name][0]
            # 表格对应的字段名为：'continents', 'countryName', 'currentConfirmedCount', 'confirmedCount', 'deadCount',
            # 'curedCount' 将数据添加到表格中
            self.table.setItem(0, 0, QTableWidgetItem(
                country_info['continents']))
            self.table.setItem(0, 1, QTableWidgetItem(
                country_info['countryName']))
            self.table.setItem(0, 2, QTableWidgetItem(
                str(country_info['currentConfirmedCount'])))
            self.table.setItem(0, 3, QTableWidgetItem(
                str(country_info['confirmedCount'])))
            self.table.setItem(0, 4, QTableWidgetItem(
                str(country_info['deadCount'])))
            self.table.setItem(0, 5, QTableWidgetItem(
                str(country_info['curedCount'])))
        self.setTabText(0, 'World Covid Data')


class CountryCovidTab(QTabWidget):
    def __init__(self, parent):
        # 初始化CountryCovidTab类，父窗体为PyeumoniaGui类
        super(CountryCovidTab, self).__init__(parent)
        # 设置窗体布局为垂直布局
        layout = QFormLayout()
        # 创建一个输入框，只允许输入数字，默认值为14
        self.days_input = QLineEdit()
        self.days_input.setValidator(QIntValidator())
        self.days_input.setText('14')
        self.data = self.get_data(days=14)
        # 将输入框添加到布局中，用于获取指定天数前的本地疫情数据
        layout.addRow('Days:', self.days_input)
        # 创建一个按钮，点击后获取指定天数前的本地疫情数据
        self.get_button = QPushButton('Get Data')
        # 将按钮添加到布局中
        layout.addRow(self.get_button)
        # 为按钮绑定点击事件
        self.get_button.clicked.connect(self.update_data)
        # 创建一个标签，用于显示当前所在国家的疫情数据
        self.country_label = QLabel('Country: ' + self.data['countryName'])
        # 将标签添加到布局中
        layout.addRow(self.country_label)
        # 创建一个表格，用于显示疫情数据
        self.table = QTableWidget()
        # 设置表格的列数为5
        self.table.setColumnCount(5)
        # 设置表格的行数为获取的天数 + 1
        self.table.setRowCount(15)
        # 设置表格的行标题为：'Date', 'Confirmed', 'Dead', 'Cured', 'Current'
        self.table.setHorizontalHeaderLabels(
            ['Date', 'currentConfirmed', 'Confirmed', 'Cured', 'Dead'])
        # 设置表格的行高
        for i in range(self.table.rowCount()):
            self.table.setRowHeight(i, 15)
        # 设置表格的列宽
        for i in range(self.table.columnCount()):
            self.table.setColumnWidth(i, 135)
        # 禁止表格的编辑功能
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 禁止改变表格的行高和列宽
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 将数据添加到表格中
        row = 0
        for date in reversed(self.data['data']):
            # 对应字段为：dateId、currentConfirmedCount、confirmedCount、deadCount、curedCount
            # dateId为int类型，原数据格式为：20220101，需要转换为：2020-01-01
            date_id = str(date['dateId'])
            date_id = date_id[:4] + '-' + date_id[4:6] + '-' + date_id[6:]
            self.table.setItem(row, 0, QTableWidgetItem(date_id))
            self.table.setItem(row, 1, QTableWidgetItem(
                str(date['currentConfirmedCount'])))
            self.table.setItem(row, 2, QTableWidgetItem(
                str(date['confirmedCount'])))
            self.table.setItem(
                row, 3, QTableWidgetItem(str(date['curedCount'])))
            self.table.setItem(
                row, 4, QTableWidgetItem(str(date['deadCount'])))
            row += 1
        # 将表格添加到布局中
        layout.addRow(self.table)
        # 新建一个标签，用于显示数据获取时间
        self.time_label = QLabel()
        self.time_label.setText(
            'Data updated at: ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        # 将标签添加到布局中
        layout.addRow(self.time_label)
        # 设置选项卡的标题
        self.setTabText(1, 'Country Covid Data')
        self.setLayout(layout)

    def get_data(self, days: int = 14):
        while True:
            try:
                covid = Covid19(auto_update=False, check_upgradable=False)
                country = covid.get_region(language='en_US')['countryName']
                self.data = covid.country_covid_data(
                    country_name=country, show_timeline=days)
            except Exception:
                continue
            else:
                return self.data

    def update_data(self):
        # 获取输入框中的天数
        days = int(self.days_input.text())
        # 将表格的行数设置为获取的天数 + 1
        self.table.setRowCount(days + 1)
        # 获取数据
        index = 0
        self.data = self.get_data(days)
        # 将数据添加到表格中
        for date in reversed(self.data['data']):
            date_id = str(date['dateId'])
            date_id = date_id[:4] + '-' + date_id[4:6] + '-' + date_id[6:]
            self.table.setItem(index, 0, QTableWidgetItem(date_id))
            self.table.setItem(index, 1, QTableWidgetItem(
                str(date['currentConfirmedCount'])))
            self.table.setItem(index, 2, QTableWidgetItem(
                str(date['confirmedCount'])))
            self.table.setItem(
                index, 3, QTableWidgetItem(str(date['curedCount'])))
            self.table.setItem(
                index, 4, QTableWidgetItem(str(date['deadCount'])))
            index += 1


class AboutTab(QTabWidget):
    def __init__(self, parent):
        # 初始化AboutTab类，父窗体为PyeumoniaGui类
        super(AboutTab, self).__init__(parent)
        # 设置窗体布局为垂直布局
        layout = QFormLayout()
        # 新建一个多行文本框，用于显示关于信息
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setText(
            'Pyeumonia is a simple tool to monitor the COVID-19 in the world.\n'
            'All the data is from DXY.\n'
            '\n'
            'Pyeumonia is developed by @Pyeumonia.\n'
            '\n'
            'If you have any questions, please contact me at: pyeumonia@protonmail.com or submit an Issue on my GitHub.\n'
            '\n'
            'Copyleft @ Pyeumonia This  software is opensource using  GNU GPL V3.\n'
            '\n'
            'Pyeumonia is a free and open source software, you can use'
            ' and edit it freely, but cannot use it for commercial use. Including'
            ' but not limited: Advertising, Sailing and closed source.\n'
            '\n'
            'If you don\'t agree with the above, please don\'t use this software.'
        )
        # 将多行文本框添加到布局中
        layout.addRow(self.text_edit)
        # 新建一个按钮，用于打开Pyeumonia的GitHub项目
        self.github_button = QPushButton('Open Pyeumonia on GitHub')
        self.github_button.clicked.connect(lambda: webbrowser.open(
            'https://github.com/pyeumonia/pyeumonia'))
        # 将按钮添加到布局中
        layout.addRow(self.github_button)
        # 新建一个按钮，用于打开数据源链接
        self.data_source_button = QPushButton('Open DXY Website')
        self.data_source_button.clicked.connect(lambda: webbrowser.open(
            'https://ncov.dxy.cn/ncovh5/view/en_pneumonia'))
        # 将按钮添加到布局中
        layout.addRow(self.data_source_button)
        # 新建一个按钮，点击后用于发送邮件
        self.email_button = QPushButton('Contact Me')
        self.email_button.clicked.connect(
            lambda: webbrowser.open('mailto:pyeumonia@protonmail.com'))
        # 将按钮添加到布局中
        layout.addRow(self.email_button)
        # 新建一个按钮，点击后显示开源许可证
        self.license_button = QPushButton('Open Source License')
        self.license_button.clicked.connect(lambda: webbrowser.open(
            'https://www.gnu.org/licenses/gpl-3.0.en.html'))
        # 将按钮添加到布局中
        layout.addRow(self.license_button)
        # 新建一个按钮，点击后更改语言为中文
        self.change_language_button = QPushButton('更改语言/Change Language')
        # 为按钮绑定一个函数，用于更改语言
        self.change_language_button.clicked.connect(self.change_language)
        # 将按钮添加到布局中
        layout.addRow(self.change_language_button)
        # 设置选项卡的标题
        self.setTabText(5, 'About')
        self.setLayout(layout)

    def change_language(self):
        confirm = QMessageBox.question(
            self, '更改语言/Change Language', '确定要将语言更改为中文吗？\nAre you really want to change language to Chinese? ', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.No:
            return
        language_dir = ''
        if system() == 'Windows':
            language_dir = f'C:/Users/{getuser()}/AppData/Local/pyeumonia/'
        elif system() == 'Linux':
            language_dir = f'/home/{getuser()}/.local/share/pyeumonia/'
        elif system() == 'Darwin':
            language_dir = f'/Users/{getuser()}/Library/Application Support/pyeumonia/'
        try:
            mkdir(language_dir)
        except FileExistsError:
            pass
        try:
            remove(language_dir + 'language.pkl')
        except FileNotFoundError:
            pass
        with open(language_dir + 'language.pkl', 'wb') as f:
            pickle.dump('zh_CN', f)
        # 弹窗提示用户语言已更改，请手动打开程序
        QMessageBox.information(
            self, '语言已更改', '语言已更改为中文，请手动重启应用程序。', QMessageBox.Ok)
        # 重新启动程序
        QApplication.instance().quit()
