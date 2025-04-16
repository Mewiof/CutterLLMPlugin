import cutter
import os
import subprocess
import sys

NODE_EXECUTABLE = "node"
NODE_SCRIPT_FILEPATH = f"{os.environ['APPDATA']}/rizin/cutter/plugins/LLMPluginAssets/index.js"

from PySide2.QtCore import QObject, SIGNAL, Slot
from PySide2.QtWidgets import (
	QAction,
	QLabel,
	QWidget,
	QVBoxLayout,
	QPlainTextEdit,
	QPushButton,
	QLineEdit
)
from PySide2.QtGui import QFontDatabase

def write_to_file(filename, text):
	try:
		with open(filename, "w") as file:
			file.write(text)
	except Exception:
		print(f"[LLM Plugin] Failed to write to \"{filename}\"")
def read_from_file(filename):
	try:
		with open(filename, "r") as file:
			return file.read()
	except Exception:
		print(f"[LLM Plugin] Failed to read from \"{filename}\"")

class LLMPluginWidget(cutter.CutterDockWidget):
	def __init__(self, parent, action):
		super(LLMPluginWidget, self).__init__(parent, action)
		self.setObjectName("LLM Plugin")
		self.setWindowTitle("LLM Plugin")

		# --- UI Setup ---
		container_widget = QWidget(self)
		layout = QVBoxLayout(container_widget)
		layout.setContentsMargins(4, 4, 4, 4)
		layout.setSpacing(4)

		# -- Model Input --
		model_label = QLabel("Model:", self)
		self._model_input = QLineEdit(self)
		self._model_input.setPlaceholderText("anthropic/claude-3.7-sonnet:thinking")
		self._model_input.setText(self._model_input.placeholderText())
		layout.addWidget(model_label)
		layout.addWidget(self._model_input)
		# -- API Key Input --
		api_key_label = QLabel("API Key:", self)
		self._api_key_input = QLineEdit(self)
		self._api_key_input.setEchoMode(QLineEdit.Password)
		self._api_key_input.setPlaceholderText("xx-xx-xx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
		layout.addWidget(api_key_label)
		layout.addWidget(self._api_key_input)

		# -- Decompiled Code Area --
		self._text_edit = QPlainTextEdit(self)
		self._text_edit.setReadOnly(True)
		self._text_edit.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
		self._text_edit.setPlaceholderText("...")
		layout.addWidget(self._text_edit)

		# -- Analyze Button --
		self._analyze_button = QPushButton("Analyze", self)
		self._analyze_button.clicked.connect(self._analyze)
		layout.addWidget(self._analyze_button)

		self.setWidget(container_widget)
		# --- End UI Setup ---

		# load
		try:
			config = read_from_file("LLMPlugin.cfg")
			if config != None:
				configValues = config.split("=meow=")
				self._model_input.setText(configValues[0])
				self._api_key_input.setText(configValues[1])
		except Exception:
			print("[LLM Plugin] Failed to load configuration")

		QObject.connect(cutter.core(), SIGNAL("seekChanged(RVA)"), self._update_contents)
		self._update_contents()

	@Slot()
	def _update_contents(self):
		try:
			decompiled_code = cutter.cmd("pdg")
			if not decompiled_code or decompiled_code.startswith("Cannot"):
				print("[LLM Plugin] Failed to decompile")
			else:
				self._decompiled_code = decompiled_code.strip()
				self._text_edit.setPlainText(self._decompiled_code)
				return
		except Exception as e:
			print("[LLM Plugin] Failed to decompile")
		self._text_edit.setPlainText("")

	@Slot()
	def _analyze(self):
		# save
		write_to_file("LLMPlugin.cfg", f"{self._model_input.text()}=meow={self._api_key_input.text()}")

		output_string = ""
		try:
			creation_flags = 0
			if sys.platform == "win32":
				creation_flags = subprocess.CREATE_NO_WINDOW
			result = subprocess.run(
				[
					NODE_EXECUTABLE,
					NODE_SCRIPT_FILEPATH,
					self._api_key_input.text(),
					self._model_input.text(),
					self._decompiled_code,
				],
				capture_output=True,
				text=True,
				encoding="utf-8",
				check=False,
				creationflags=creation_flags
			)
			output_string = result.stdout + result.stderr
			failed = output_string.startswith("Failed --> ")
			if failed:
				output_string = output_string.split("Failed --> ")[1]
			if result.returncode != 0 or failed:
				print("[LLM Plugin] Failed to analyze")
			else:
				print("[LLM Plugin] Analyzed")
		except Exception:
			print("[LLM Plugin] Failed to analyze")

		self._text_edit.setPlainText(output_string)


class LLMPlugin(cutter.CutterPlugin):
	name = "LLM Plugin"
	description = "-"
	version = "1.0"
	author = "Mewiof"

	def setupPlugin(self):
		pass

	def setupInterface(self, main):
		action = QAction("LLM Plugin", main)
		action.setCheckable(True)
		widget = LLMPluginWidget(main, action)
		main.addPluginDockWidget(widget, action)

	def terminate(self):
		pass

def create_cutter_plugin():
	return LLMPlugin()
