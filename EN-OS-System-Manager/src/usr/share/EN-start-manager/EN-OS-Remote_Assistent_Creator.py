#!/usr/bin/env python3
import sys
import os
import subprocess
import threading
import re
import shutil
import time
import json
import locale
from pathlib import Path
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFrame,
                             QLineEdit, QTextEdit, QProgressBar, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSignal, QObject
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor, QLinearGradient,
                         QPainter, QFontDatabase, QTextCursor)

os.environ['XDG_RUNTIME_DIR'] = '/tmp/runtime-root'

LOCALES = {
    'en': {
        'app_title': 'EN-OS Remote Assistant Creator',
        'header': '🛠️ Remote Assistant Creator',
        'token_label': 'Telegram Bot Token:',
        'token_placeholder': 'Enter your Bot Token from @BotFather...',
        'id_label': 'Admin Chat ID:',
        'id_placeholder': 'Enter your Telegram Chat ID...',
        'console_label': 'Build Output:',
        'build_btn': '🛠️ Build Remote Assistant',
        'clear_btn': '🗑️ Clear Console',
        'help_btn': '❓ Instructions',
        'language': 'Language',
        'error_title': 'Error',
        'success_title': 'Success',
        'error_fields': 'Please fill in all fields!',
        'error_build_running': 'Build already in progress...',
        'success_build': 'Build completed successfully!',
        'instructions': """
📋 Instructions:

1. Create a Telegram Bot using @BotFather
2. Copy the Bot Token and paste it above
3. Send a message to your bot and get your Chat ID using @userinfobot
4. Click 'Build Remote Assistant' to compile the client
5. The executable will be created as 'enclient'
6. Application will start automatically and run on system startup
        """
    },
    'ru': {
        'app_title': 'EN-OS Remote Assistant Creator',
        'header': '🛠️ Remote Assistant Creator',
        'token_label': 'Токен Telegram Бота:',
        'token_placeholder': 'Введите токен бота от @BotFather...',
        'id_label': 'Ваш телеграм ID:',
        'id_placeholder': 'Введите ваш Telegram ID...',
        'console_label': 'Вывод сборки:',
        'build_btn': '🛠️ Собрать Ассистента',
        'clear_btn': '🗑️ Очистить консоль',
        'help_btn': '❓ Инструкции',
        'language': 'Язык',
        'error_title': 'Ошибка',
        'success_title': 'Успех',
        'error_fields': 'Пожалуйста, заполните все поля!',
        'error_build_running': 'Сборка уже выполняется...',
        'success_build': 'Сборка успешно завершена!',
        'instructions': """
📋 Инструкции:

1. Создайте бота в Telegram через @BotFather
2. Скопируйте токен бота и вставьте выше
3. Отправьте сообщение боту и получите ваш Chat ID через @userinfobot
4. Нажмите 'Собрать Ассистента' для компиляции клиента
5. Исполняемый файл будет создан как 'enclient'
6. Приложение запустится автоматически и будет работать при старте системы
        """
    },
    'es': {
        'app_title': 'Creador de Asistente Remoto EN-OS',
        'header': '🛠️ Creador de Asistente Remoto',
        'token_label': 'Token del Bot de Telegram:',
        'token_placeholder': 'Ingrese el token de su bot de @BotFather...',
        'id_label': 'ID de Chat del Administrador:',
        'id_placeholder': 'Ingrese su ID de chat de Telegram...',
        'console_label': 'Salida de compilación:',
        'build_btn': '🛠️ Crear Asistente Remoto',
        'clear_btn': '🗑️ Limpiar Consola',
        'help_btn': '❓ Instrucciones',
        'language': 'Idioma',
        'error_title': 'Error',
        'success_title': 'Éxito',
        'error_fields': '¡Por favor complete todos los campos!',
        'error_build_running': 'La compilación ya está en progreso...',
        'success_build': '¡Compilación completada con éxito!',
        'instructions': """
📋 Instrucciones:

1. Crea un bot de Telegram usando @BotFather
2. Copia el Token del Bot y pégalo arriba
3. Envía un mensaje a tu bot y obtén tu Chat ID con @userinfobot
4. Haz clic en 'Crear Asistente Remoto' para compilar
5. Se creará el ejecutable 'enclient'
6. La aplicación se iniciará automáticamente y se ejecutará al iniciar el sistema
        """
    },
    'fr': {
        'app_title': 'Créateur d\'Assistant Distant EN-OS',
        'header': '🛠️ Créateur d\'Assistant Distant',
        'token_label': 'Token du Bot Telegram :',
        'token_placeholder': 'Entrez le token de votre bot depuis @BotFather...',
        'id_label': 'ID de Chat Admin :',
        'id_placeholder': 'Entrez votre ID de chat Telegram...',
        'console_label': 'Sortie de compilation :',
        'build_btn': '🛠️ Créer l\'Assistant Distant',
        'clear_btn': '🗑️ Effacer la Console',
        'help_btn': '❓ Instructions',
        'language': 'Langue',
        'error_title': 'Erreur',
        'success_title': 'Succès',
        'error_fields': 'Veuillez remplir tous les champs !',
        'error_build_running': 'La compilation est déjà en cours...',
        'success_build': 'Compilation terminée avec succès !',
        'instructions': """
📋 Instructions :

1. Créez un bot Telegram via @BotFather
2. Copiez le token du bot et collez-le ci-dessus
3. Envoyez un message au bot et obtenez votre Chat ID avec @userinfobot
4. Cliquez sur « Créer l'Assistant Distant » pour compiler
5. L'exécutable 'enclient' sera créé
6. L'application démarrera automatiquement au démarrage du système
        """
    },
    'de': {
        'app_title': 'EN-OS Fernassistenten-Ersteller',
        'header': '🛠️ Fernassistenten-Ersteller',
        'token_label': 'Telegram Bot Token:',
        'token_placeholder': 'Geben Sie Ihren Bot-Token von @BotFather ein...',
        'id_label': 'Admin-Chat-ID:',
        'id_placeholder': 'Geben Sie Ihre Telegram-Chat-ID ein...',
        'console_label': 'Build-Ausgabe:',
        'build_btn': '🛠️ Fernassistenten erstellen',
        'clear_btn': '🗑️ Konsole leeren',
        'help_btn': '❓ Anleitung',
        'language': 'Sprache',
        'error_title': 'Fehler',
        'success_title': 'Erfolg',
        'error_fields': 'Bitte alle Felder ausfüllen!',
        'error_build_running': 'Build läuft bereits...',
        'success_build': 'Build erfolgreich abgeschlossen!',
        'instructions': """
📋 Anleitung:

1. Erstellen Sie einen Telegram-Bot mit @BotFather
2. Kopieren Sie den Bot-Token und fügen Sie ihn oben ein
3. Senden Sie eine Nachricht an Ihren Bot und holen Sie Ihre Chat-ID mit @userinfobot
4. Klicken Sie auf 'Fernassistenten erstellen' zum Kompilieren
5. Die ausführbare Datei 'enclient' wird erstellt
6. Die Anwendung startet automatisch und läuft beim Systemstart
        """
    },
    'zh_CN': {
        'app_title': 'EN-OS 远程助手创建器',
        'header': '🛠️ 远程助手创建器',
        'token_label': 'Telegram Bot 令牌：',
        'token_placeholder': '请输入来自 @BotFather 的机器人令牌...',
        'id_label': '管理员聊天 ID：',
        'id_placeholder': '请输入您的 Telegram 聊天 ID...',
        'console_label': '构建输出：',
        'build_btn': '🛠️ 构建远程助手',
        'clear_btn': '🗑️ 清除控制台',
        'help_btn': '❓ 使用说明',
        'language': '语言',
        'error_title': '错误',
        'success_title': '成功',
        'error_fields': '请填写所有字段！',
        'error_build_running': '构建已在进行中...',
        'success_build': '构建成功完成！',
        'instructions': """
📋 使用说明：

1. 通过 @BotFather 创建 Telegram 机器人
2. 复制机器人令牌并粘贴到上方
3. 向机器人发送消息，并通过 @userinfobot 获取您的 Chat ID
4. 点击「构建远程助手」进行编译
5. 将生成可执行文件「enclient」
6. 程序将自动启动并设置为开机自启
        """
    },
    'ja': {
        'app_title': 'EN-OS リモートアシスタント作成ツール',
        'header': '🛠️ リモートアシスタント作成ツール',
        'token_label': 'Telegram Bot トークン：',
        'token_placeholder': '@BotFather から取得したボットトークンを入力...',
        'id_label': '管理者チャットID：',
        'id_placeholder': 'あなたの Telegram チャットIDを入力...',
        'console_label': 'ビルド出力：',
        'build_btn': '🛠️ リモートアシスタントを作成',
        'clear_btn': '🗑️ コンソールをクリア',
        'help_btn': '❓ 使い方',
        'language': '言語',
        'error_title': 'エラー',
        'success_title': '成功',
        'error_fields': 'すべての項目を入力してください！',
        'error_build_running': 'ビルドが既に実行中です...',
        'success_build': 'ビルドが正常に完了しました！',
        'instructions': """
📋 使い方：

1. @BotFather を使って Telegram ボットを作成
2. ボットのトークンをコピーして上記に入力
3. ボットにメッセージを送り、@userinfobot でチャットIDを取得
4. 「リモートアシスタントを作成」をクリックしてコンパイル
5. 実行ファイル「enclient」が作成されます
6. アプリケーションは自動起動し、システム起動時に実行されます
        """
    },
    'ko': {
        'app_title': 'EN-OS 원격 지원 도구 제작기',
        'header': '🛠️ 원격 지원 도구 제작기',
        'token_label': 'Telegram 봇 토큰:',
        'token_placeholder': '@BotFather에서 받은 봇 토큰을 입력하세요...',
        'id_label': '관리자 채팅 ID:',
        'id_placeholder': '당신의 Telegram 채팅 ID를 입력하세요...',
        'console_label': '빌드 출력:',
        'build_btn': '🛠️ 원격 지원 도구 빌드',
        'clear_btn': '🗑️ 콘솔 지우기',
        'help_btn': '❓ 사용 방법',
        'language': '언어',
        'error_title': '오류',
        'success_title': '성공',
        'error_fields': '모든 항목을 입력해 주세요!',
        'error_build_running': '이미 빌드가 진행 중입니다...',
        'success_build': '빌드가 성공적으로 완료되었습니다!',
        'instructions': """
📋 사용 방법:

1. @BotFather를 통해 Telegram 봇 생성
2. 봇 토큰을 복사하여 위에 붙여넣기
3. 봇에게 메시지 전송 후 @userinfobot으로 채팅 ID 확인
4. '원격 지원 도구 빌드' 버튼 클릭하여 컴파일
5. 실행 파일 'enclient' 생성됨
6. 프로그램은 자동 실행되며 시스템 시작 시 함께 실행
        """
    }
}

