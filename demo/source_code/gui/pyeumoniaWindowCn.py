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


# 中文界面，当检测到系统语言为中文时，显示此窗口
class PyeumoniaGuiCn(QMainWindow):
    def __init__(self, parent):
        super(PyeumoniaGuiCn, self).__init__(
            parent, flags=Qt.WindowStaysOnTopHint)
        self.setWindowTitle('Pyeumonia 疫情数据查询系统')
        self.setWindowIcon(QIcon('pyeumonia.png'))
        self.setFixedSize(800, 600)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # 新建一个QTabWidget，用于创建标签页，分别为“全球疫情数据”、“国家疫情数据”、”中国疫情数据“、”国内风险地区“和“关于”
        self.tabs = QTabWidget()
        self.world_tab = WorldCovidTab(self)
        self.country_tab = CountryCovidTab(self)
        self.china_tab = ChinaCovidTab(self)
        self.danger_areas_tab = DangerAreasTab(self)
        self.about_tab = AboutTab(self)
        self.tabs.addTab(self.world_tab, '全球疫情数据')
        self.tabs.addTab(self.country_tab, '国家疫情数据')
        self.tabs.addTab(self.china_tab, '中国疫情数据')
        self.tabs.addTab(self.danger_areas_tab, '国内风险地区')
        self.tabs.addTab(self.about_tab, '关于')
        self.setCentralWidget(self.tabs)


