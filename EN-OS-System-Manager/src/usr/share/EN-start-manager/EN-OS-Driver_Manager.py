#!/usr/bin/env python3
import sys
import os
import subprocess
import threading
import re
import json
import locale
import time
from pathlib import Path
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFrame,
                             QTextEdit, QProgressBar, QMessageBox, QCheckBox, QComboBox,
                             QInputDialog)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSignal, QObject
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor, QPainter, QFontDatabase, QTextCursor)

os.environ['XDG_RUNTIME_DIR'] = '/tmp/runtime-root'

LOCALES = {
    'en': {
        'app_title': 'EN-OS Driver Manager',
        'header': '🛠️ EN-OS Driver Manager',
        'hardware_detection': 'Hardware Detection',
        'detecting_hardware': 'Detecting graphics cards...',
        'driver_installation': 'Driver Installation',
        'system_update': 'Update system before installation',
        'nomodeset': 'Add nomodeset to GRUB (fix graphics issues)',
        'install_nvidia': '🟢 Install NVIDIA Drivers',
        'install_amd': '🔵 Install AMD Drivers',
        'install_intel': '🟡 Install Intel Drivers',
        'console_output': 'Installation Output:',
        'install_btn': '✔️ Start Installation',
        'clear_btn': '🗑️ Clear Output',
        'language': 'Language',
        'error_title': 'Error',
        'success_title': 'Success',
        'confirm_install': 'Confirm Installation',
        'install_confirm_msg': 'Install {} drivers? This may take several minutes.',
        'operation_started': 'Operation started...',
        'operation_completed': 'Operation completed successfully!',
        'operation_failed': 'Operation failed!',
        'no_drivers_selected': 'Please select at least one driver to install',
        'hardware_info': 'Detected Graphics Cards:',
        'gpu_detected': 'GPU detected:',
        'no_gpu_detected': 'No compatible graphics cards detected',
        'need_root': 'Root access required',
        'need_root_msg': 'This operation requires root privileges. Please enter your password.',
        'install_success': 'Drivers installed successfully!',
        'install_failed': 'Driver installation failed'
    },
    'ru': {
        'app_title': 'EN-OS Driver Manager',
        'header': '🛠️ EN-OS Driver Manager',
        'hardware_detection': 'Обнаружение оборудования',
        'detecting_hardware': 'Определение видеокарт...',
        'driver_installation': 'Установка драйверов',
        'system_update': 'Обновить систему перед установкой (иногда разрешает конфликты пакетов)',
        'nomodeset': 'Добавить nomodeset в GRUB (решение проблем с графикой)',
        'install_nvidia': '🟢 Установить драйверы NVIDIA',
        'install_amd': '🟢 Установить драйверы AMD',
        'install_intel': '🟡 Установить драйверы Intel',
        'console_output': 'Вывод установки:',
        'install_btn': '✔️ Начать установку',
        'clear_btn': '🗑️ Очистить вывод',
        'language': 'Язык',
        'error_title': 'Ошибка',
        'success_title': 'Успех',
        'confirm_install': 'Подтверждение установки',
        'install_confirm_msg': 'Установить драйверы {}? Это может занять несколько минут.',
        'operation_started': 'Операция запущена...',
        'operation_completed': 'Операция успешно завершена!',
        'operation_failed': 'Операция не удалась!',
        'no_drivers_selected': 'Пожалуйста, выберите хотя бы один драйвер для установки',
        'hardware_info': 'Обнаруженные видеокарты:',
        'gpu_detected': 'Видеокарта обнаружена:',
        'no_gpu_detected': 'Совместимые видеокарты не обнаружены',
        'need_root': 'Требуются права sudo',
        'need_root_msg': 'Эта операция требует прав sudo. Пожалуйста, введите ваш пароль.',
        'install_success': 'Драйверы успешно установлены!',
        'install_failed': 'Ошибка установки драйверов'
    },
    'es': {
        'app_title': 'Gestor de Controladores EN-OS',
        'header': '🛠️ Gestor de Controladores EN-OS',
        'hardware_detection': 'Detección de Hardware',
        'detecting_hardware': 'Detectando tarjetas gráficas...',
        'driver_installation': 'Instalación de Controladores',
        'system_update': 'Actualizar el sistema antes de la instalación',
        'nomodeset': 'Añadir nomodeset a GRUB (soluciona problemas gráficos)',
        'install_nvidia': '🟢 Instalar controladores NVIDIA',
        'install_amd': '🔵 Instalar controladores AMD',
        'install_intel': '🟡 Instalar controladores Intel',
        'console_output': 'Salida de instalación:',
        'install_btn': '✔️ Iniciar Instalación',
        'clear_btn': '🗑️ Limpiar Salida',
        'language': 'Idioma',
        'error_title': 'Error',
        'success_title': 'Éxito',
        'confirm_install': 'Confirmar Instalación',
        'install_confirm_msg': '¿Instalar controladores {}? Esto puede tomar varios minutos.',
        'operation_started': 'Operación iniciada...',
        'operation_completed': '¡Operación completada con éxito!',
        'operation_failed': '¡La operación falló!',
        'no_drivers_selected': 'Por favor, selecciona al menos un controlador para instalar',
        'hardware_info': 'Tarjetas Gráficas Detectadas:',
        'gpu_detected': 'GPU detectada:',
        'no_gpu_detected': 'No se detectaron tarjetas gráficas compatibles',
        'need_root': 'Se requieren privilegios de root',
        'need_root_msg': 'Esta operación requiere privilegios de administrador. Por favor, introduce tu contraseña.',
        'install_success': '¡Controladores instalados correctamente!',
        'install_failed': 'Fallo al instalar los controladores'
    },
    'fr': {
        'app_title': 'Gestionnaire de pilotes EN-OS',
        'header': '🛠️ Gestionnaire de pilotes EN-OS',
        'hardware_detection': 'Détection du matériel',
        'detecting_hardware': 'Détection des cartes graphiques...',
        'driver_installation': 'Installation des pilotes',
        'system_update': 'Mettre à jour le système avant l\'installation',
        'nomodeset': 'Ajouter nomodeset à GRUB (résout les problèmes graphiques)',
        'install_nvidia': '🟢 Installer les pilotes NVIDIA',
        'install_amd': '🔵 Installer les pilotes AMD',
        'install_intel': '🟡 Installer les pilotes Intel',
        'console_output': 'Sortie d\'installation :',
        'install_btn': '✔️ Démarrer l\'installation',
        'clear_btn': '🗑️ Effacer la sortie',
        'language': 'Langue',
        'error_title': 'Erreur',
        'success_title': 'Succès',
        'confirm_install': 'Confirmer l\'installation',
        'install_confirm_msg': 'Installer les pilotes {} ? Cela peut prendre plusieurs minutes.',
        'operation_started': 'Opération démarrée...',
        'operation_completed': 'Opération terminée avec succès !',
        'operation_failed': 'L\'opération a échoué !',
        'no_drivers_selected': 'Veuillez sélectionner au moins un pilote à installer',
        'hardware_info': 'Cartes graphiques détectées :',
        'gpu_detected': 'GPU détecté :',
        'no_gpu_detected': 'Aucune carte graphique compatible détectée',
        'need_root': 'Privilèges root requis',
        'need_root_msg': 'Cette opération nécessite des privilèges d\'administrateur. Veuillez entrer votre mot de passe.',
        'install_success': 'Pilotes installés avec succès !',
        'install_failed': 'Échec de l\'installation des pilotes'
    },
    'de': {
        'app_title': 'EN-OS Treiber-Manager',
        'header': '🛠️ EN-OS Treiber-Manager',
        'hardware_detection': 'Hardware-Erkennung',
        'detecting_hardware': 'Grafikkarten werden erkannt...',
        'driver_installation': 'Treiberinstallation',
        'system_update': 'System vor der Installation aktualisieren',
        'nomodeset': 'nomodeset zu GRUB hinzufügen (behebt Grafikprobleme)',
        'install_nvidia': '🟢 NVIDIA-Treiber installieren',
        'install_amd': '🔵 AMD-Treiber installieren',
        'install_intel': '🟡 Intel-Treiber installieren',
        'console_output': 'Installationsausgabe:',
        'install_btn': '✔️ Installation starten',
        'clear_btn': '🗑️ Ausgabe löschen',
        'language': 'Sprache',
        'error_title': 'Fehler',
        'success_title': 'Erfolg',
        'confirm_install': 'Installation bestätigen',
        'install_confirm_msg': '{} Treiber installieren? Dies kann mehrere Minuten dauern.',
        'operation_started': 'Vorgang gestartet...',
        'operation_completed': 'Vorgang erfolgreich abgeschlossen!',
        'operation_failed': 'Vorgang fehlgeschlagen!',
        'no_drivers_selected': 'Bitte wählen Sie mindestens einen Treiber zur Installation aus',
        'hardware_info': 'Erkannte Grafikkarten:',
        'gpu_detected': 'GPU erkannt:',
        'no_gpu_detected': 'Keine kompatiblen Grafikkarten erkannt',
        'need_root': 'Root-Rechte erforderlich',
        'need_root_msg': 'Diese Operation erfordert Root-Rechte. Bitte geben Sie Ihr Passwort ein.',
        'install_success': 'Treiber erfolgreich installiert!',
        'install_failed': 'Treiberinstallation fehlgeschlagen'
    },
    'zh_CN': {
        'app_title': 'EN-OS 驱动管理器',
        'header': '🛠️ EN-OS 驱动管理器',
        'hardware_detection': '硬件检测',
        'detecting_hardware': '正在检测显卡...',
        'driver_installation': '驱动安装',
        'system_update': '安装前更新系统',
        'nomodeset': '在 GRUB 中添加 nomodeset（修复图形问题）',
        'install_nvidia': '🟢 安装 NVIDIA 驱动',
        'install_amd': '🔵 安装 AMD 驱动',
        'install_intel': '🟡 安装 Intel 驱动',
        'console_output': '安装输出：',
        'install_btn': '✔️ 开始安装',
        'clear_btn': '🗑️ 清除输出',
        'language': '语言',
        'error_title': '错误',
        'success_title': '成功',
        'confirm_install': '确认安装',
        'install_confirm_msg': '是否安装 {} 驱动？此过程可能需要几分钟。',
        'operation_started': '操作开始...',
        'operation_completed': '操作成功完成！',
        'operation_failed': '操作失败！',
        'no_drivers_selected': '请选择至少一个要安装的驱动',
        'hardware_info': '检测到的显卡：',
        'gpu_detected': '检测到显卡：',
        'no_gpu_detected': '未检测到兼容的显卡',
        'need_root': '需要 root 权限',
        'need_root_msg': '此操作需要管理员权限。请输入您的密码。',
        'install_success': '驱动安装成功！',
        'install_failed': '驱动安装失败'
    },
    'ja': {
        'app_title': 'EN-OS ドライバーマネージャー',
        'header': '🛠️ EN-OS ドライバーマネージャー',
        'hardware_detection': 'ハードウェア検出',
        'detecting_hardware': 'グラフィックカードを検出中...',
        'driver_installation': 'ドライバーインストール',
        'system_update': 'インストール前にシステムを更新',
        'nomodeset': 'GRUB に nomodeset を追加（グラフィック問題の修正）',
        'install_nvidia': '🟢 NVIDIA ドライバーをインストール',
        'install_amd': '🔵 AMD ドライバーをインストール',
        'install_intel': '🟡 Intel ドライバーをインストール',
        'console_output': 'インストール出力：',
        'install_btn': '✔️ インストール開始',
        'clear_btn': '🗑️ 出力クリア',
        'language': '言語',
        'error_title': 'エラー',
        'success_title': '成功',
        'confirm_install': 'インストールの確認',
        'install_confirm_msg': '{} ドライバーをインストールしますか？数分かかる可能性があります。',
        'operation_started': '操作を開始しました...',
        'operation_completed': '操作が正常に完了しました！',
        'operation_failed': '操作に失敗しました！',
        'no_drivers_selected': 'インストールするドライバーを少なくとも1つ選択してください',
        'hardware_info': '検出されたグラフィックカード：',
        'gpu_detected': 'GPU検出：',
        'no_gpu_detected': '互換性のあるグラフィックカードが見つかりません',
        'need_root': 'root権限が必要です',
        'need_root_msg': 'この操作には管理者権限が必要です。パスワードを入力してください。',
        'install_success': 'ドライバーのインストールに成功しました！',
        'install_failed': 'ドライバーのインストールに失敗しました'
    },
    'ko': {
        'app_title': 'EN-OS 드라이버 매니저',
        'header': '🛠️ EN-OS 드라이버 매니저',
        'hardware_detection': '하드웨어 감지',
        'detecting_hardware': '그래픽 카드 감지 중...',
        'driver_installation': '드라이버 설치',
        'system_update': '설치 전 시스템 업데이트',
        'nomodeset': 'GRUB에 nomodeset 추가 (그래픽 문제 해결)',
        'install_nvidia': '🟢 NVIDIA 드라이버 설치',
        'install_amd': '🔵 AMD 드라이버 설치',
        'install_intel': '🟡 Intel 드라이버 설치',
        'console_output': '설치 출력:',
        'install_btn': '✔️ 설치 시작',
        'clear_btn': '🗑️ 출력 지우기',
        'language': '언어',
        'error_title': '오류',
        'success_title': '성공',
        'confirm_install': '설치 확인',
        'install_confirm_msg': '{} 드라이버를 설치하시겠습니까? 몇 분 정도 걸릴 수 있습니다.',
        'operation_started': '작업 시작...',
        'operation_completed': '작업이 성공적으로 완료되었습니다!',
        'operation_failed': '작업 실패!',
        'no_drivers_selected': '설치할 드라이버를 하나 이상 선택해 주세요',
        'hardware_info': '감지된 그래픽 카드:',
        'gpu_detected': 'GPU 감지됨:',
        'no_gpu_detected': '호환되는 그래픽 카드가 감지되지 않음',
        'need_root': '루트 권한 필요',
        'need_root_msg': '이 작업에는 관리자 권한이 필요합니다. 비밀번호를 입력해 주세요.',
        'install_success': '드라이버 설치 성공!',
        'install_failed': '드라이버 설치 실패'
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

class DriverSignals(QObject):
    output_received = pyqtSignal(str)
    progress_updated = pyqtSignal(int, str)
    installation_finished = pyqtSignal(bool, str)

class MinimalButton(QPushButton):
    def __init__(self, text, icon=None, color_scheme='blue', parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(50)
        self.setFont(QFont("Segoe UI", 11, QFont.Bold))

        self._opacity = 1.0
        self._scale = 1.0
        self.color_scheme = color_scheme

        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(22, 22))

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
                padding: 12px 18px;
                text-align: center;
                font-weight: bold;
                font-size: 12px;
            }}
            MinimalButton:hover {{
                background-color: {color['hover']};
                border: 1px solid {color['text']};
            }}
            MinimalButton:pressed {{
                background-color: {color['bg']};
                border: 1px solid {color['text']};
            }}
            MinimalButton:checked {{
                background-color: {color['text']};
                color: {COLORS['primary']['dark']};
                border: 1px solid {color['text']};
            }}
            MinimalButton:disabled {{
                background-color: {COLORS['primary']['medium']};
                color: {COLORS['text']['muted']};
                border: 1px solid {COLORS['misc']['border']};
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

class DriverInstaller:
    def __init__(self, signals, update_system=False, install_nomodeset=False, sudo_password=None, nvidia_model=None):
        self.signals = signals
        self.update_system = update_system
        self.install_nomodeset = install_nomodeset
        self.stop_requested = False
        self.sudo_password = sudo_password
        self.nvidia_model = nvidia_model

    def run_sudo_command(self, command, description=""):
        try:
            if description:
                self.signals.output_received.emit(f"🔧 {description}...")

            full_command = ["sudo", "-S"] + command
            input_text = (self.sudo_password + '\n') if self.sudo_password else '\n'

            result = subprocess.run(
                full_command,
                input=input_text,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                if description:
                    self.signals.output_received.emit(f"✔️ {description} completed")
                return True
            else:
                stderr = result.stderr.strip()
                self.signals.output_received.emit(f"❌ {description} failed: {stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.signals.output_received.emit(f"❌ {description} timed out")
            return False
        except Exception as e:
            self.signals.output_received.emit(f"❌ {description} error: {str(e)}")
            return False

    def wait_for_pacman_lock(self):
        lock_file = "/var/lib/pacman/db.lck"
        max_wait = 30
        wait_time = 0

        while os.path.exists(lock_file) and wait_time < max_wait:
            self.signals.output_received.emit("⏳ Waiting for pacman database to unlock...")
            time.sleep(2)
            wait_time += 2

        if os.path.exists(lock_file):
            self.run_sudo_command(["rm", "-f", lock_file], "Remove database lock")

    def install_drivers(self, driver_types):
        try:
            self.wait_for_pacman_lock()

            if self.update_system:
                self.signals.progress_updated.emit(10, "🟢 Updating system...")
                if not self.run_sudo_command(["pacman", "-Syu", "--noconfirm"], "Update system"):
                    self.signals.installation_finished.emit(False, "System update failed")
                    return

            installed_count = 0
            total_drivers = len(driver_types)

            for i, driver_type in enumerate(driver_types):
                progress = 20 + (i * 60 // total_drivers)
                self.signals.progress_updated.emit(progress, f"📦 Installing {driver_type} drivers...")

                if self.install_driver_packages(driver_type):
                    installed_count += 1
                else:
                    self.signals.output_received.emit(f"⚠️ Skipping {driver_type} due to installation failure")

            if installed_count > 0:
                self.signals.progress_updated.emit(85, "🟢 Updating initramfs...")
                self.run_sudo_command(["mkinitcpio", "-P"], "Update initramfs")

                if self.install_nomodeset:
                    self.signals.progress_updated.emit(90, "🛠️ Configuring GRUB...")
                    self.configure_grub()

            self.signals.progress_updated.emit(100, "🛠️ Installation completed!")
            success_msg = f"Successfully installed {installed_count}/{total_drivers} driver packages"
            self.signals.installation_finished.emit(True, success_msg)

        except Exception as e:
            self.signals.output_received.emit(f"❌ Installation error: {str(e)}")
            self.signals.installation_finished.emit(False, f"Installation failed: {str(e)}")


    def install_driver_packages(self, driver_type):
        repo_packages = []

        if driver_type == 'nvidia':
            if self.nvidia_model is None:
                self.signals.output_received.emit("⚠️ No NVIDIA model detected")
                return False

            match = re.search(r'(RTX|GTX|GT)\s*(\d+)', self.nvidia_model, re.I)
            if match:
                prefix = match.group(1).upper()
                series_num = int(match.group(2))

                if prefix == 'RTX' or series_num >= 1650:
                    repo_packages = [
                        'nvidia-open-dkms',
                        'nvidia-utils',
                        'nvidia-settings',
                        'vulkan-icd-loader',
                        'vulkan-tools'
                    ]

                elif series_num >= 900:
                    repo_packages = [
                        'nvidia-580xx-dkms',
                        'nvidia-580xx-utils',
                        'nvidia-settings',
                        'lib32-nvidia-580xx-utils',
                        'vulkan-icd-loader',
                        'vulkan-tools'
                    ]

                elif series_num >= 600:
                    repo_packages = [
                        'nvidia-470xx-dkms',
                        'nvidia-470xx-utils',
                        'nvidia-settings',
                        'lib32-nvidia-470xx-utils',
                        'vulkan-icd-loader',
                        'vulkan-tools'
                    ]

                elif series_num >= 400:
                    repo_packages = [
                        'nvidia-390xx-dkms',
                        'nvidia-390xx-utils',
                        'lib32-nvidia-390xx-utils',
                        'nvidia-settings',
                        'vulkan-icd-loader',
                        'vulkan-tools'
                    ]

                else:
                    self.signals.output_received.emit(
                        "❌ Ваша видеокарта слишком старая (до Fermi).\n"
                        "Проприетарные драйверы NVIDIA больше не поддерживаются.\n"
                        "Рекомендуется использовать открытый драйвер nouveau."
                    )
                    return False

            else:
                repo_packages = [
                    'nvidia-open-dkms',
                    'nvidia-utils',
                    'nvidia-settings',
                    'vulkan-icd-loader',
                    'vulkan-tools'
                ]

        elif driver_type == 'amd':
            repo_packages = [
                'mesa', 'lib32-mesa',
                'vulkan-radeon', 'lib32-vulkan-radeon',
                'libva-mesa-driver',
                'mesa-vdpau'
            ]

        elif driver_type == 'intel':
            repo_packages = [
                'mesa', 'lib32-mesa',
                'vulkan-intel', 'lib32-vulkan-intel',
                'intel-media-driver'
            ]

        if not repo_packages:
            self.signals.output_received.emit(f"⚠️ Unknown driver type or GPU: {driver_type}")
            return False

        all_packages = repo_packages
        self.signals.output_received.emit(
            f"📦 Selected packages for {driver_type}: {', '.join(all_packages)}"
        )

        self.run_sudo_command(["pacman-key", "--init"], "Init pacman key")
        self.run_sudo_command(["pacman-key", "--populate", "archlinux"], "Populate pacman key")

        self.signals.output_received.emit("📦 Installing packages from repositories...")
        if not self.run_sudo_command(
            ["pacman", "-S", "--noconfirm"] + all_packages,
            "Install NVIDIA driver packages"
        ):
            self.signals.output_received.emit("❌ Failed to install some packages")
            return False

        self.signals.output_received.emit("✅ Driver installation completed successfully")
        return True



    def configure_grub(self):
        self.signals.output_received.emit("🛠️ Configuring GRUB...")

        self.run_sudo_command(
            ["cp", "/etc/default/grub", "/etc/default/grub.backup"],
            "Backup GRUB config"
        )

        try:
            with open("/etc/default/grub", "r") as f:
                grub_content = f.read()
        except Exception as e:
            self.signals.output_received.emit(f"❌ Cannot read /etc/default/grub: {e}")
            return False

        cmdline_match = re.search(r'^GRUB_CMDLINE_LINUX_DEFAULT="([^"]*)"', grub_content, re.MULTILINE)

        if not cmdline_match:
            self.signals.output_received.emit("❌ Не найдена строка GRUB_CMDLINE_LINUX_DEFAULT")
            return False

        current_params = cmdline_match.group(1).strip()
        params_list = current_params.split()

        if "nomodeset" in params_list:
            self.signals.output_received.emit("ℹ️ Параметр nomodeset уже присутствует в GRUB")
            return True

        params_list.insert(0, "nomodeset")
        new_cmdline = ' '.join(params_list)

        sed_pattern = f's/GRUB_CMDLINE_LINUX_DEFAULT="[^"]*"/GRUB_CMDLINE_LINUX_DEFAULT="{new_cmdline}"/'

        result = self.run_sudo_command(
            ["sed", "-i", sed_pattern, "/etc/default/grub"],
            "Add nomodeset to GRUB_CMDLINE_LINUX_DEFAULT"
        )

        if not result:
            self.signals.output_received.emit("❌ Не удалось добавить nomodeset в GRUB")
            return False

        self.run_sudo_command(
            ["grub-mkconfig", "-o", "/boot/grub/grub.cfg"],
            "Update GRUB configuration"
        )

        self.signals.output_received.emit("✅ nomodeset успешно добавлен в параметры загрузки")
        return True

class DriverManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.language_manager = LanguageManager()

        self.setWindowTitle(self.language_manager.get_text('app_title'))
        self.setFixedSize(800, 800)

        try:
            self.setWindowIcon(QtGui.QIcon('/usr/share/EN-start-manager/icons/icon.png'))
        except:
            pass

        self.install_thread = None
        self.detected_gpus = []
        self.signals = DriverSignals()
        self.nvidia_model = None

        self.setup_ui()
        self.connect_signals()
        self.detect_hardware()

    def setup_ui(self):
        self.load_fonts()
        self.set_modern_theme()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 15)
        main_layout.setSpacing(15)

        self.create_header(main_layout)
        self.create_hardware_section(main_layout)
        self.create_driver_selection_section(main_layout)
        self.create_console_section(main_layout)
        self.create_progress_section(main_layout)
        self.create_action_buttons(main_layout)

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

    def create_hardware_section(self, parent_layout):
        hardware_frame = QFrame()
        hardware_frame.setStyleSheet(f"""
            QFrame {{
        background-color: #111123;
        border: none;
        border-radius: 12px;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.3);}}
        """)


        hardware_layout = QVBoxLayout(hardware_frame)
        hardware_layout.setSpacing(10)
        hardware_layout.setContentsMargins(15, 15, 15, 15)

        hardware_title = QLabel(self.language_manager.get_text('hardware_detection'))
        hardware_title.setStyleSheet(f"color: {COLORS['accent']['purple']}; font-weight: bold; font-size: 14px;")
        hardware_layout.addWidget(hardware_title)

        self.hardware_info = QLabel(self.language_manager.get_text('detecting_hardware'))
        self.hardware_info.setStyleSheet(f"color: {COLORS['text']['secondary']}; font-size: 11px;")
        self.hardware_info.setWordWrap(True)
        hardware_layout.addWidget(self.hardware_info)

        parent_layout.addWidget(hardware_frame)

    def create_driver_selection_section(self, parent_layout):
        driver_frame = QFrame()
        driver_frame.setStyleSheet(f"""
        QFrame {{
        background-color: #111123;
        border: none;
        border-radius: 12px;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.3);}}
        """)

        driver_layout = QVBoxLayout(driver_frame)
        driver_layout.setSpacing(12)
        driver_layout.setContentsMargins(15, 15, 15, 15)

        driver_title = QLabel(self.language_manager.get_text('driver_installation'))
        driver_title.setStyleSheet(f"color: {COLORS['accent']['green']}; font-weight: bold; font-size: 14px;")
        driver_layout.addWidget(driver_title)

        options_layout = QHBoxLayout()

        self.update_checkbox = QCheckBox(self.language_manager.get_text('system_update'))
        self.update_checkbox.setChecked(False)
        self.update_checkbox.setStyleSheet(f"color: {COLORS['text']['secondary']}; font-size: 11px;")
        options_layout.addWidget(self.update_checkbox)

        self.nomodeset_checkbox = QCheckBox(self.language_manager.get_text('nomodeset'))
        self.nomodeset_checkbox.setChecked(False)
        self.nomodeset_checkbox.setStyleSheet(f"color: {COLORS['text']['secondary']}; font-size: 11px;")
        options_layout.addWidget(self.nomodeset_checkbox)

        options_layout.addStretch()
        driver_layout.addLayout(options_layout)

        driver_buttons_layout = QHBoxLayout()
        driver_buttons_layout.setSpacing(10)

        self.nvidia_btn = MinimalButton(self.language_manager.get_text('install_nvidia'), color_scheme='green')
        self.nvidia_btn.setCheckable(True)
        self.nvidia_btn.setEnabled(False)
        driver_buttons_layout.addWidget(self.nvidia_btn)

        self.amd_btn = MinimalButton(self.language_manager.get_text('install_amd'), color_scheme='blue')
        self.amd_btn.setCheckable(True)
        self.amd_btn.setEnabled(False)
        driver_buttons_layout.addWidget(self.amd_btn)

        self.intel_btn = MinimalButton(self.language_manager.get_text('install_intel'), color_scheme='cyan')
        self.intel_btn.setCheckable(True)
        self.intel_btn.setEnabled(False)
        driver_buttons_layout.addWidget(self.intel_btn)

        self.nvidia_btn.toggled.connect(lambda checked: self.on_driver_toggle('NVIDIA', checked))
        self.amd_btn.toggled.connect(lambda checked: self.on_driver_toggle('AMD', checked))
        self.intel_btn.toggled.connect(lambda checked: self.on_driver_toggle('Intel', checked))


        driver_layout.addLayout(driver_buttons_layout)
        parent_layout.addWidget(driver_frame)

    def on_driver_toggle(self, driver_name, checked):
        lang = self.language_manager.current_language
        if lang == 'ru':
            msg = f"✅ Вы выбрали драйвер {driver_name}" if checked else f"❌ Вы убрали драйвер {driver_name}"
        else:
            msg = f"✅ {driver_name} driver selected" if checked else f"❌ {driver_name} driver deselected"
        self.console.append_output(msg)



    def create_console_section(self, parent_layout):
        console_label = QLabel(self.language_manager.get_text('console_output'))
        console_label.setStyleSheet(f"color: {COLORS['text']['primary']}; font-weight: bold; font-size: 13px;")
        parent_layout.addWidget(console_label)

        self.console = OutputConsole()
        self.console.setMinimumHeight(150)
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

    def create_action_buttons(self, parent_layout):
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        self.install_btn = MinimalButton(self.language_manager.get_text('install_btn'), color_scheme='green')
        self.install_btn.clicked.connect(self.start_installation)
        self.install_btn.setEnabled(False)
        buttons_layout.addWidget(self.install_btn)

        self.clear_btn = MinimalButton(self.language_manager.get_text('clear_btn'), color_scheme='purple')
        self.clear_btn.clicked.connect(self.clear_console)
        buttons_layout.addWidget(self.clear_btn)

        buttons_layout.addStretch()
        parent_layout.addLayout(buttons_layout)

    def connect_signals(self):
        self.signals.output_received.connect(self.on_output_received)
        self.signals.progress_updated.connect(self.on_progress_updated)
        self.signals.installation_finished.connect(self.on_installation_finished)

    def on_language_changed(self):
        language_code = self.language_combo.currentData()
        if self.language_manager.set_language(language_code):
            self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(self.language_manager.get_text('app_title'))
        self.header_label.setText(self.language_manager.get_text('header'))

        self.hardware_info.setText(self.language_manager.get_text('detecting_hardware'))

        self.nvidia_btn.setText(self.language_manager.get_text('install_nvidia'))
        self.amd_btn.setText(self.language_manager.get_text('install_amd'))
        self.intel_btn.setText(self.language_manager.get_text('install_intel'))

        self.install_btn.setText(self.language_manager.get_text('install_btn'))
        self.clear_btn.setText(self.language_manager.get_text('clear_btn'))

        self.update_checkbox.setText(self.language_manager.get_text('system_update'))
        self.nomodeset_checkbox.setText(self.language_manager.get_text('nomodeset'))

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

    def detect_hardware(self):
        try:
            hardware_info = f"🔍 {self.language_manager.get_text('hardware_info')}\n\n"
            self.detected_gpus = []

            result = subprocess.run(["lspci", "-nn"], capture_output=True, text=True, timeout=10)
            output = result.stdout

            nvidia_ids = ['10de']
            amd_ids = ['1002', '1022']
            intel_ids = ['8086']

            self.nvidia_btn.setEnabled(False)
            self.amd_btn.setEnabled(False)
            self.intel_btn.setEnabled(False)

            for line in output.split('\n'):
                if any(x in line for x in ['VGA', '3D', 'Display']):
                    device_ids = re.findall(r'\[([0-9a-f]{4}:[0-9a-f]{4})\]', line)
                    for device_id in device_ids:
                        vendor_id = device_id.split(':')[0]
                        model = re.sub(r'.*\[.*\]:\s*', '', line).strip()

                        if vendor_id in nvidia_ids:
                            hardware_info += f"• {self.language_manager.get_text('gpu_detected')} NVIDIA: {model}\n"
                            if 'nvidia' not in self.detected_gpus:
                                self.detected_gpus.append('nvidia')
                            self.nvidia_model = model
                            self.nvidia_btn.setEnabled(True)
                        elif vendor_id in amd_ids:
                            hardware_info += f"• {self.language_manager.get_text('gpu_detected')} AMD: {model}\n"
                            if 'amd' not in self.detected_gpus:
                                self.detected_gpus.append('amd')
                            self.amd_btn.setEnabled(True)
                        elif vendor_id in intel_ids:
                            hardware_info += f"• {self.language_manager.get_text('gpu_detected')} Intel: {model}\n"
                            if 'intel' not in self.detected_gpus:
                                self.detected_gpus.append('intel')
                            self.intel_btn.setEnabled(True)

            if not self.detected_gpus:
                hardware_info += f"• {self.language_manager.get_text('no_gpu_detected')}\n"

            self.hardware_info.setText(hardware_info)
            # enable install button if any gpu detected
            self.install_btn.setEnabled(len(self.detected_gpus) > 0)

            # Log detected GPUs to console for visibility
            if self.detected_gpus:
                self.console.append_output("🔍 Detected: " + ", ".join([d.upper() for d in self.detected_gpus]))
            else:
                self.console.append_output("🔍 No compatible GPUs detected")

        except Exception as e:
            self.hardware_info.setText(f"❌ Hardware detection error: {str(e)}")
            self.console.append_output(f"❌ Hardware detection error: {str(e)}")

    def get_selected_drivers(self):
        selected_drivers = []
        driver_buttons = {
            'nvidia': self.nvidia_btn,
            'amd': self.amd_btn,
            'intel': self.intel_btn
        }

        for driver_type, button in driver_buttons.items():
            if button.isChecked() and button.isEnabled():
                selected_drivers.append(driver_type)

        return selected_drivers

    def check_sudo_access(self):
        try:
            result = subprocess.run(
                ["sudo", "-n", "true"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def request_sudo_access(self):
        if self.check_sudo_access():
            self.console.append_output("🔒 Root access already available (cached/NOPASSWD).")
            return ""

        self.console.append_output("🔐 Requesting root access (password required)...")
        tries = 0
        while tries < 3:
            tries += 1
            password, ok = QInputDialog.getText(
                self,
                self.language_manager.get_text('need_root'),
                self.language_manager.get_text('need_root_msg'),
                QtWidgets.QLineEdit.Password
            )
            if not ok:
                self.console.append_output("❌ Root access canceled by user.")
                return None

            # try to validate password with sudo -S -v
            try:
                proc = subprocess.run(
                    ["sudo", "-S", "-k", "-v"],
                    input=(password + "\n"),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if proc.returncode == 0:
                    self.console.append_output("✅ Root access granted.")
                    return password
                else:
                    stderr = proc.stderr.strip()
                    self.console.append_output(f"❌ Incorrect password or sudo failed (attempt {tries}/3).")
            except Exception as e:
                self.console.append_output(f"❌ Error checking sudo: {e}")
                return None

        self.console.append_output("❌ Root access not granted after 3 attempts.")
        return None

    def start_installation(self):
        selected_drivers = self.get_selected_drivers()

        if not selected_drivers:
            self.show_error_message(self.language_manager.get_text('no_drivers_selected'))
            return

        self.console.append_output("🟢 Selected drivers: " + ", ".join([d.upper() for d in selected_drivers]))

        sudo_password = self.request_sudo_access()
        if sudo_password is None:
            self.show_error_message("Root access denied or canceled")
            return

        driver_list = ", ".join(selected_drivers).upper()
        reply = QMessageBox.question(
            self,
            self.language_manager.get_text('confirm_install'),
            self.language_manager.get_text('install_confirm_msg').format(driver_list),
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.No:
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.install_btn.setEnabled(False)
        self.console.clear()
        self.console.append_output("🟢 Starting installation for: " + ", ".join([d.upper() for d in selected_drivers]))

        update_system = self.update_checkbox.isChecked()
        install_nomodeset = self.nomodeset_checkbox.isChecked()

        installer = DriverInstaller(self.signals, update_system, install_nomodeset, sudo_password, self.nvidia_model)
        self.install_thread = threading.Thread(target=lambda: installer.install_drivers(selected_drivers))
        self.install_thread.daemon = True
        self.install_thread.start()

    def on_output_received(self, text):
        self.console.append_output(text)

    def on_progress_updated(self, value, message):
        self.progress_bar.setValue(value)
        self.console.append_output(message)

    def on_installation_finished(self, success, message):
        self.progress_bar.setValue(100)
        self.install_btn.setEnabled(True)

        if success:
            self.console.append_output("🟢 " + message, COLORS['misc']['success'])
        else:
            self.console.append_output("❌ " + message, COLORS['misc']['error'])

    def clear_console(self):
        self.console.clear()

    def show_error_message(self, message):
        self.console.append_output("❌ " + message, COLORS['misc']['error'])

    def closeEvent(self, event):
        if self.install_thread and self.install_thread.is_alive():
            reply = QMessageBox.question(
                self,
                "Installation in progress",
                "Driver installation is still running. Are you sure you want to quit?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("EN-OS Driver Manager")
    app.setApplicationVersion("2.0")

    window = DriverManager()
    window.show()

    sys.exit(app.exec_())
