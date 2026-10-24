
#
# DP832 GUI - 现代化界面重构版
# 每个通道以卡片形式呈现：大字体电压/电流 + 功率曲线历程
# 右侧 “+” 按钮可增加通道列（默认 1 列，最多 3 列）
#

import sys

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

try:
	import pyqtgraph as pg
except ImportError:
	print("Install pyqtgraph: pip install pyqtgraph")
	raise

from dp832 import DP832


# ----------------------------------------------------------------------------
# 主题配色
# ----------------------------------------------------------------------------
COLOR_BG        = "#171923"   # 窗口背景
COLOR_CARD      = "#21242f"   # 卡片背景
COLOR_CARD_ALT  = "#272b38"   # 卡片内分区背景
COLOR_BORDER    = "#33384a"   # 边框
COLOR_TEXT      = "#e6e8ef"   # 主文字
COLOR_SUBTLE    = "#8b90a3"   # 次要文字
COLOR_ACCENT    = "#5b8cff"   # 强调色（蓝）
COLOR_VOLTAGE   = "#ffb454"   # 电压（琥珀）
COLOR_CURRENT   = "#43d9a3"   # 电流（青绿）
COLOR_POWER     = "#7aa2ff"   # 功率曲线（蓝）
COLOR_ON        = "#43d97f"   # 输出开启（绿）
COLOR_OFF       = "#ff6b6b"   # 输出关闭（红）

FONT_NUM = "Consolas,'Cascadia Mono','Courier New',monospace"

MAX_COLUMNS = 3


