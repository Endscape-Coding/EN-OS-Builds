#!/usr/bin/env python3
import sys
import os
import subprocess
import json
import traceback
import locale
from pathlib import Path
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFrame,
                             QMessageBox, QComboBox)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, pyqtProperty, QTimer
from PyQt5.QtGui import (QIcon, QFont, QPalette, QColor, QLinearGradient,
                         QPainter, QPixmap, QFontDatabase)

os.environ['XDG_RUNTIME_DIR'] = '/tmp/runtime-root'


LOCALES = {
    'en': {
        'app_title': 'EN-OS System Manager',
        'header': 'EN-OS System Manager',
        'driver_management': 'Driver Management',
        'driver_desc': 'Install and update system drivers for optimal hardware performance',
        'software_center': 'Software Center',
        'software_desc': 'Browse and install applications from the Arch and EN-OS repository, you can also update the system',
        'remote_assistant': 'Remote Assistant Creator',
        'remote_desc': 'Create your own remote computer control solution',
        'zapret_manager': 'EN-Zapret Manager',
        'zapret_desc': 'Unblock YouTube in Russia without VPN',
        'launch_driver': '🛠️ Driver Manager',
        'launch_software': '📦 Software Center',
        'launch_remote': '🌐 Remote Assistant Creator',
        'launch_zapret': '🛡️ Zapret Manager',
        'footer': 'EN-OS 1.0 Leningrad Region · Modern Arch-based Distribution · Built with ❤️',
        'language': 'Language',
        'error_title': 'Error',
        'error_launch': 'Failed to launch {}: {}',
        'error_file_not_found': 'File not found: {}',
        'error_permission': 'Permission denied: {}',
        'error_unknown': 'Unknown error: {}',
        'settings_title': 'System Settings',
        'system_tweaks': '⚙ System Tweaks',
        'remove_autostart': '🗑 Remove Start Manager from Autostart',
        'disable_kde_restore': '❌ Disable KDE Session Restore',
        'refresh_mirrors': '🌐 Refresh Pacman Mirrors',
        'clean_journal': '🗑️ Clean System Journal Logs',
        'close': 'Close',
        'info_autostart_removed': '✔️ Autostart already disabled',
        'disable_pacman_keys_auto': '✔️ Disable automatic pacman keys initialization',
        'enable_pacman_keys_auto':  '✔️ Enable automatic pacman keys initialization',
        'ok_autostart_removed': '✔️ Start Manager removed from autostart',
        'error_remove_autostart': '❌ Failed to remove autostart file',
        'ok_kde_restore_disabled': '✔️ KDE session restore disabled.\nRestart KDE.',
        'ok_mirrors_refreshed': '✔️ Pacman mirrors refreshed.',
        'error_mirrors': '❌ Failed to refresh pacman mirrors.',
        'ok_journal_cleaned': '✔️ System journal logs cleaned.',
        'error_journal': '❌ Failed to clean journal logs.',
    },
    'ru': {
        'app_title': 'EN-OS System Manager',
        'header': 'EN-OS System Manager',
        'driver_management': 'Driver Management',
        'driver_desc': 'Установка и обновление системных драйверов для оптимальной работы оборудования',
        'software_center': 'Software Center',
        'software_desc': 'Просмотр и установка приложений из репозиториев Arch и EN-OS, также обновление системы',
        'remote_assistant': 'Remote Assistant Creator',
        'remote_desc': 'Создайте свое решение для удаленного управления компьютером',
        'zapret_manager': 'EN-Zapret Manager',
        'zapret_desc': 'Разблокировка YouTube в России без VPN',
        'launch_driver': '🛠️ Driver Manager',
        'launch_software': '📦 Software Center',
        'launch_remote': '🌐 Remote Assistant Creator',
        'launch_zapret': '🛡️ Zapret Manager',
        'footer': 'EN-OS 1.0 · Современный дистрибутив на основе Arch · Создано с ❤️',
        'language': 'Язык',
        'error_title': 'Ошибка',
        'error_launch': 'Не удалось запустить {}: {}',
        'error_file_not_found': 'Файл не найден: {}',
        'error_permission': 'Доступ запрещен: {}',
        'error_unknown': 'Неизвестная ошибка: {}',
        'settings_title': 'Настройки системы',
        'system_tweaks': '⚙ Системные твики',
        'remove_autostart': '🗑 Убрать Start Manager из автозагрузки',
        'disable_kde_restore': '❌ Отключить восстановление сессии KDE',
        'refresh_mirrors': '🌐 Обновить зеркала Pacman',
        'clean_journal': '🗑️ Очистить логи журнала системы',
        'close': 'Закрыть',
        'info_autostart_removed': 'Автозагрузка уже отключена',
        'ok_autostart_removed': 'Start Manager убран из автозагрузки',
        'error_remove_autostart': 'Не удалось удалить файл автозагрузки',
        'ok_kde_restore_disabled': 'Восстановление сессии KDE отключено.\nПерезапусти KDE.',
        'disable_pacman_keys_auto': '❌ Отключить автоматическую инициализацию ключей pacman',
        'enable_pacman_keys_auto':  '✔️ Включить авт. инициализацию ключей pacman',
        'ok_baloo_disabled': 'Индексатор файлов Baloo отключен.\nПерезапусти KDE.',
        'ok_fstrim_enabled': 'fstrim.timer включен для TRIM SSD.',
        'error_fstrim': 'Не удалось включить fstrim.timer.',
        'ok_mirrors_refreshed': 'Зеркала Pacman обновлены.',
        'error_mirrors': 'Не удалось обновить зеркала Pacman.',
        'ok_journal_cleaned': 'Логи журнала системы очищены.',
        'error_journal': 'Не удалось очистить логи журнала.',
    },
    'es': {
        'app_title': 'EN-OS System Manager',
        'header': 'EN-OS System Manager',
        'driver_management': 'Gestión de Controladores',
        'driver_desc': 'Instalar y actualizar controladores del sistema para un rendimiento óptimo del hardware',
        'software_center': 'Centro de Software',
        'software_desc': 'Explorar e instalar aplicaciones desde los repositorios de Arch y EN-OS, también actualizar el sistema',
        'remote_assistant': 'Creador de Asistente Remoto',
        'remote_desc': 'Crea tu propia solución de control remoto de computadora',
        'zapret_manager': 'EN-Zapret Manager',
        'zapret_desc': 'Desbloquear YouTube en Rusia sin VPN',
        'launch_driver': '🛠️ Gestor de Controladores',
        'launch_software': '📦 Centro de Software',
        'launch_remote': '🌐 Creador de Asistente Remoto',
        'launch_zapret': '🛡️ Gestor de Zapret',
        'footer': 'EN-OS 1.0 · Distribución moderna basada en Arch · Construido con ❤️',
        'language': 'Idioma',
        'error_title': 'Error',
        'error_launch': 'No se pudo iniciar {}: {}',
        'error_file_not_found': 'Archivo no encontrado: {}',
        'error_permission': 'Permiso denegado: {}',
        'error_unknown': 'Error desconocido: {}',
        'settings_title': 'Configuraciones del Sistema',
        'system_tweaks': '⚙ Ajustes del Sistema',
        'remove_autostart': '🗑 Eliminar Start Manager del Inicio Automático',
        'disable_kde_restore': '❌ Desactivar Restauración de Sesión KDE',
        'refresh_mirrors': '🌐 Actualizar Espejos de Pacman',
        'clean_journal': '🗑️ Limpiar Registros del Journal del Sistema',
        'close': 'Cerrar',
        'info_autostart_removed': 'Inicio automático ya desactivado',
        'ok_autostart_removed': 'Start Manager eliminado del inicio automático',
        'error_remove_autostart': 'No se pudo eliminar el archivo de inicio automático',
        'disable_pacman_keys_auto': 'Desactivar inicialización automática de claves de pacman',
        'enable_pacman_keys_auto':  '✔️ Activar inicialización automática de claves pacman',
        'ok_kde_restore_disabled': 'Restauración de sesión KDE desactivada.\nReinicia KDE.',
        'ok_baloo_disabled': 'Indexador de archivos Baloo desactivado.\nReinicia KDE.',
        'ok_fstrim_enabled': 'fstrim.timer habilitado para TRIM SSD.',
        'error_fstrim': 'No se pudo habilitar fstrim.timer.',
        'ok_mirrors_refreshed': 'Espejos de Pacman actualizados.',
        'error_mirrors': 'No se pudo actualizar espejos de Pacman.',
        'ok_journal_cleaned': 'Registros del journal del sistema limpiados.',
        'error_journal': 'No se pudo limpiar registros del journal.',
    },
    'zh_CN': {
        'app_title': 'EN-OS 系统管理器',
        'header': 'EN-OS 系统管理器',
        'driver_management': '驱动管理',
        'driver_desc': '安装和更新系统驱动程序以获得最佳硬件性能',
        'software_center': '软件中心',
        'software_desc': '浏览并从 Arch 和 EN-OS 仓库安装应用程序，也可更新系统',
        'remote_assistant': '远程助手创建器',
        'remote_desc': '创建您自己的远程电脑控制方案',
        'zapret_manager': 'EN-Zapret 管理器',
        'zapret_desc': '在俄罗斯不使用 VPN 解锁 YouTube',
        'launch_driver': '🛠️ 驱动管理器',
        'launch_software': '📦 软件中心',
        'launch_remote': '🌐 远程助手创建器',
        'launch_zapret': '🛡️ Zapret 管理器',
        'footer': 'EN-OS 1.0 · 现代 Arch 系发行版 · 用 ❤️ 打造',
        'language': '语言',
        'error_title': '错误',
        'error_launch': '无法启动 {}: {}',
        'error_file_not_found': '文件未找到: {}',
        'error_permission': '权限被拒绝: {}',
        'error_unknown': '未知错误: {}',
        'disable_pacman_keys_auto': '❌ 禁用 pacman 密钥自动初始化',
        'enable_pacman_keys_auto':  '✔️ 启用 pacman 密钥自动初始化',
        'settings_title': '系统设置',
        'system_tweaks': '⚙ 系统优化',
        'remove_autostart': '🗑 从开机启动中移除 Start Manager',
        'disable_kde_restore': '❌ 禁用 KDE 会话恢复',
        'refresh_mirrors': '🌐 刷新 Pacman 镜像',
        'clean_journal': '🗑️ 清理系统日志',
        'close': '关闭',
    },

    'ja': {
        'app_title': 'EN-OS システムマネージャー',
        'header': 'EN-OS システムマネージャー',
        'driver_management': 'ドライバ管理',
        'driver_desc': '最適なハードウェアパフォーマンスのためのシステムドライバのインストール・更新',
        'software_center': 'ソフトウェアセンター',
        'software_desc': 'Arch および EN-OS リポジトリからアプリケーションを閲覧・インストール、システム更新も可能',
        'remote_assistant': 'リモートアシスタント作成ツール',
        'remote_desc': '自分だけのリモートパソコン制御ソリューションを作成',
        'zapret_manager': 'EN-Zapret マネージャー',
        'zapret_desc': 'VPNなしでロシアのYouTubeを解除',
        'launch_driver': '🛠️ ドライバマネージャー',
        'launch_software': '📦 ソフトウェアセンター',
        'launch_remote': '🌐 リモートアシスタント作成ツール',
        'launch_zapret': '🛡️ Zapret マネージャー',
        'footer': 'EN-OS 1.0 · モダンArchベースディストリビューション · ❤️で作られました',
        'language': '言語',
        'error_title': 'エラー',
        'error_launch': '{} の起動に失敗: {}',
        'error_file_not_found': 'ファイルが見つかりません: {}',
        'error_permission': '権限が拒否されました: {}',
        'error_unknown': '不明なエラー: {}',
        'disable_pacman_keys_auto': 'pacmanキーの自動初期化を無効化',
        'enable_pacman_keys_auto':  '✔️ pacmanキーの自動初期化を有効にする',
        'settings_title': 'システム設定',
        'system_tweaks': '⚙ システム調整',
        'remove_autostart': '🗑 スタートアップから Start Manager を削除',
        'disable_kde_restore': '❌ KDE セッション復元を無効化',
        'refresh_mirrors': '🌐 Pacman ミラーを更新',
        'clean_journal': '🗑️ システムジャーナルログをクリーンアップ',
        'close': '閉じる',
    },

    'ko': {
        'app_title': 'EN-OS 시스템 관리자',
        'header': 'EN-OS 시스템 관리자',
        'driver_management': '드라이버 관리',
        'driver_desc': '최적의 하드웨어 성능을 위한 시스템 드라이버 설치 및 업데이트',
        'software_center': '소프트웨어 센터',
        'software_desc': 'Arch 및 EN-OS 저장소에서 애플리케이션 탐색 및 설치, 시스템 업데이트 가능',
        'remote_assistant': '원격 보조 도구 생성기',
        'remote_desc': '나만의 원격 컴퓨터 제어 솔루션 만들기',
        'zapret_manager': 'EN-Zapret 관리자',
        'zapret_desc': 'VPN 없이 러시아에서 YouTube 차단 해제',
        'launch_driver': '🛠️ 드라이버 관리자',
        'launch_software': '📦 소프트웨어 센터',
        'launch_remote': '🌐 원격 보조 도구 생성기',
        'launch_zapret': '🛡️ Zapret 관리자',
        'footer': 'EN-OS 1.0 · 모던 Arch 기반 배포판 · ❤️로 제작됨',
        'language': '언어',
        'error_title': '오류',
        'error_launch': '{} 실행 실패: {}',
        'error_file_not_found': '파일을 찾을 수 없음: {}',
        'error_permission': '권한 거부: {}',
        'error_unknown': '알 수 없는 오류: {}',
        'settings_title': '시스템 설정',
        'system_tweaks': '⚙ 시스템 튜닝',
        'remove_autostart': '🗑 시작 관리자 자동 실행 제거',
        'disable_pacman_keys_auto': '❌ pacman 키 자동 초기화 비활성화',
        'enable_pacman_keys_auto':  '✔️ pacman 키 자동 초기화 활성화',
        'disable_kde_restore': '❌ KDE 세션 복원 비활성화',
        'refresh_mirrors': '🌐 Pacman 미러 새로고침',
        'clean_journal': '🗑️ 시스템 저널 로그 정리',
        'close': '닫기',
    },

    'fr': {
        'app_title': 'EN-OS System Manager',
        'header': 'EN-OS System Manager',
        'driver_management': 'Gestion des Pilotes',
        'driver_desc': 'Installer et mettre à jour les pilotes système pour des performances optimales du matériel',
        'software_center': 'Centre Logiciel',
        'software_desc': 'Parcourir et installer des applications depuis les dépôts Arch et EN-OS, vous pouvez également mettre à jour le système',
        'remote_assistant': 'Créateur d\'Assistant à Distance',
        'remote_desc': 'Créez votre propre solution de contrôle à distance d\'ordinateur',
        'zapret_manager': 'EN-Zapret Manager',
        'zapret_desc': 'Débloquer YouTube en Russie sans VPN',
        'launch_driver': '🛠️ Gestionnaire de Pilotes',
        'launch_software': '📦 Centre Logiciel',
        'launch_remote': '🌐 Créateur d\'Assistant à Distance',
        'launch_zapret': '🛡️ Gestionnaire de Zapret',
        'footer': 'EN-OS 1.0 · Distribution moderne basée sur Arch · Construit avec ❤️',
        'language': 'Langue',
        'error_title': 'Erreur',
        'error_launch': 'Échec du lancement de {} : {}',
        'error_file_not_found': 'Fichier non trouvé : {}',
        'error_permission': 'Permission refusée : {}',
        'error_unknown': 'Erreur inconnue : {}',
        'settings_title': 'Paramètres du Système',
        'system_tweaks': '⚙ Ajustements du Système',
        'remove_autostart': '🗑 Supprimer Start Manager du Démarrage Automatique',
        'disable_kde_restore': '❌ Désactiver la Restauration de Session KDE',
        'refresh_mirrors': '🌐 Actualiser les Miroirs Pacman',
        'clean_journal': '🗑️ Nettoyer les Journaux du Journal Système',
        'close': 'Fermer',
        'info_autostart_removed': 'Démarrage automatique déjà désactivé',
        'disable_pacman_keys_auto': 'Désactiver l’initialisation automatique des clés pacman',
        'enable_pacman_keys_auto':  '✔️ Activer l’initialisation automatique des clés pacman',
        'ok_autostart_removed': 'Start Manager supprimé du démarrage automatique',
        'error_remove_autostart': 'Échec de la suppression du fichier de démarrage automatique',
        'ok_kde_restore_disabled': 'Restauration de session KDE désactivée.\nRedémarrez KDE.',
        'error_fstrim': 'Échec de l\'activation de fstrim.timer.',
        'ok_mirrors_refreshed': 'Miroirs Pacman actualisés.',
        'error_mirrors': 'Échec de l\'actualisation des miroirs Pacman.',
        'ok_journal_cleaned': 'Journaux du journal système nettoyés.',
        'error_journal': 'Échec du nettoyage des journaux du journal.',
    },
    'de': {
        'app_title': 'EN-OS System Manager',
        'header': 'EN-OS System Manager',
        'driver_management': 'Treiber-Management',
        'driver_desc': 'Installieren und Aktualisieren von Systemtreibern für optimale Hardwareleistung',
        'software_center': 'Software-Center',
        'software_desc': 'Durchsuchen und Installieren von Anwendungen aus den Arch- und EN-OS-Repositories, Sie können auch das System aktualisieren',
        'remote_assistant': 'Remote-Assistent-Ersteller',
        'remote_desc': 'Erstellen Sie Ihre eigene Lösung zur Fernsteuerung des Computers',
        'zapret_manager': 'EN-Zapret Manager',
        'zapret_desc': 'YouTube in Russland ohne VPN entsperren',
        'launch_driver': '🛠️ Treiber-Manager',
        'launch_software': '📦 Software-Center',
        'launch_remote': '🌐 Remote-Assistent-Ersteller',
        'launch_zapret': '🛡️ Zapret-Manager',
        'footer': 'EN-OS 1.0· Moderne Arch-basierte Distribution · Gebaut mit ❤️',
        'language': 'Sprache',
        'error_title': 'Fehler',
        'error_launch': 'Fehler beim Starten von {}: {}',
        'error_file_not_found': 'Datei nicht gefunden: {}',
        'error_permission': 'Zugriff verweigert: {}',
        'error_unknown': 'Unbekannter Fehler: {}',
        'disable_pacman_keys_auto': '❌ Automatische Initialisierung der pacman-Schlüssel deaktivieren',
        'settings_title': 'Systemeinstellungen',
        'enable_pacman_keys_auto':  '✔️ Automatische Initialisierung der pacman-Schlüssel aktivieren',
        'system_tweaks': '⚙ Systemanpassungen',
        'remove_autostart': '🗑 Start Manager aus Autostart entfernen',
        'disable_kde_restore': '❌ KDE-Sitzungswiederherstellung deaktivieren',
        'refresh_mirrors': '🌐 Pacman-Spiegel aktualisieren',
        'clean_journal': '🗑️ System-Journal-Protokolle bereinigen',
        'close': 'Schließen',
        'info_autostart_removed': 'Autostart bereits deaktiviert',
        'ok_autostart_removed': 'Start Manager aus Autostart entfernt',
        'error_remove_autostart': 'Fehler beim Entfernen der Autostart-Datei',
        'ok_kde_restore_disabled': 'KDE-Sitzungswiederherstellung deaktiviert.\nStarten Sie KDE neu.',
        'ok_baloo_disabled': 'Baloo-Dateiindexierer deaktiviert.\nStarten Sie KDE neu.',
        'ok_fstrim_enabled': 'fstrim.timer für SSD-TRIM aktiviert.',
        'error_fstrim': 'Fehler beim Aktivieren von fstrim.timer.',
        'ok_mirrors_refreshed': 'Pacman-Spiegel aktualisiert.',
        'error_mirrors': 'Fehler beim Aktualisieren der Pacman-Spiegel.',
        'ok_journal_cleaned': 'System-Journal-Protokolle bereinigt.',
        'error_journal': 'Fehler beim Bereinigen der Journal-Protokolle.',
    },
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
        'dark_blue': '#4361ee'
    },
    'text': {
        'primary': '#ffffff',
        'secondary': '#b8b8d1',
        'muted': '#8b8ba7'
    },
    'misc': {
        'border': '#2d2d4d',
        'success': '#4cd964',
        'error': '#ff4757'
    }
}