class WorldCovidTab(QTabWidget):
    def __init__(self, parent):
        # 初始化WorldCovidTab类，父窗体为PyeumoniaGui类
        super(WorldCovidTab, self).__init__(parent)
        self.data = self.get_data()
        layout = QFormLayout()
        # 新建一个下拉框，用于选择洲名
        self.continent_combo = QComboBox()
        self.continent_combo.addItems(['全球', '非洲', '南美洲', '北美洲',
                                       '亚洲', '欧洲', '大洋洲', '其他'])
        # 当下拉框选择值变化时，调用continent_changed()函数
        self.continent_combo.currentIndexChanged.connect(
            self.continent_changed)
        # 新建一个下拉框，用于选择国家名，可选值根据选择的洲名不同而不同
        self.country_combo = QComboBox()
        countries = [country['countryName'] for country in self.data]
        self.country_combo.addItems(countries)
        # 将两个下拉框添加到布局中
        layout.addRow('请选择洲:', self.continent_combo)
        layout.addRow('请选择国家:', self.country_combo)
        # 新建一个按钮，用于更新数据
        self.update_button = QPushButton('查询')
        self.update_button.clicked.connect(self.update_data)
        # 将按钮添加到布局中
        layout.addRow(self.update_button)
        # 新建一个单选框，用于选择是否实时刷新数据
        self.realtime_check = QCheckBox('实时更新数据(这可能会导致获取数据延迟)')
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
            ['洲', '国家', '现存确诊', '累计确诊', '累计死亡', '累计治愈'])
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
            '数据更新时间: ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        # 将标签添加到布局中
        layout.addRow(self.time_label)
        self.setTabText(0, '全球疫情数据')
        self.setLayout(layout)

    def get_data(self):
        while True:
            try:
                covid = Covid19(auto_update=False,
                                check_upgradable=False, language='zh_CN')
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
                '数据更新时间: ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
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
        self.setTabText(0, '全球疫情数据')


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
        layout.addRow('请输入要获取的天数:', self.days_input)
        # 创建一个按钮，点击后获取指定天数前的本地疫情数据
        self.get_button = QPushButton('获取数据')
        # 将按钮添加到布局中
        layout.addRow(self.get_button)
        # 为按钮绑定点击事件
        self.get_button.clicked.connect(self.update_data)
        # 创建一个标签，用于显示当前所在国家的疫情数据
        self.country_label = QLabel('当前所在国家: ' + self.data['countryName'])
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
            ['日期', '现存确诊', '累计确诊', '累计治愈', '累计死亡'])
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
            '数据更新时间: ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        # 将标签添加到布局中
        layout.addRow(self.time_label)
        # 设置选项卡的标题
        self.setTabText(1, '国家疫情数据')
        self.setLayout(layout)

    def get_data(self, days: int = 14):
        while True:
            try:
                covid = Covid19(auto_update=False,
                                check_upgradable=False, language='zh_CN')
                country = covid.get_region(language='zh_CN')['countryName']
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
        # 更新底部标签的时间
        self.time_label.setText(
            '数据更新时间: ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
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


class ChinaCovidTab(QTabWidget):
    def __init__(self, parent):
        # 初始化ChinaCovidTab类，父窗体为PyeumoniaGui类
        super(ChinaCovidTab, self).__init__(parent)
        # 设置窗体布局为垂直布局
        layout = QFormLayout()
        self.data = self.get_data()
        # 新建一个下拉框，用于显示省份名称
        self.province_combo = QComboBox()
        self.province_combo.addItems(
            [
                '全国', '台湾', '香港', '澳门', '广东', '上海', '安徽', '甘肃', '福建',
                '天津', '江苏', '海南', '山东', '浙江', '四川', '北京', '重庆', '江西',
                '河南', '云南', '陕西', '辽宁', '湖南', '湖北', '山西', '青海', '河北',
                '广西', '新疆', '贵州', '宁夏', '西藏', '吉林', '黑龙江', '内蒙古'
            ]
        )
        # 当下拉框的值改变时，触发province_changed函数
        self.province_combo.currentIndexChanged.connect(self.province_changed)
        # 将下拉框添加到布局中
        layout.addRow('请选择省份: ', self.province_combo)
        # 新建一个下拉框，用于显示城市名称，当下拉框的值改变时，自动更新城市下拉框的值
        self.city_combo = QComboBox()
        self.city_combo.addItem('全部')
        for province in self.data:
            for city in province['cities']:
                self.city_combo.addItem(city['cityName'])
        # 将下拉框添加到布局中
        layout.addRow('请选择城市: ', self.city_combo)
        # 新建一个复选框，用于显示是否实时更新数据
        self.realtime_check = QCheckBox('实时更新数据(这可能会导致获取数据延迟)')
        self.realtime_check.setChecked(False)
        # 将复选框添加到布局中
        layout.addRow(self.realtime_check)
        # 新建一个按钮，用于获取数据，当按钮被点击时，出发update_data函数
        self.update_button = QPushButton('更新数据')
        self.update_button.clicked.connect(self.update_data)
        # 将按钮添加到布局中
        layout.addRow(self.update_button)
        # 新建一个表格，用于显示数据
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        # 设置表格的表头
        self.table.setHorizontalHeaderLabels(
            ['省份', '城市', '现存确诊', '累计确诊', '累计治愈', '累计死亡'])
        # 设置表格的行高为15
        for i in range(self.table.rowCount()):
            self.table.setRowHeight(i, 15)
        # 设置表格的列宽为100
        for i in range(self.table.columnCount()):
            self.table.setColumnWidth(i, 100)
        # 禁止表格的编辑功能
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 禁止更改行高和列宽
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        # 设置表格的行数为全国所有城市的数量，即city_combo的菜单数量 -1，列数为6
        self.table.setRowCount(self.city_combo.count() - 1)
        # 将数据显示到表格中
        index = 0
        for province in self.data:
            for city in province['cities']:
                self.table.setItem(index, 0, QTableWidgetItem(
                    province['provinceShortName']))
                self.table.setItem(
                    index, 1, QTableWidgetItem(city['cityName']))
                self.table.setItem(index, 2, QTableWidgetItem(
                    str(city['currentConfirmedCount'])))
                self.table.setItem(index, 3, QTableWidgetItem(
                    str(city['confirmedCount'])))
                self.table.setItem(
                    index, 4, QTableWidgetItem(str(city['curedCount'])))
                self.table.setItem(
                    index, 5, QTableWidgetItem(str(city['deadCount'])))
                index += 1
        # 将表格添加到布局中
        layout.addRow(self.table)
        # 显示更新时间
        self.update_time = QLabel(
            '数据更新时间: ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        layout.addRow(self.update_time)
        self.setTabText(2, '中国疫情数据')
        self.setLayout(layout)

    def get_data(self):
        while True:
            try:
                covid = Covid19(auto_update=False,
                                check_upgradable=False, language='zh_CN')
                self.data = covid.cn_covid_data(include_cities=True)
            except Exception:
                continue
            else:
                return self.data

    def province_changed(self):
        cities_combo = ['全部']
        for province in self.data:
            # 如果下拉框的值与数据中的省份名称相同，则将城市下拉框的值设置为该省份的城市名称
            if province['provinceShortName'] in ['香港', '澳门', '台湾']:
                cities_combo = ['全部']
            else:
                if province['provinceShortName'] == self.province_combo.currentText():
                    for city in province['cities']:
                        cities_combo.append(city['cityName'])
                elif self.province_combo.currentText() == '全国':
                    for province_ in self.data:
                        for city in province_['cities']:
                            cities_combo.append(city['cityName'])
        self.city_combo.clear()
        self.city_combo.addItems(cities_combo)

    def update_data(self):
        # 判断是否实时更新数据
        if self.realtime_check.isChecked():
            self.data = self.get_data()
            # 更新时间
            self.update_time.setText(
                '数据更新时间: ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        # 获取省份和城市下拉框的值
        province_name = self.province_combo.currentText()
        city_name = self.city_combo.currentText()
        # 如果省份和城市下拉框的值为全部，则显示全国所有城市的数据
        if province_name == '全部' and city_name == '全部':
            # 设置表格的行数为全国所有城市的数量，即city_combo的菜单数量 -1，列数为6
            self.table.setRowCount(self.city_combo.count() - 1)
            # 将数据显示到表格中
            index = 0
            for province in self.data:
                for city in province['cities']:
                    self.table.setItem(index, 0, QTableWidgetItem(
                        province['provinceShortName']))
                    self.table.setItem(
                        index, 1, QTableWidgetItem(city['cityName']))
                    self.table.setItem(index, 2, QTableWidgetItem(
                        str(city['currentConfirmedCount'])))
                    self.table.setItem(index, 3, QTableWidgetItem(
                        str(city['confirmedCount'])))
                    self.table.setItem(
                        index, 4, QTableWidgetItem(str(city['curedCount'])))
                    self.table.setItem(
                        index, 5, QTableWidgetItem(str(city['deadCount'])))
                    index += 1
        # 如果省份下拉框的值不为全部，但是城市下拉框的值为全部，则显示该省份所有城市的数据
        elif province_name != '全部' and city_name == '全部':
            # 设置表格的行数为该省份所有城市的数量，即city_combo的菜单数量 -1，列数为6
            if province_name in ['香港', '澳门', '台湾']:
                self.table.setRowCount(1)
            else:
                self.table.setRowCount(self.city_combo.count() - 1)
            # 将数据显示到表格中
            index = 0
            for province in self.data:
                if province['provinceShortName'] != province_name:
                    continue
                for city in province['cities']:
                    self.table.setItem(
                        index, 0, QTableWidgetItem(province_name))
                    self.table.setItem(
                        index, 1, QTableWidgetItem(city['cityName']))
                    self.table.setItem(index, 2, QTableWidgetItem(
                        str(city['currentConfirmedCount'])))
                    self.table.setItem(index, 3, QTableWidgetItem(
                        str(city['confirmedCount'])))
                    self.table.setItem(
                        index, 4, QTableWidgetItem(str(city['curedCount'])))
                    self.table.setItem(
                        index, 5, QTableWidgetItem(str(city['deadCount'])))
                    index += 1
        # 如果城市下拉框的值不为全部，则显示该省份该城市的数据
        elif city_name != '全部':
            # 设置表格的行数为1，列数为6
            self.table.setRowCount(1)
            # 将数据显示到表格中
            for province in self.data:
                if province['provinceShortName'] != province_name:
                    continue
                for city in province['cities']:
                    if city_name != city['cityName']:
                        continue
                    self.table.setItem(0, 0, QTableWidgetItem(province_name))
                    self.table.setItem(0, 1, QTableWidgetItem(city_name))
                    self.table.setItem(0, 2, QTableWidgetItem(
                        str(city['currentConfirmedCount'])))
                    self.table.setItem(0, 3, QTableWidgetItem(
                        str(city['confirmedCount'])))
                    self.table.setItem(
                        0, 4, QTableWidgetItem(str(city['curedCount'])))
                    self.table.setItem(
                        0, 5, QTableWidgetItem(str(city['deadCount'])))


class DangerAreasTab(QTabWidget):
    def __init__(self, parent):
        super(DangerAreasTab, self).__init__(parent)
        self.data = self.get_data()
        layout = QFormLayout()
        # 新建一个标签，提示用户选择省份
        self.province_label = QLabel('请选择省份:')
        # 新建一个下拉框，用于选择省份（只有存在风险地区的省份才会显示）
        self.province_combo = QComboBox()
        self.province_combo.addItems(['全部'])
        # 新建一个标签，提示用户选择城市
        self.city_label = QLabel('请选择城市:')
        # 新建一个下拉框，用于选择城市（只有存在风险地区的城市才会显示）
        self.city_combo = QComboBox()
        self.city_combo.addItems(['全部'])
        # 将下拉框添加到布局中
        province_layout = QVBoxLayout()
        province_layout.addWidget(self.province_label, alignment=Qt.AlignTop)
        province_layout.addWidget(self.province_combo, alignment=Qt.AlignTop)
        city_layout = QVBoxLayout()
        city_layout.addWidget(self.city_label, alignment=Qt.AlignTop)
        city_layout.addWidget(self.city_combo, alignment=Qt.AlignTop)
        combo_layout = QHBoxLayout()
        combo_layout.addLayout(province_layout)
        combo_layout.addLayout(city_layout)
        # 将标签和下拉框添加到布局中
        layout.addRow(combo_layout)
        # 新建一个按钮，用于获取数据
        self.get_data_button = QPushButton('获取数据')
        # 新建一个按钮，用于获取当地的风险地区
        self.get_locale_button = QPushButton('获取当地的风险地区')
        # 为按钮添加快捷键
        self.get_locale_button.setShortcut('Shift+L')
        layout.addRow(self.get_data_button)
        layout.addRow(self.get_locale_button)
        # 新建一个标签，用于显示高风险地区数量
        self.high_danger_label = QLabel('高风险地区数量: 0')
        layout.addRow(self.high_danger_label)
        # 新建一个多行文本框，用于显示高风险地区的信息
        self.high_danger_text = QTextEdit()
        self.high_danger_text.setReadOnly(True)
        layout.addRow(self.high_danger_text)
        # 新建一个标签，用于显示中风险地区数量
        self.mid_danger_label = QLabel('中风险地区数量: 0')
        layout.addRow(self.mid_danger_label)
        # 新建一个多行文本框，用于显示中风险地区的信息
        self.mid_danger_text = QTextEdit()
        self.mid_danger_text.setReadOnly(True)
        layout.addRow(self.mid_danger_text)
        # 新建一个标签，用于显示数据更新时间
        self.update_time_label = QLabel(
            '数据更新时间: ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        layout.addRow(self.update_time_label)
        for province in self.data:
            self.province_combo.addItem(province['provinceName'])
            for city in province['cities']:
                self.city_combo.addItem(city['cityName'])
        # 当省份改变时，触发province_changed函数
        self.province_combo.currentIndexChanged.connect(self.province_changed)
        # 当按钮被点击时，触发update_data函数
        self.get_data_button.clicked.connect(self.update_data)
        # 当按钮被点击时，触发get_locale_data函数
        self.get_locale_button.clicked.connect(self.get_locale_data)
        self.setLayout(layout)
        self.setTabText(3, '国内风险地区')

    def get_data(self, city_name=None):
        while True:
            try:
                covid = Covid19(check_upgradable=False)
                self.data = covid.danger_areas_data(city_name=city_name)
            except Exception:
                time.sleep(1)
            else:
                return self.data

    def province_changed(self):
        province_name = self.province_combo.currentText()
        self.city_combo.clear()
        self.city_combo.addItems(['全部'])
        if province_name == '全部':
            for province in self.data:
                for city in province['cities']:
                    self.city_combo.addItem(city['cityName'])
        else:
            for province in self.data:
                if province['provinceName'] == province_name:
                    for city in province['cities']:
                        self.city_combo.addItem(city['cityName'])
                    break

    def get_locale_data(self):
        # 无视实时更新和省份城市的选择，直接获取当地的风险地区
        locale = Covid19(check_upgradable=False).get_region(language='zh_CN')
        data = self.get_data(city_name='auto')
        # 再次发送请求，防止接下来的操作发生错误
        self.data = self.get_data()
        # 更新标签的文本
        self.update_time_label.setText(
            '数据更新时间: ' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        locale_province = locale['provinceName']
        locale_city = locale['cityName']
        # 如果data是列表，则表示当地无中高风险地区，程序获取的是全国的风险地区，如果data是字典，则表示当地有中高风险地区，程序获取的是当地的风险地区
        if isinstance(data, list):
            self.high_danger_label.setText(
                locale_province + locale_city + '没有高风险地区')
            self.high_danger_text.setText('')
            self.mid_danger_label.setText(
                locale_province + locale_city + '没有中风险地区')
            self.mid_danger_text.setText('')
        else:
            high_danger_count = 0
            high_danger_areas = []
            mid_danger_count = 0
            mid_danger_areas = []
            include_high_danger = False
            include_mid_danger = False
            # 判断当地是否有高风险地区，如果抛出KeyError，则表示当地没有高风险地区
            try:
                high_danger_count = data['highDangerCount']
                high_danger_areas = data['highDangerAreas']
            except KeyError:
                pass
            else:
                include_high_danger = True
            # 判断当地是否有中风险地区，如果抛出KeyError，则表示当地没有中风险地区
            try:
                mid_danger_count = data['midDangerCount']
                mid_danger_areas = data['midDangerAreas']
            except KeyError:
                pass
            else:
                include_mid_danger = True
            warning_text = '系统检测到您的所在地' + locale_province + locale_city + '有'
            if include_high_danger:
                warning_text = warning_text + str(
                    high_danger_count) + '个高风险地区和' if include_mid_danger else warning_text + str(
                    high_danger_count) + '个高风险地区!'
                self.high_danger_label.setText(
                    locale_province + locale_city + '有' + str(high_danger_count) + '个高风险地区')
                self.high_danger_text.setText('\n'.join(high_danger_areas))
            else:
                self.high_danger_label.setText(
                    locale_province + locale_city + '没有高风险地区')
            if include_mid_danger:
                warning_text = warning_text + str(mid_danger_count) + '个中风险地区'
                self.mid_danger_label.setText(
                    locale_province + locale_city + '有' + str(mid_danger_count) + '个中风险地区!')
                self.mid_danger_text.setText('\n'.join(mid_danger_areas))
            else:
                self.mid_danger_label.setText(
                    locale_province + locale_city + '没有中风险地区')
            if include_high_danger or include_mid_danger:
                QMessageBox.warning(
                    self, '注意防护', warning_text, QMessageBox.Yes)

    def get_location(self) -> dict:
        while True:
            try:
                covid = Covid19(check_upgradable=False)
                location = covid.get_region(language='zh_CN')
            except Exception:
                continue
            else:
                return location

    def update_data(self):
        province_name = self.province_combo.currentText()
        city_name = self.city_combo.currentText()
        if province_name == '全部' and city_name == '全部':
            high_danger_count = 0
            mid_danger_count = 0
            high_danger_areas = []
            mid_danger_areas = []
            for province in self.data:
                for city in province['cities']:
                    try:
                        high_danger_count += city['highDangerCount']
                    except KeyError:
                        pass
                    else:
                        high_areas = city['highDangerAreas']
                        high_danger_areas += [province['provinceName'] + city['cityName'] + high_areas[index] for index
                                              in range(len(high_areas))]
                    try:
                        mid_danger_count += city['midDangerCount']
                    except KeyError:
                        pass
                    else:
                        mid_areas = city['midDangerAreas']
                        mid_danger_areas += [province['provinceName'] + city['cityName'] + mid_areas[index] for index
                                             in range(len(mid_areas))]
            self.high_danger_label.setText(
                '全国高风险地区数量: ' + str(high_danger_count))
            self.high_danger_text.setText('\n'.join(high_danger_areas))
            self.mid_danger_label.setText(
                '全国中风险地区数量: ' + str(mid_danger_count))
            self.mid_danger_text.setText('\n'.join(mid_danger_areas))
        elif city_name == '全部' and province_name != '全部':
            high_danger_count = 0
            mid_danger_count = 0
            high_danger_areas = []
            mid_danger_areas = []
            for province in self.data:
                if province_name != province['provinceName']:
                    continue
                for city in province['cities']:
                    try:
                        high_danger_count += city['highDangerCount']
                    except KeyError:
                        pass
                    else:
                        high_areas = city['highDangerAreas']
                        high_danger_areas += [province['provinceName'] + city['cityName'] + high_areas[index] for index
                                              in range(len(high_areas))]
                    try:
                        mid_danger_count += city['midDangerCount']
                    except KeyError:
                        pass
                    else:
                        mid_areas = city['midDangerAreas']
                        mid_danger_areas += [province['provinceName'] + city['cityName'] + mid_areas[index] for index
                                             in range(len(mid_areas))]
                self.high_danger_label.setText(
                    province_name + '高风险地区数量: ' + str(high_danger_count))
                self.high_danger_text.setText('\n'.join(high_danger_areas))
                self.mid_danger_label.setText(
                    province_name + '中风险地区数量: ' + str(mid_danger_count))
                self.mid_danger_text.setText('\n'.join(mid_danger_areas))
        else:
            high_danger_count = 0
            mid_danger_count = 0
            high_danger_areas = []
            mid_danger_areas = []
            for province in self.data:
                if province_name != province['provinceName']:
                    continue
                for city in province['cities']:
                    if city_name != city['cityName']:
                        continue
                    try:
                        high_danger_count += city['highDangerCount']
                    except KeyError:
                        pass
                    else:
                        high_areas = city['highDangerAreas']
                        high_danger_areas += [province['provinceName'] + city['cityName'] + high_areas[index] for index
                                              in range(len(high_areas))]
                    try:
                        mid_danger_count += city['midDangerCount']
                    except KeyError:
                        pass
                    else:
                        mid_areas = city['midDangerAreas']
                        mid_danger_areas += [province['provinceName'] + city['cityName'] + mid_areas[index] for index
                                             in range(len(mid_areas))]
                self.high_danger_label.setText(
                    province_name + city_name + '高风险地区数量: ' + str(high_danger_count))
                self.high_danger_text.setText('\n'.join(high_danger_areas))
                self.mid_danger_label.setText(
                    province_name + city_name + '中风险地区数量: ' + str(mid_danger_count))
                self.mid_danger_text.setText('\n'.join(mid_danger_areas))


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
            'Pyeumonia是一个强大的工具，可以查看全球的疫情数据。\n'
            '所有数据都是来自丁香医生官网。\n'
            '\n'
            'Pyeumonia开发者：@Pyeumonia.\n'
            '\n'
            '如果你有任何问题，请通过电子邮件联系我：pyeumonia@protonmail.com，也可以在我的GitHub上面提交Issues。\n'
            '\n'
            '本程序使用GNU GPL V3协议开源\n'
            '\n'
            'Pyeumonia是一个免费、开源的软件，你可以自由的使用以及修改软件源码，'
            '但是禁止将软件用于商业用途，包括但不限于广告、售卖或者是闭源发布！\n'
            '\n'
            '如果你不遵循以上条款，请停止使用Pyeumonia。\n'
        )
        # 将多行文本框添加到布局中
        layout.addRow(self.text_edit)
        # 新建一个按钮，用于打开Pyeumonia的GitHub项目
        self.github_button = QPushButton('我的GitHub项目')
        self.github_button.clicked.connect(lambda: webbrowser.open(
            'https://github.com/pyeumonia/pyeumonia'))
        # 将按钮添加到布局中
        layout.addRow(self.github_button)
        # 新建一个按钮，用于打开数据源链接
        self.data_source_button = QPushButton('打开丁香园数据源链接')
        self.data_source_button.clicked.connect(
            lambda: webbrowser.open('https://ncov.dxy.cn/ncovh5/view/pneumonia'))
        # 将按钮添加到布局中
        layout.addRow(self.data_source_button)
        # 新建一个按钮，点击后用于发送邮件
        self.email_button = QPushButton('联系我')
        self.email_button.clicked.connect(
            lambda: webbrowser.open('mailto:pyeumonia@protonmail.com'))
        # 将按钮添加到布局中
        layout.addRow(self.email_button)
        # 新建一个按钮，点击后显示开源许可证
        self.license_button = QPushButton('开源许可证')
        self.license_button.clicked.connect(lambda: webbrowser.open(
            'https://jxself.org/translations/gpl-3.zh.shtml'))
        # 将按钮添加到布局中
        layout.addRow(self.license_button)
        # 新建一个按钮，点击后重新启动程序，并更改语言为英文
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
            self, '更改语言/Change Language', '确定要将语言更改为英文吗？\nAre you really want to change language to English? ', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
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
            pickle.dump('en_US', f)
        # 弹窗提示用户语言已更改，请手动打开程序
        QMessageBox.information(
            self, 'Language Changed', 'Language has been changed to English, please restart the program manually.', QMessageBox.Ok)
        # 重新启动程序
        QApplication.instance().quit()