def build_stylesheet():
	"""返回全局 QSS 样式表"""
	return f"""
	QMainWindow, QWidget {{
		background-color: {COLOR_BG};
		color: {COLOR_TEXT};
		font-family: 'Segoe UI','Microsoft YaHei',sans-serif;
		font-size: 14px;
	}}

	/* 顶部工具栏 */
	QFrame#topBar {{
		background-color: {COLOR_CARD};
		border-bottom: 1px solid {COLOR_BORDER};
	}}
	QLabel#appTitle {{
		font-size: 18px;
		font-weight: 700;
		color: {COLOR_TEXT};
	}}
	QLabel#appSub {{
		font-size: 11px;
		color: {COLOR_SUBTLE};
	}}

	/* 输入框 */
	QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
		background-color: {COLOR_CARD_ALT};
		border: 1px solid {COLOR_BORDER};
		border-radius: 6px;
		padding: 5px 8px;
		color: {COLOR_TEXT};
		selection-background-color: {COLOR_ACCENT};
	}}
	QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
		border: 1px solid {COLOR_ACCENT};
	}}
	QDoubleSpinBox::up-button, QDoubleSpinBox::down-button,
	QSpinBox::up-button, QSpinBox::down-button {{
		width: 14px;
		background: {COLOR_CARD};
		border: none;
	}}
	/* 设定区应用按钮 */
	QPushButton#applyBtn {{
		background-color: {COLOR_ACCENT};
		border: none;
		border-radius: 6px;
		padding: 5px 12px;
		font-weight: 600;
		color: #ffffff;
	}}
	QPushButton#applyBtn:hover {{ background-color: #6f9bff; }}
	QLabel#setCaption {{
		font-size: 12px;
		color: {COLOR_SUBTLE};
	}}
	QComboBox::drop-down {{ border: none; width: 20px; }}
	QComboBox QAbstractItemView {{
		background-color: {COLOR_CARD_ALT};
		border: 1px solid {COLOR_BORDER};
		color: {COLOR_TEXT};
		selection-background-color: {COLOR_ACCENT};
	}}

	/* 普通按钮 */
	QPushButton {{
		background-color: {COLOR_CARD_ALT};
		border: 1px solid {COLOR_BORDER};
		border-radius: 6px;
		padding: 6px 14px;
		color: {COLOR_TEXT};
	}}
	QPushButton:hover {{ border: 1px solid {COLOR_ACCENT}; }}
	QPushButton:pressed {{ background-color: {COLOR_BORDER}; }}
	QPushButton#connectBtn {{
		background-color: {COLOR_ACCENT};
		border: none;
		font-weight: 600;
		color: #ffffff;
	}}
	QPushButton#connectBtn:hover {{ background-color: #6f9bff; }}
	QPushButton:disabled {{ color: {COLOR_SUBTLE}; }}

	/* 右侧加号按钮 */
	QPushButton#addBtn {{
		background-color: {COLOR_ACCENT};
		border: none;
		border-radius: 18px;
		min-width: 36px; max-width: 36px;
		min-height: 36px; max-height: 36px;
		font-size: 24px;
		font-weight: 700;
		color: #ffffff;
	}}
	QPushButton#addBtn:hover {{ background-color: #6f9bff; }}
	QPushButton#addBtn:disabled {{
		background-color: {COLOR_BORDER};
		color: {COLOR_SUBTLE};
	}}

	/* 通道卡片 */
	QFrame#channelCard {{
		background-color: {COLOR_CARD};
		border: 1px solid {COLOR_BORDER};
		border-radius: 14px;
	}}
	QLabel#cardTitle {{
		font-size: 16px;
		font-weight: 700;
		color: {COLOR_TEXT};
	}}
	QLabel#metricCaption {{
		font-size: 11px;
		font-weight: 600;
		letter-spacing: 2px;
		color: {COLOR_SUBTLE};
	}}
	QLabel#voltValue {{
		font-family: {FONT_NUM};
		font-size: 46px;
		font-weight: 700;
		color: {COLOR_VOLTAGE};
	}}
	QLabel#currValue {{
		font-family: {FONT_NUM};
		font-size: 46px;
		font-weight: 700;
		color: {COLOR_CURRENT};
	}}
	QLabel#unitLabel {{
		font-size: 20px;
		font-weight: 600;
		color: {COLOR_SUBTLE};
	}}
	QLabel#powerValue {{
		font-family: {FONT_NUM};
		font-size: 15px;
		font-weight: 600;
		color: {COLOR_POWER};
	}}

	QFrame#metricBox {{
		background-color: {COLOR_CARD_ALT};
		border-radius: 10px;
	}}

	/* 卡片内 ON 按钮 */
	QPushButton#onBtn {{
		border-radius: 8px;
		font-weight: 700;
		font-size: 14px;
		border: none;
		padding: 8px 0;
	}}
	QPushButton#onBtn:checked {{
		background-color: {COLOR_ON};
		color: #10241a;
	}}
	QPushButton#onBtn:!checked {{
		background-color: {COLOR_OFF};
		color: #2a1414;
	}}

	/* 移除卡片按钮 */
	QPushButton#removeBtn {{
		background: transparent;
		border: none;
		border-radius: 10px;
		min-width: 22px; max-width: 22px;
		min-height: 22px; max-height: 22px;
		color: {COLOR_SUBTLE};
		font-size: 15px;
	}}
	QPushButton#removeBtn:hover {{
		background-color: {COLOR_OFF};
		color: #ffffff;
	}}

	QCheckBox {{ color: {COLOR_TEXT}; spacing: 6px; }}
	QCheckBox::indicator {{
		width: 16px; height: 16px;
		border-radius: 4px;
		border: 1px solid {COLOR_BORDER};
		background-color: {COLOR_CARD_ALT};
	}}
	QCheckBox::indicator:checked {{
		background-color: {COLOR_ACCENT};
		border: 1px solid {COLOR_ACCENT};
	}}

	QLabel#statusOk {{ color: {COLOR_ON}; }}
	QLabel#statusErr {{ color: {COLOR_OFF}; }}
	"""


# ----------------------------------------------------------------------------
# 指标显示块（大字体数值 + 单位）
# ----------------------------------------------------------------------------
class MetricBox(QFrame):
	def __init__(self, caption, value_style, unit, parent=None):
		super().__init__(parent)
		self.setObjectName("metricBox")
		lay = QVBoxLayout(self)
		lay.setContentsMargins(14, 10, 14, 10)
		lay.setSpacing(2)

		cap = QLabel(caption)
		cap.setObjectName("metricCaption")
		lay.addWidget(cap)

		row = QHBoxLayout()
		row.setSpacing(6)
		row.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
		self.value = QLabel("0.000")
		self.value.setProperty("styleRole", value_style)
		self.value.setStyleSheet(f"""
			font-family: {FONT_NUM};
			font-size: 46px;
			font-weight: 700;
			color: {value_style};
		""")
		unit_lbl = QLabel(unit)
		unit_lbl.setObjectName("unitLabel")
		row.addWidget(self.value)
		row.addWidget(unit_lbl, 0, Qt.AlignBottom)
		row.addStretch()
		lay.addLayout(row)

	def setValue(self, text):
		self.value.setText(text)