COLORS = {
    'primary': {
        'dark': '#0f0f23',
        'medium': '#1a1a2e',
        'light': '#16213e'
    },
    'accent': {
        'blue': '#4fc4cf',
        'purple': '#9d4edd',
        'cyan': '#00bbf9',
        'dark_blue': '#4361ee',
        'green': '#4cd964'
    },
    'text': {
        'primary': '#ffffff',
        'secondary': '#b8b8d1',
        'muted': '#8b8ba7'
    },
    'misc': {
        'border': '#2d2d4d',
        'success': '#4cd964',
        'error': '#ff4757',
        'input_bg': '#2a2a4a'
    }
}

class LanguageManager:
    def __init__(self):
        self.current_language = self.detect_system_language()
        self.load_language_setting()

    def detect_system_language(self):
        try:
            lang_env = os.environ.get('LANG', '') or os.environ.get('LANGUAGE', '')
            if lang_env:
                lang_code = lang_env.split('_')[0].lower()
                if lang_code in ['ru', 'uk']:
                    return 'ru'

            try:
                system_locale = locale.getdefaultlocale()[0]
                if system_locale:
                    lang_code = system_locale.split('_')[0].lower()
                    if lang_code in ['ru', 'uk']:
                        return 'ru'
            except:
                pass

        except Exception as e:
            print(f"Language detection error: {e}")

        return 'en'

    def load_language_setting(self):
        try:
            config_dir = Path.home() / '.config' / 'enos_manager'
            config_file = config_dir / 'settings.json'

            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    saved_language = settings.get('language')
                    if saved_language in LOCALES:
                        self.current_language = saved_language
        except Exception as e:
            print(f"Error loading language settings: {e}")

    def save_language_setting(self):
        try:
            config_dir = Path.home() / '.config' / 'enos_manager'
            config_dir.mkdir(parents=True, exist_ok=True)

            config_file = config_dir / 'settings.json'
            settings = {'language': self.current_language}

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving language settings: {e}")

    def get_text(self, key):
        return LOCALES[self.current_language].get(key, key)

    def set_language(self, language):
        if language in LOCALES:
            self.current_language = language
            self.save_language_setting()
            return True
        return False