class LanguageManager:
    def __init__(self):
        self.current_language = self.detect_system_language()
        self.load_language_setting()

    def detect_system_language(self):
        lang_map = {
            'en': 'en',
            'ru': 'ru',
            'uk': 'ru',
            'es': 'es',
            'fr': 'fr',
            'de': 'de',
        }
        default = 'en'

        try:
            lang_env = os.environ.get('LANG', '') or os.environ.get('LANGUAGE', '')
            if lang_env:
                lang_code = lang_env.split('_')[0].lower()
                return lang_map.get(lang_code, default)

            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                lang_code = system_locale.split('_')[0].lower()
                return lang_map.get(lang_code, default)

            result = subprocess.run(['locale'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('LANG=') or line.startswith('LANGUAGE='):
                        lang_code = line.split('=')[1].split('_')[0].lower().replace('"', '')
                        return lang_map.get(lang_code, default)
        except Exception as e:
            print(f"Language detection error: {e}")

        return default

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

class MinimalButton(QPushButton):
    def __init__(self, text, icon=None, color_scheme='blue', parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(70)
        self.setFont(QFont("GNF", 44))

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
            'green': {'bg': '#2a2a4a', 'hover': '#3a3a5a', 'text': '#4cd964'}
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
                font-size: 20px;
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

class ModernCard(QFrame):
    def __init__(self, title, description, icon=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            ModernCard {{
                background-color: {COLORS['primary']['medium']};
                border: 1px solid {COLORS['misc']['border']};
                border-radius: 12px;
                padding: 0px;
            }}
        """)
        self.setMinimumHeight(100)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(12)

        if icon:
            icon_label = QLabel()
            icon_label.setPixmap(icon.pixmap(32, 32))
            icon_label.setStyleSheet("padding: 3px;")
            layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text']['primary']};
                font-size: 14px;
                font-weight: bold;
            }}
        """)

        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text']['secondary']};
                font-size: 12px;
            }}
        """)
        desc_label.setWordWrap(True)
        desc_label.setFixedHeight(70)
        desc_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)
        layout.addLayout(text_layout)

class ENOSStarter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.language_manager = LanguageManager()

        self.setWindowTitle(self.language_manager.get_text('app_title'))
        self.setFixedSize(900, 700)

        try:
            self.setWindowIcon(QtGui.QIcon('/usr/share/icons/en-os/start/logo.png'))
        except:
            pass

        self.load_fonts()
        self.set_modern_theme()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 15)
        main_layout.setSpacing(15)

        self.create_header(main_layout)
        self.create_cards_section(main_layout)
        self.create_buttons_section(main_layout)

        main_layout.addStretch()

        settings_layout = QHBoxLayout()
        settings_layout.addStretch()

        self.settings_btn = QPushButton("⚙ Mini-Tweaker")
        self.settings_btn.setFixedSize(260, 42)
        self.settings_btn.clicked.connect(self.open_settings)

        self.settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']['medium']};
                color: {COLORS['accent']['blue']};
                border: 1px solid {COLORS['misc']['border']};
                border-radius: 10px;
                font-size: 13px;
                font-weight: bold;
                padding: 6px 14px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['accent']['blue']};
                background-color: {COLORS['primary']['light']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['primary']['dark']};
            }}
        """)

        settings_layout.addWidget(self.settings_btn)
        settings_layout.addStretch()

        main_layout.addLayout(settings_layout)


        self.create_footer(main_layout)

        self._window_opacity = 1.0

    def open_settings(self):
        dlg = SettingsWindow(self.language_manager, self)
        dlg.exec_()

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

    def create_cards_section(self, parent_layout):
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        self.card1 = ModernCard(
            self.language_manager.get_text('driver_management'),
            self.language_manager.get_text('driver_desc')
        )
        self.card2 = ModernCard(
            self.language_manager.get_text('software_center'),
            self.language_manager.get_text('software_desc')
        )
        self.card3 = ModernCard(
            self.language_manager.get_text('remote_assistant'),
            self.language_manager.get_text('remote_desc')
        )
        self.card4 = ModernCard(
            self.language_manager.get_text('zapret_manager'),
            self.language_manager.get_text('zapret_desc')
        )

        cards_layout.addWidget(self.card1)
        cards_layout.addWidget(self.card2)
        cards_layout.addWidget(self.card3)
        cards_layout.addWidget(self.card4)

        parent_layout.addLayout(cards_layout)

    def create_buttons_section(self, parent_layout):
        buttons_container = QFrame()
        buttons_container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['primary']['dark']};
                border: 1px solid {COLORS['misc']['border']};
                border-radius: 12px;
                padding: 0px;
            }}
        """)

        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setSpacing(10)
        buttons_layout.setContentsMargins(15, 15, 15, 15)

        self.driver_btn = MinimalButton(
            self.language_manager.get_text('launch_driver'),
            color_scheme='blue'
        )
        self.driver_btn.clicked.connect(self.launch_driver_manager)
        buttons_layout.addWidget(self.driver_btn)

        self.packages_btn = MinimalButton(
            self.language_manager.get_text('launch_software'),
            color_scheme='purple'
        )
        self.packages_btn.clicked.connect(self.launch_package_installer)
        buttons_layout.addWidget(self.packages_btn)

        self.updater_btn = MinimalButton(
            self.language_manager.get_text('launch_remote'),
            color_scheme='cyan'
        )
        self.updater_btn.clicked.connect(self.launch_assist_creator)
        buttons_layout.addWidget(self.updater_btn)

        self.zapret_btn = MinimalButton(
            self.language_manager.get_text('launch_zapret'),
            color_scheme='green'
        )
        self.zapret_btn.clicked.connect(self.zapret_manager)
        buttons_layout.addWidget(self.zapret_btn)

        parent_layout.addWidget(buttons_container)

    def create_footer(self, parent_layout):
        self.footer_label = QLabel(self.language_manager.get_text('footer'))
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text']['muted']};
                font-size: 10px;
                font-weight: medium;
                padding: 8px;
                background-color: {COLORS['primary']['dark']};
                border: 1px solid {COLORS['misc']['border']};
                border-radius: 8px;
            }}
        """)
        parent_layout.addWidget(self.footer_label)

    def on_language_changed(self):
        language_code = self.language_combo.currentData()
        if self.language_manager.set_language(language_code):
            self.restart_application()

    def restart_application(self):
        import sys
        import os

        self.close()

        os.execl(
            sys.executable,
            sys.executable,
            *sys.argv
        )

    def retranslate_ui(self):
        self.setWindowTitle(self.language_manager.get_text('app_title'))

        self.header_label.setText(self.language_manager.get_text('header'))

        self.update_card_descriptions()

        self.driver_btn.setText(self.language_manager.get_text('launch_driver'))
        self.packages_btn.setText(self.language_manager.get_text('launch_software'))
        self.updater_btn.setText(self.language_manager.get_text('launch_remote'))
        self.zapret_btn.setText(self.language_manager.get_text('launch_zapret'))

        self.footer_label.setText(self.language_manager.get_text('footer'))

    def update_card_descriptions(self):
        for card, desc_key in [
            (self.card1, 'driver_desc'),
            (self.card2, 'software_desc'),
            (self.card3, 'remote_desc'),
            (self.card4, 'zapret_desc')
        ]:
            text_layout = card.layout().itemAt(1).layout()
            if text_layout and text_layout.count() >= 2:
                desc_label = text_layout.itemAt(1).widget()
                if isinstance(desc_label, QLabel):
                    desc_label.setText(self.language_manager.get_text(desc_key))

    def load_fonts(self):
        try:
            font_id = QFontDatabase.addApplicationFont("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
            if font_id != -1:
                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                app_font = QFont(font_family, 9)
                QApplication.setFont(app_font)
        except Exception as e:
            print(f"Font loading error: {e}")

    def set_modern_theme(self):
        """Устанавливает современную тему"""
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
            QScrollBar:vertical {{
                border: none;
                background: {COLORS['primary']['medium']};
                width: 8px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['accent']['blue']};
                min-height: 20px;
                border-radius: 4px;
            }}
        """)

    def showEvent(self, event):
        self.setWindowOpacity(0.0)
        self.fade_animation = QPropertyAnimation(self, b"window_opacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.start()
        super().showEvent(event)

    def safe_launch(self, command, app_name):
        try:
            if isinstance(command, list):
                executable = command[0]
            else:
                executable = command

            if not os.path.exists(executable):
                error_msg = self.language_manager.get_text('error_file_not_found').format(executable)
                self.show_error_message(app_name, error_msg)
                return False

            if not os.access(executable, os.X_OK):
                error_msg = self.language_manager.get_text('error_permission').format(executable)
                self.show_error_message(app_name, error_msg)
                return False

            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if process.poll() is not None:
                error_msg = self.language_manager.get_text('error_launch').format(app_name, "Process terminated immediately")
                self.show_error_message(app_name, error_msg)
                return False
            return True

        except FileNotFoundError:
            error_msg = self.language_manager.get_text('error_file_not_found').format(executable)
            self.show_error_message(app_name, error_msg)
        except PermissionError:
            error_msg = self.language_manager.get_text('error_permission').format(executable)
            self.show_error_message(app_name, error_msg)
        except Exception as e:
            error_msg = self.language_manager.get_text('error_unknown').format(str(e))
            self.show_error_message(app_name, error_msg)
            print(f"Detailed error for {app_name}:")
            traceback.print_exc()

        return False

    def launch_driver_manager(self):
        app_name = self.language_manager.get_text('driver_management')
        self.safe_launch(["/usr/bin/enos-driver-manager"], app_name)

    def launch_assist_creator(self):
        app_name = self.language_manager.get_text('remote_assistant')
        self.safe_launch(["/usr/bin/enos-assistant-creator"], app_name)

    def launch_package_installer(self):
        app_name = self.language_manager.get_text('software_center')
        self.safe_launch(["/usr/bin/pamac-manager"], app_name)

    def zapret_manager(self):
        app_name = self.language_manager.get_text('zapret_manager')
        self.safe_launch(["/usr/bin/enos-zapret-manager"], app_name)

    def show_error_message(self, app_name, message):
        QMessageBox.critical(
            self,
            self.language_manager.get_text('error_title'),
            f"{app_name}: {message}",
            QMessageBox.Ok
        )

    def get_window_opacity(self):
        return self._window_opacity

    def set_window_opacity(self, opacity):
        self._window_opacity = opacity
        self.setWindowOpacity(opacity)

    window_opacity = pyqtProperty(float, get_window_opacity, set_window_opacity)

class SettingsWindow(QtWidgets.QDialog):
    def __init__(self, language_manager, parent=None):
        super().__init__(parent)
        self.language_manager = language_manager

        self.setWindowTitle(self.language_manager.get_text('settings_title'))
        self.setFixedSize(550, 500)  # Increased size for more buttons
        self.setModal(True)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['primary']['dark']};
            }}
            QPushButton {{
                background-color: {COLORS['primary']['medium']};
                color: {COLORS['text']['primary']};
                border: 1px solid {COLORS['misc']['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['accent']['blue']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel(self.language_manager.get_text('system_tweaks'))
        title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['accent']['blue']};
                font-size: 18px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(title)

        self.remove_autostart_btn = QPushButton(self.language_manager.get_text('remove_autostart'))
        self.remove_autostart_btn.clicked.connect(self.remove_enos_autostart)
        layout.addWidget(self.remove_autostart_btn)

        self.disable_kde_restore_btn = QPushButton(self.language_manager.get_text('disable_kde_restore'))
        self.disable_kde_restore_btn.clicked.connect(self.disable_kde_session_restore)
        layout.addWidget(self.disable_kde_restore_btn)

        self.refresh_mirrors_btn = QPushButton(self.language_manager.get_text('refresh_mirrors'))
        self.refresh_mirrors_btn.clicked.connect(self.refresh_pacman_mirrors)
        layout.addWidget(self.refresh_mirrors_btn)

        self.clean_journal_btn = QPushButton(self.language_manager.get_text('clean_journal'))
        self.clean_journal_btn.clicked.connect(self.clean_journal_logs)
        layout.addWidget(self.clean_journal_btn)

        self.enable_keys_auto_btn = QPushButton(self.language_manager.get_text('enable_pacman_keys_auto'))
        self.enable_keys_auto_btn.clicked.connect(self.enable_pacman_keys_init_service)
        layout.addWidget(self.enable_keys_auto_btn)

        self.disable_keys_auto_btn = QPushButton(self.language_manager.get_text('disable_pacman_keys_auto'))
        self.disable_keys_auto_btn.clicked.connect(self.disable_pacman_keys_init_service)
        layout.addWidget(self.disable_keys_auto_btn)

        layout.addStretch()

        close_btn = QPushButton(self.language_manager.get_text('close'))
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

    def remove_enos_autostart(self):
        home_dir = os.path.expanduser("~")
        path = os.path.join(home_dir, ".config", "autostart", "en-system-manager.desktop")

        if not os.path.exists(path):
            QMessageBox.information(self, "Info", self.language_manager.get_text('info_autostart_removed'))
            return

        try:
            os.remove(path)
            QMessageBox.information(self, "OK", self.language_manager.get_text('ok_autostart_removed'))
        except Exception as e:
            QMessageBox.critical(self, "Error",
                                f"{self.language_manager.get_text('error_remove_autostart')}\n{str(e)}")

    def disable_pacman_keys_init_service(self):
        result = subprocess.run(
            ["pkexec", "systemctl", "disable", "--now", "pacman-keys-init.service"],
            capture_output=True, text=True
        )

        if result.returncode == 0:
            QMessageBox.information(self, "OK",
                "Автоматическая инициализация ключей pacman отключена")
        else:
            QMessageBox.critical(self, "Ошибка",
                f"Не удалось отключить службу:\n{result.stderr}")

    def enable_pacman_keys_init_service(self):
        result = subprocess.run(
            ["pkexec", "systemctl", "enable", "--now", "pacman-keys-init.service"],
            capture_output=True, text=True
        )

        if result.returncode == 0:
            QMessageBox.information(self, "OK",
                "Автоматическая инициализация ключей pacman отключена")
        else:
            QMessageBox.critical(self, "Ошибка",
                f"Не удалось отключить службу:\n{result.stderr}")

    def disable_kde_session_restore(self):
        config_path = Path.home() / ".config" / "ksmserverrc"

        data = config_path.read_text().splitlines() if config_path.exists() else []

        new_data = []
        in_general = False
        written = False

        for line in data:
            if line.strip() == "[General]":
                in_general = True
                new_data.append(line)
                continue

            if in_general and line.startswith("loginMode="):
                new_data.append("loginMode=emptySession")
                written = True
                in_general = False
                continue

            new_data.append(line)

        if not written:
            new_data += ["", "[General]", "loginMode=emptySession"]

        config_path.write_text("\n".join(new_data))

        QMessageBox.information(
            self,
            "OK",
            self.language_manager.get_text('ok_kde_restore_disabled')
        )

    def refresh_pacman_mirrors(self):
        result = subprocess.run(
            ["pkexec", "reflector", "--latest", "20", "--protocol", "https", "--sort", "rate", "--save", "/etc/pacman.d/mirrorlist"],
            capture_output=True
        )

        if result.returncode == 0:
            QMessageBox.information(self, "OK", self.language_manager.get_text('ok_mirrors_refreshed'))
        else:
            QMessageBox.critical(self, "Error", self.language_manager.get_text('error_mirrors'))

    def clean_journal_logs(self):
        result = subprocess.run(
            ["pkexec", "journalctl", "--vacuum-time=2weeks"],
            capture_output=True
        )

        if result.returncode == 0:
            QMessageBox.information(self, "OK", self.language_manager.get_text('ok_journal_cleaned'))
        else:
            QMessageBox.critical(self, "Error", self.language_manager.get_text('error_journal'))



if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("EN-OS System Manager")
        app.setApplicationVersion("1.0")

        try:
            app.setWindowIcon(QIcon.fromTheme("system-run"))
        except:
            pass

        window = ENOSStarter()
        window.show()

        sys.exit(app.exec_())

    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)