# ----------------------------------------------------------------------------
# 通道卡片
# ----------------------------------------------------------------------------
class ChannelCard(QFrame):
	"""单个通道的展示卡片：通道选择 + 大字体 V/I + 功率曲线 + ON 按钮"""

	removeRequested = Signal(object)

	def __init__(self, index, parent=None):
		super().__init__(parent)
		self.setObjectName("channelCard")

		# 数据状态
		self.index = index
		self.channel = "CH%d" % (index + 1)
		self.points = 600
		self.pdata = [0.0] * self.points
		self.output_on = False

		root = QVBoxLayout(self)
		root.setContentsMargins(16, 14, 16, 16)
		root.setSpacing(12)

		# --- 卡片头部：标题 + 通道选择 + 移除 ---
		header = QHBoxLayout()
		header.setSpacing(8)

		self.title = QLabel("通道 %d" % (index + 1))
		self.title.setObjectName("cardTitle")
		header.addWidget(self.title)
		header.addStretch()

		self.cbChannel = QComboBox()
		self.cbChannel.addItems(["CH1", "CH2", "CH3"])
		self.cbChannel.setCurrentIndex(index)
		self.cbChannel.currentIndexChanged.connect(self._onChannelChanged)
		header.addWidget(self.cbChannel)

		self.removeBtn = QPushButton("×")
		self.removeBtn.setObjectName("removeBtn")
		self.removeBtn.setToolTip("移除此通道")
		self.removeBtn.clicked.connect(lambda: self.removeRequested.emit(self))
		header.addWidget(self.removeBtn)
		root.addLayout(header)

		# --- 电压 / 电流 大字显示 ---
		metrics = QHBoxLayout()
		metrics.setSpacing(12)
		self.voltBox = MetricBox("电压 VOLTAGE", COLOR_VOLTAGE, "V")
		self.currBox = MetricBox("电流 CURRENT", COLOR_CURRENT, "A")
		metrics.addWidget(self.voltBox, 1)
		metrics.addWidget(self.currBox, 1)
		root.addLayout(metrics)

		# --- 设定区：输出电压 / 限流 / 过流保护 ---
		root.addWidget(self._buildSettingBox())

		# --- 功率曲线 ---
		power_header = QHBoxLayout()
		power_header.setSpacing(8)
		pcap = QLabel("功率历程 POWER")
		pcap.setObjectName("metricCaption")
		power_header.addWidget(pcap)
		power_header.addStretch()
		self.powerValue = QLabel("0.000 W")
		self.powerValue.setObjectName("powerValue")
		power_header.addWidget(self.powerValue)
		root.addLayout(power_header)

		self.pw = pg.PlotWidget()
		self.pw.setBackground(COLOR_CARD_ALT)
		self.pw.setMouseEnabled(x=True, y=True)
		self.pw.hideButtons()
		self.pw.setMinimumHeight(150)
		self.pw.showGrid(x=True, y=True, alpha=0.15)
		self.pw.setLabel('bottom', '采样点', color=COLOR_SUBTLE, **{'font-size': '10px'})
		self.pw.setLabel('left', 'W', color=COLOR_SUBTLE, **{'font-size': '10px'})
		for ax in ('left', 'bottom'):
			self.pw.getAxis(ax).setPen(pg.mkPen(COLOR_BORDER, width=1))
			self.pw.getAxis(ax).setTextPen(pg.mkPen(COLOR_SUBTLE, width=1))
		self.pw.getPlotItem().getViewBox().setMouseMode(pg.ViewBox.RectMode)
		self.curve = self.pw.plot(
			self.pdata,
			pen=pg.mkPen(COLOR_POWER, width=2),
			name="Power",
		)
		root.addWidget(self.pw, 1)

		# --- 底部：ON 按钮 + 采样点数 ---
		footer = QHBoxLayout()
		footer.setSpacing(10)

		self.onBtn = QPushButton("输出 OFF")
		self.onBtn.setObjectName("onBtn")
		self.onBtn.setCheckable(True)
		self.onBtn.setChecked(False)
		self.onBtn.clicked.connect(self._onToggleOutput)
		footer.addWidget(self.onBtn, 1)

		footer.addWidget(QLabel("点数"))
		self.sbPoints = QSpinBox()
		self.sbPoints.setMinimum(10)
		self.sbPoints.setMaximum(500000)
		self.sbPoints.setValue(self.points)
		self.sbPoints.valueChanged.connect(self._onPointsChanged)
		footer.addWidget(self.sbPoints)

		root.addLayout(footer)

	# ------------------------- 设定区构建 -------------------------
	def _buildSettingBox(self):
		box = QFrame()
		box.setObjectName("metricBox")
		lay = QVBoxLayout(box)
		lay.setContentsMargins(14, 10, 14, 12)
		lay.setSpacing(8)

		cap = QLabel("设定 SETTING")
		cap.setObjectName("metricCaption")
		lay.addWidget(cap)

		# 电压设定行
		vrow = QHBoxLayout()
		vrow.setSpacing(8)
		vlbl = QLabel("输出电压")
		vlbl.setObjectName("setCaption")
		vlbl.setFixedWidth(64)
		self.setV = QDoubleSpinBox()
		self.setV.setRange(0.0, 40.0)
		self.setV.setDecimals(3)
		self.setV.setSingleStep(0.1)
		self.setV.setSuffix(" V")
		self.setV.setValue(5.0 * (self.index + 1))
		self.applyVBtn = QPushButton("设定电压")
		self.applyVBtn.setObjectName("applyBtn")
		self.applyVBtn.clicked.connect(self._applyVoltage)
		vrow.addWidget(vlbl)
		vrow.addWidget(self.setV, 1)
		vrow.addWidget(self.applyVBtn)
		lay.addLayout(vrow)

		# 限流设定行
		irow = QHBoxLayout()
		irow.setSpacing(8)
		ilbl = QLabel("限流值")
		ilbl.setObjectName("setCaption")
		ilbl.setFixedWidth(64)
		self.setI = QDoubleSpinBox()
		self.setI.setRange(0.0, 5.0)
		self.setI.setDecimals(3)
		self.setI.setSingleStep(0.01)
		self.setI.setSuffix(" A")
		self.setI.setValue(0.5)
		self.applyIBtn = QPushButton("设定限流")
		self.applyIBtn.setObjectName("applyBtn")
		self.applyIBtn.clicked.connect(self._applyCurrent)
		irow.addWidget(ilbl)
		irow.addWidget(self.setI, 1)
		irow.addWidget(self.applyIBtn)
		lay.addLayout(irow)

		# 过流保护 OCP
		self.ocpCheck = QCheckBox("过流保护 OCP（电流超限即切断输出）")
		self.ocpCheck.setToolTip(
			"开启后以“限流值”作为过流阈值，一旦超过则切断输出。\n"
			"仅“限流值”为恒流钳位（不切断），两者配合可完整实现限流+过流保护。"
		)
		self.ocpCheck.toggled.connect(self._applyOcp)
		lay.addWidget(self.ocpCheck)

		return box

	# ------------------------- 设定区槽函数 -------------------------
	def _applyVoltage(self):
		main = self.window()
		if hasattr(main, "applyVoltage"):
			main.applyVoltage(self, self.setV.value())

	def _applyCurrent(self):
		main = self.window()
		if hasattr(main, "applyCurrent"):
			main.applyCurrent(self, self.setI.value())

	def _applyOcp(self, enabled):
		main = self.window()
		if hasattr(main, "applyOcp"):
			main.applyOcp(self, enabled, self.setI.value())

	# ------------------------- 内部槽函数 -------------------------
	def _onChannelChanged(self, idx):
		self.channel = "CH%d" % (idx + 1)

	def _onPointsChanged(self, val):
		self.points = int(val)
		# 调整数据缓冲长度
		if len(self.pdata) > self.points:
			self.pdata = self.pdata[-self.points:]
		else:
			self.pdata = [0.0] * (self.points - len(self.pdata)) + self.pdata

	def _onToggleOutput(self):
		self.output_on = self.onBtn.isChecked()
		self.onBtn.setText("输出 ON" if self.output_on else "输出 OFF")
		# 真实设备的输出控制在主窗口处理
		main = self.window()
		if hasattr(main, "onOutputToggled"):
			main.onOutputToggled(self)

	# ------------------------- 对外接口 -------------------------
	def setRemoveEnabled(self, enabled):
		self.removeBtn.setVisible(enabled)

	def updateReading(self, v, i, p):
		"""刷新大字体数值与功率曲线"""
		self.voltBox.setValue("%.3f" % v)
		self.currBox.setValue("%.4f" % i)
		self.powerValue.setText("%.3f W" % p)

		self.pdata.append(p)
		while len(self.pdata) > self.points:
			self.pdata.pop(0)
		self.curve.setData(self.pdata)