class BuildSignals(QObject):
    output_received = pyqtSignal(str)
    progress_updated = pyqtSignal(int, str)
    build_finished = pyqtSignal(bool, str)

class MinimalButton(QPushButton):
    def __init__(self, text, icon=None, color_scheme='blue', parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(55)
        self.setFont(QFont("GNF", 14))

        self._opacity = 1.0
        self._scale = 1.0
        self.color_scheme = color_scheme

        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(24, 24))

        self.update_style()

        self.hover_animation = QPropertyAnimation(self, b"scale")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.OutBack)

        self.click_animation = QPropertyAnimation(self, b"opacity")
        self.click_animation.setDuration(100)
        self.click_animation.setEasingCurve(QEasingCurve.OutCubic)

    def update_style(self):
        colors = {
            'blue': {'bg': '#2a2a4a', 'hover': '#3a3a5a', 'text': COLORS['accent']['blue']},
            'purple': {'bg': '#2a2a4a', 'hover': '#3a3a5a', 'text': COLORS['accent']['purple']},
            'cyan': {'bg': '#2a2a4a', 'hover': '#3a3a5a', 'text': COLORS['accent']['cyan']},
            'green': {'bg': '#2a2a4a', 'hover': '#3a3a5a', 'text': COLORS['accent']['green']}
        }

        color = colors.get(self.color_scheme, colors['blue'])

        self.setStyleSheet(f"""
            MinimalButton {{
                background-color: {color['bg']};
                color: {color['text']};
                border: 1px solid {COLORS['misc']['border']};
                border-radius: 8px;
                padding: 15px 20px;
                text-align: center;
                font-weight: normal;
                font-size: 16px;
            }}
            MinimalButton:hover {{
                background-color: {color['hover']};
                border: 1px solid {color['text']};
            }}
            MinimalButton:pressed {{
                background-color: {color['bg']};
                border: 1px solid {color['text']};
            }}
        """)

    def get_opacity(self):
        return self._opacity

    def set_opacity(self, opacity):
        self._opacity = opacity
        self.update()

    def get_scale(self):
        return self._scale

    def set_scale(self, scale):
        self._scale = scale
        self.update()

    opacity = pyqtProperty(float, get_opacity, set_opacity)
    scale = pyqtProperty(float, get_scale, set_scale)

    def enterEvent(self, event):
        self.hover_animation.stop()
        self.hover_animation.setStartValue(self.scale)
        self.hover_animation.setEndValue(1.02)
        self.hover_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hover_animation.stop()
        self.hover_animation.setStartValue(self.scale)
        self.hover_animation.setEndValue(1.0)
        self.hover_animation.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.click_animation.stop()
        self.click_animation.setStartValue(self.opacity)
        self.click_animation.setEndValue(0.95)
        self.click_animation.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.click_animation.stop()
        self.click_animation.setStartValue(self.opacity)
        self.click_animation.setEndValue(1.0)
        self.click_animation.start()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(self._opacity)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.rect().center())
        painter.scale(self._scale, self._scale)
        painter.translate(-self.rect().center())
        super().paintEvent(event)