# ----------------------------------------------------------------------------
# 主窗口
# ----------------------------------------------------------------------------
class DP832GUI(QMainWindow):

	def __init__(self):
		super(DP832GUI, self).__init__()
		self.setWindowTitle("DP832 GUI")
		self.inst = None
		self.connected = False
		self.readtimer = None

		pg.setConfigOptions(antialias=True)

		settings = QSettings()
		constr = settings.value('constring')
		if constr is None:
			constr = "USB0::0x1AB1::0x0E11::DPXXXXXXXXXXX::INSTR"

		central = QWidget()
		self.setCentralWidget(central)
		outer = QVBoxLayout(central)
		outer.setContentsMargins(0, 0, 0, 0)
		outer.setSpacing(0)

		outer.addWidget(self._buildTopBar(constr))

		# 卡片容器
		self.cardsHost = QWidget()
		self.cardsLayout = QHBoxLayout(self.cardsHost)
		self.cardsLayout.setContentsMargins(14, 14, 14, 14)
		self.cardsLayout.setSpacing(14)
		self.cardsLayout.addStretch()
		outer.addWidget(self.cardsHost, 1)

		self.cards = []
		self.addChannelCard()   # 默认 1 列

		self.resize(1000, 680)
		self._refreshAddButton()

		# 启动即连接仪器并读取状态（连接失败时仅状态栏提示，不弹窗）
		self.tryConnect(show_error=False)

	# ------------------------- 顶部工具栏 -------------------------
	def _buildTopBar(self, constr):
		bar = QFrame()
		bar.setObjectName("topBar")
		bar.setFixedHeight(66)
		lay = QHBoxLayout(bar)
		lay.setContentsMargins(16, 10, 16, 10)
		lay.setSpacing(10)

		titleBox = QVBoxLayout()
		titleBox.setSpacing(0)
		t = QLabel("DP832 电源监控")
		t.setObjectName("appTitle")
		s = QLabel("Rigol DP832 Power Supply Monitor")
		s.setObjectName("appSub")
		titleBox.addWidget(t)
		titleBox.addWidget(s)
		lay.addLayout(titleBox)

		lay.addSpacing(20)

		lay.addWidget(QLabel("连接地址"))
		self.constr = QLineEdit(constr)
		self.constr.setMinimumWidth(320)
		lay.addWidget(self.constr)

		self.connectBtn = QPushButton("连接")
		self.connectBtn.setObjectName("connectBtn")
		self.connectBtn.clicked.connect(lambda: self.tryConnect())
		lay.addWidget(self.connectBtn)

		self.disconnectBtn = QPushButton("断开")
		self.disconnectBtn.clicked.connect(self.dis)
		self.disconnectBtn.setEnabled(False)
		lay.addWidget(self.disconnectBtn)

		self.statusLbl = QLabel("未连接")
		self.statusLbl.setObjectName("statusErr")
		lay.addWidget(self.statusLbl)

		lay.addStretch()

		self.addBtn = QPushButton("+")
		self.addBtn.setObjectName("addBtn")
		self.addBtn.setToolTip("增加一个通道列（最多 3 列）")
		self.addBtn.clicked.connect(self.addChannelCard)
		lay.addWidget(self.addBtn)

		return bar

	# ------------------------- 卡片管理 -------------------------
	def addChannelCard(self):
		if len(self.cards) >= MAX_COLUMNS:
			return
		idx = len(self.cards)
		card = ChannelCard(idx)
		card.removeRequested.connect(self.removeChannelCard)
		# 插入到末尾 stretch 之前
		self.cardsLayout.insertWidget(self.cardsLayout.count() - 1, card)
		self.cards.append(card)
		self._refreshAddButton()

	def removeChannelCard(self, card):
		if len(self.cards) <= 1:
			return
		if card in self.cards:
			self.cards.remove(card)
			self.cardsLayout.removeWidget(card)
			card.deleteLater()
		# 重新排布索引与默认通道
		for i, c in enumerate(self.cards):
			c.index = i
			c.title.setText("通道 %d" % (i + 1))
		self._refreshAddButton()

	def _refreshAddButton(self):
		full = len(self.cards) >= MAX_COLUMNS
		self.addBtn.setEnabled(not full)
		self.addBtn.setToolTip(
			"已达最多 3 列" if full else "增加一个通道列（最多 3 列）"
		)
		# 仅剩 1 个卡片时隐藏其移除按钮
		for c in self.cards:
			c.setRemoveEnabled(len(self.cards) > 1)

	# ------------------------- 连接 / 通信 -------------------------
	def tryConnect(self, show_error=True):
		constr = self.constr.text()
		QSettings().setValue('constring', constr)

		try:
			self.inst = DP832()
			self.inst.conn(constr)
			self.connected = True
			self._setStatus("已连接", True)
			self.connectBtn.setEnabled(False)
			self.disconnectBtn.setEnabled(True)
			self.constr.setEnabled(False)
			self._startTimer()
		except Exception as e:
			self._setStatus("连接失败: %s" % e, False)
			if show_error:
				QMessageBox.critical(self, "连接失败", str(e))
			self.inst = None
			self.connected = False

	def _startTimer(self):
		if self.readtimer is None:
			self.readtimer = QTimer()
			self.readtimer.setInterval(250)
			self.readtimer.timeout.connect(self.updateReadings)
		self.readtimer.start()

	def dis(self):
		if self.readtimer is not None:
			self.readtimer.stop()
		if self.inst is not None:
			try:
				self.inst.dis()
			except Exception:
				pass
			self.inst = None
		self.connected = False
		self._setStatus("未连接", False)
		self.connectBtn.setEnabled(True)
		self.disconnectBtn.setEnabled(False)
		self.constr.setEnabled(True)

	def _setStatus(self, text, ok):
		self.statusLbl.setText(text)
		self.statusLbl.setObjectName("statusOk" if ok else "statusErr")
		# 触发样式刷新
		self.statusLbl.style().unpolish(self.statusLbl)
		self.statusLbl.style().polish(self.statusLbl)

	def onOutputToggled(self, card):
		"""卡片 ON 按钮状态变化时，向真实设备发送输出指令"""
		if self.inst is None:
			return
		state = "ON" if card.output_on else "OFF"
		try:
			if card.output_on:
				# 开启输出前先清除可能存在的 OCP 保护锁定
				try:
					self.inst.clear_protection(card.channel)
				except Exception:
					pass
			self.inst.writing(":OUTP %s,%s" % (card.channel, state))
		except Exception as e:
			self._setStatus("输出指令失败", False)

	def applyVoltage(self, card, volts):
		"""设定输出电压（如 24V）"""
		if self.inst is None:
			self._setStatus("未连接，无法设定电压", False)
			return
		try:
			self.inst.set_voltage(volts, card.channel)
			self._setStatus("已设定 %s 电压 %.3fV" % (card.channel, volts), True)
		except Exception as e:
			self._setStatus("设定电压失败", False)

	def applyCurrent(self, card, amps):
		"""设定恒流限流值（如 0.2A）"""
		if self.inst is None:
			self._setStatus("未连接，无法设定限流", False)
			return
		try:
			self.inst.set_current(amps, card.channel)
			self._setStatus("已设定 %s 限流 %.3fA" % (card.channel, amps), True)
		except Exception as e:
			self._setStatus("设定限流失败", False)

	def applyOcp(self, card, enabled, level):
		"""开/关过流保护 OCP，阈值取限流值；超限即切断输出"""
		if self.inst is None:
			self._setStatus("未连接，无法设定过流保护", False)
			return
		try:
			self.inst.set_ocp(enabled, level, card.channel)
			self._setStatus(
				"%s 过流保护已%s（%.3fA）" % (card.channel, "开启" if enabled else "关闭", level),
				True,
			)
		except Exception as e:
			self._setStatus("设定 OCP 失败", False)

	# ------------------------- 数据刷新 -------------------------
	def updateReadings(self):
		if not self.connected or self.inst is None:
			return
		for card in self.cards:
			try:
				r = self.inst.readings(card.channel)
				card.updateReading(r["v"], r["i"], r["p"])
			except Exception:
				# 单通道读取失败不影响其它通道
				pass


# ----------------------------------------------------------------------------
# 入口
# ----------------------------------------------------------------------------
def makeApplication():
	app = QApplication(sys.argv)
	app.setOrganizationName("GhettoFab Productions")
	app.setApplicationName("DP832 GUI")
	app.setStyleSheet(build_stylesheet())
	return app


if __name__ == '__main__':
	app = makeApplication()

	window = DP832GUI()
	window.show()

	sys.exit(app.exec())