class ModernInput(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(45)
        self.setFont(QFont("Segoe UI", 10))

        self.setStyleSheet(f"""
            ModernInput {{
                background-color: {COLORS['misc']['input_bg']};
                color: {COLORS['text']['primary']};
                border: 1px solid {COLORS['misc']['border']};
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 13px;
                selection-background-color: {COLORS['accent']['blue']};
            }}
            ModernInput:focus {{
                border: 1px solid {COLORS['accent']['blue']};
            }}
            ModernInput:hover {{
                border: 1px solid {COLORS['accent']['cyan']};
            }}
        """)

class OutputConsole(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Monospace", 9))

        self.setStyleSheet(f"""
            OutputConsole {{
                background-color: {COLORS['primary']['dark']};
                color: {COLORS['text']['secondary']};
                border: 1px solid {COLORS['misc']['border']};
                border-radius: 8px;
                padding: 10px;
                font-family: 'Monospace';
            }}
        """)

    def append_output(self, text, color=None):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)

        if color:
            self.setTextColor(QColor(color))
        else:
            self.setTextColor(QColor(COLORS['text']['secondary']))

        cursor.insertText(text + '\n')
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

class BuildWorker:
    def __init__(self, token, chat_id, signals):
        self.token = token.strip()
        self.chat_id = chat_id.strip()
        self.signals = signals
        self.stop_requested = False

    def run(self):
        try:
            self.signals.progress_updated.emit(5, "Подготовка к запуску сборочного скрипта...")

            build_script = "build.sh"

            if not os.path.isfile(build_script):
                raise FileNotFoundError(f"Скрипт сборки '{build_script}' не найден в текущей папке!")

            self.signals.output_received.emit("🚀 Запускаю build.sh с переданными параметрами...")
            self.signals.output_received.emit(f"   • Token: {self.token[:10]}...****")
            self.signals.output_received.emit(f"   • Chat ID: {self.chat_id}")

            cmd = [
                "bash",
                build_script,
                f"--token={self.token}",
                f"--id={self.chat_id}"
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            for line in iter(process.stdout.readline, ''):
                if self.stop_requested:
                    process.terminate()
                    self.signals.output_received.emit("⚠️ Сборка прервана пользователем")
                    break
                cleaned = line.rstrip()
                if cleaned:
                    self.signals.output_received.emit(cleaned)

            process.stdout.close()
            return_code = process.wait()

            self.signals.progress_updated.emit(100, "Сборка завершена")

            if return_code == 0:
                self.signals.output_received.emit("🎉 Сборка успешно завершена!")
                self.signals.build_finished.emit(True, "Приложение собрано и настроено")
            else:
                msg = f"Скрипт завершился с ошибкой (код возврата {return_code})"
                self.signals.output_received.emit("❌ " + msg)
                self.signals.build_finished.emit(False, msg)

        except FileNotFoundError as e:
            self.signals.output_received.emit(f"❌ {str(e)}")
            self.signals.build_finished.emit(False, str(e))
        except Exception as e:
            error_msg = f"Критическая ошибка при запуске сборки: {str(e)}"
            self.signals.output_received.emit("💥 " + error_msg)
            self.signals.build_finished.emit(False, error_msg)

    def stop(self):
        self.stop_requested = True

class RemoteAssistantCreator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.language_manager = LanguageManager()

        self.setWindowTitle(self.language_manager.get_text('app_title'))
        self.setFixedSize(750, 800)

        try:
            self.setWindowIcon(QtGui.QIcon('/usr/share/icons/en-os/start/logo.png'))
        except:
            pass

        self.build_thread = None
        self.build_worker = None
        self.signals = BuildSignals()

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        self.load_fonts()
        self.set_modern_theme()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(25, 25, 25, 20)
        main_layout.setSpacing(20)

        self.create_header(main_layout)

        self.create_input_section(main_layout)

        self.create_console_section(main_layout)

        self.create_progress_section(main_layout)

        self.create_buttons_section(main_layout)

    def create_header(self, parent_layout):
        header_layout = QHBoxLayout()

        self.header_label = QLabel(self.language_manager.get_text('header'))
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['accent']['blue']};
                font-size: 24px;
                font-weight: bold;
                padding: 15px;
                background-color: {COLORS['primary']['dark']};
                border-radius: 12px;
                border: 1px solid {COLORS['misc']['border']};
            }}
        """)
        self.header_label.setMinimumHeight(60)

        language_layout = QHBoxLayout()
        language_layout.setSpacing(8)

        self.language_combo = QComboBox()
        self.language_combo.addItem("EN", 'en')
        self.language_combo.addItem("RU", 'ru')
        self.language_combo.addItem("ES", 'es')
        self.language_combo.addItem("FR", 'fr')
        self.language_combo.addItem("DE", 'de')
        self.language_combo.addItem("简体中文", 'zh_CN')
        self.language_combo.addItem("日本語", 'ja')
        self.language_combo.addItem("한국어", 'ko')

        current_lang_code = {
            'en': "EN",
            'ru': "RU",
            'es': "ES",
            'fr': "FR",
            'de': "DE",
            'zh_CN':"简体中文",
            'ja':"日本語",
            'ko':"한국어",
        }.get(self.language_manager.current_language, "EN")
        self.language_combo.setCurrentText(current_lang_code)

        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        self.language_combo.setFixedSize(70, 35)
        self.language_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['primary']['medium']};
                color: {COLORS['text']['primary']};
                border: 1px solid {COLORS['misc']['border']};
                border-radius: 6px;
                padding: 5px;
                font-size: 12px;
                font-weight: bold;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 15px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {COLORS['text']['secondary']};
                width: 0px;
                height: 0px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['primary']['medium']};
                color: {COLORS['text']['primary']};
                border: 1px solid {COLORS['misc']['border']};
                border-radius: 6px;
                selection-background-color: {COLORS['accent']['blue']};
            }}
        """)

        language_layout.addWidget(self.language_combo)

        header_layout.addWidget(self.header_label)
        header_layout.addLayout(language_layout)

        parent_layout.addLayout(header_layout)

    def create_input_section(self, parent_layout):
        input_frame = QFrame()
        input_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['primary']['dark']};
                border: 2px solid {COLORS['misc']['border']};
                border-radius: 12px;
                padding: 0px;
            }}
        """)

        input_layout = QVBoxLayout(input_frame)
        input_layout.setSpacing(12)
        input_layout.setContentsMargins(20, 20, 20, 20)

        # Убираем рамки у текстовых меток
        self.token_label = QLabel(self.language_manager.get_text('token_label'))
        self.token_label.setStyleSheet(f"""
            color: {COLORS['text']['primary']};
            font-weight: bold;
            font-size: 13px;
            background: transparent;
            border: none;
        """)

        self.token_input = ModernInput(self.language_manager.get_text('token_placeholder'))

        # Убираем рамки у текстовых меток
        self.id_label = QLabel(self.language_manager.get_text('id_label'))
        self.id_label.setStyleSheet(f"""
            color: {COLORS['text']['primary']};
            font-weight: bold;
            font-size: 13px;
            background: transparent;
            border: none;
        """)

        self.id_input = ModernInput(self.language_manager.get_text('id_placeholder'))

        input_layout.addWidget(self.token_label)
        input_layout.addWidget(self.token_input)
        input_layout.addWidget(self.id_label)
        input_layout.addWidget(self.id_input)

        parent_layout.addWidget(input_frame)

    def create_console_section(self, parent_layout):
        self.console_label = QLabel(self.language_manager.get_text('console_label'))
        self.console_label.setStyleSheet(f"color: {COLORS['text']['primary']}; font-weight: bold; font-size: 13px;")
        parent_layout.addWidget(self.console_label)

        self.console = OutputConsole()
        self.console.setMinimumHeight(200)
        parent_layout.addWidget(self.console)

    def create_progress_section(self, parent_layout):
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {COLORS['misc']['border']};
                border-radius: 8px;
                text-align: center;
                background-color: {COLORS['primary']['dark']};
                color: {COLORS['text']['primary']};
                font-weight: bold;
                height: 25px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 {COLORS['accent']['green']},
                    stop: 1 {COLORS['accent']['cyan']});
                border-radius: 6px;
            }}
        """)
        self.progress_bar.setVisible(False)
        parent_layout.addWidget(self.progress_bar)

    def create_buttons_section(self, parent_layout):
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        self.build_btn = MinimalButton(self.language_manager.get_text('build_btn'), color_scheme='green')
        self.build_btn.clicked.connect(self.start_build_process)

        self.clear_btn = MinimalButton(self.language_manager.get_text('clear_btn'), color_scheme='purple')
        self.clear_btn.clicked.connect(self.clear_console)

        self.help_btn = MinimalButton(self.language_manager.get_text('help_btn'), color_scheme='blue')
        self.help_btn.clicked.connect(self.show_instructions)

        buttons_layout.addWidget(self.build_btn)
        buttons_layout.addWidget(self.clear_btn)
        buttons_layout.addWidget(self.help_btn)

        parent_layout.addLayout(buttons_layout)

    def connect_signals(self):
        self.signals.output_received.connect(self.on_output_received)
        self.signals.progress_updated.connect(self.on_progress_updated)
        self.signals.build_finished.connect(self.on_build_finished)

    def on_language_changed(self):
        language_code = self.language_combo.currentData()
        if self.language_manager.set_language(language_code):
            self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(self.language_manager.get_text('app_title'))
        self.header_label.setText(self.language_manager.get_text('header'))
        self.token_label.setText(self.language_manager.get_text('token_label'))
        self.token_input.setPlaceholderText(self.language_manager.get_text('token_placeholder'))
        self.id_label.setText(self.language_manager.get_text('id_label'))
        self.id_input.setPlaceholderText(self.language_manager.get_text('id_placeholder'))
        self.console_label.setText(self.language_manager.get_text('console_label'))
        self.build_btn.setText(self.language_manager.get_text('build_btn'))
        self.clear_btn.setText(self.language_manager.get_text('clear_btn'))
        self.help_btn.setText(self.language_manager.get_text('help_btn'))

    def load_fonts(self):
        try:
            font_id = QFontDatabase.addApplicationFont("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
            if font_id != -1:
                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                app_font = QFont(font_family, 9)
                QApplication.setFont(app_font)
        except:
            pass

    def set_modern_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(COLORS['primary']['dark']))
        palette.setColor(QPalette.WindowText, QColor(COLORS['text']['primary']))
        palette.setColor(QPalette.Base, QColor(COLORS['primary']['medium']))
        palette.setColor(QPalette.AlternateBase, QColor(COLORS['primary']['light']))
        palette.setColor(QPalette.ToolTipBase, QColor(COLORS['primary']['dark']))
        palette.setColor(QPalette.ToolTipText, QColor(COLORS['text']['primary']))
        palette.setColor(QPalette.Text, QColor(COLORS['text']['primary']))
        palette.setColor(QPalette.Button, QColor(COLORS['primary']['medium']))
        palette.setColor(QPalette.ButtonText, QColor(COLORS['text']['primary']))
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Highlight, QColor(COLORS['accent']['blue']))
        palette.setColor(QPalette.HighlightedText, Qt.white)

        self.setPalette(palette)

        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {COLORS['primary']['dark']},
                    stop: 1 #0a0a1a);
                border: none;
            }}
        """)

    def start_build_process(self):
        token = self.token_input.text().strip()
        chat_id = self.id_input.text().strip()

        if not token or not chat_id:
            self.show_error_message(self.language_manager.get_text('error_fields'))
            return

        if self.build_thread and self.build_thread.is_alive():
            self.console.append_output(self.language_manager.get_text('error_build_running'))
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.build_btn.setEnabled(False)
        self.console.clear()

        self.build_worker = BuildWorker(token, chat_id, self.signals)
        self.build_thread = threading.Thread(target=self.build_worker.run)
        self.build_thread.daemon = True
        self.build_thread.start()

    def on_output_received(self, text):
        self.console.append_output(text)

    def on_progress_updated(self, value, message):
        self.progress_bar.setValue(value)
        self.console.append_output(message)

    def on_build_finished(self, success, message):
        self.progress_bar.setValue(100)
        self.build_btn.setEnabled(True)

        if success:
            self.console.append_output("🎉 " + message, COLORS['misc']['success'])
        else:
            self.console.append_output("❌ " + message, COLORS['misc']['error'])

    def clear_console(self):
        self.console.clear()

    def show_instructions(self):
        self.console.clear()
        self.console.append_output(self.language_manager.get_text('instructions'), COLORS['accent']['cyan'])

    def show_error_message(self, message):
        self.console.append_output("❌ " + message, COLORS['misc']['error'])

    def closeEvent(self, event):
        if self.build_thread and self.build_thread.is_alive():
            reply = QMessageBox.question(self, "Build in progress",
                                       "Build is still running. Are you sure you want to quit?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                event.ignore()
                return
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Remote Assistant Creator")
    app.setApplicationVersion("2.0")

    window = RemoteAssistantCreator()
    window.show()

    sys.exit(app.exec_())
