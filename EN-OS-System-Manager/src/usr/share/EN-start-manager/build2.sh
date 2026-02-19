#!/bin/bash

show_help() {
    echo "Usage: $0 --token=\"BOT_TOKEN\" --id=ADMIN_CHAT_ID"
    echo "Options:"
    echo "  --token=BOT_TOKEN     Telegram Bot Token from BotFather"
    echo "  --id=ADMIN_CHAT_ID    Your Telegram Chat ID"
    echo "  --help                Show this help message"
    exit 0
}

for arg in "$@"; do
    case $arg in
        --token=*)
            BOT_TOKEN="${arg#*=}"
            ;;
        --id=*)
            ADMIN_CHAT_ID="${arg#*=}"
            ;;
        --help)
            show_help
            ;;
    esac
done

if [ -z "$BOT_TOKEN" ] || [ -z "$ADMIN_CHAT_ID" ]; then
    echo "Error: Missing required parameters"
    show_help
    exit 1
fi

BUILD_DIR="$HOME/.enclient"

echo "Целевая папка сборки: $BUILD_DIR"

if [ -d "$BUILD_DIR" ]; then
    echo "Очищаем старую папку сборки..."
    rm -rf "$BUILD_DIR"/*
else
    echo "Создаём скрытую папку..."
    mkdir -p "$BUILD_DIR"
fi

echo "Переносим исходные файлы в $BUILD_DIR..."
cp -v main.go   "$BUILD_DIR/" 2>/dev/null || echo "main.go не найден, пропускаем"
cp -v go.mod    "$BUILD_DIR/" 2>/dev/null || true
cp -v go.sum    "$BUILD_DIR/" 2>/dev/null || true

if [ -d "assets" ]; then
    echo "Копируем папку assets..."
    cp -r assets "$BUILD_DIR/"
fi

cd "$BUILD_DIR" || { echo "Не удалось перейти в $BUILD_DIR"; exit 1; }

echo "Работаем в директории: $(pwd)"

if ! command -v go &> /dev/null; then
    echo "Установка Go..."
    wget https://go.dev/dl/go1.23.1.linux-amd64.tar.gz -O /tmp/go.tar.gz || exit 1
    sudo rm -rf /usr/local/go
    sudo tar -C /usr/local -xzf /tmp/go.tar.gz
    rm /tmp/go.tar.gz
    echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
    source ~/.bashrc
else
    echo "Go уже установлен ($(go version))"
fi

echo "Установка зависимостей..."
go mod download || { echo "Ошибка загрузки зависимостей"; exit 1; }

EXECUTABLE_NAME="enclient"
EXECUTABLE_PATH="$BUILD_DIR/$EXECUTABLE_NAME"

if pgrep -f "$EXECUTABLE_PATH" > /dev/null; then
    echo "Останавливаю предыдущий экземпляр..."
    pkill -f "$EXECUTABLE_PATH"
    sleep 1
fi

[ -f "$EXECUTABLE_PATH" ] && rm -f "$EXECUTABLE_PATH"

echo "Обновляю токен и ID в main.go..."
sed -i "s/BOT_TOKEN *= *\".*\"/BOT_TOKEN = \"$BOT_TOKEN\"/" main.go
sed -i "s/ADMIN_CHAT_ID *= *[0-9]*/ADMIN_CHAT_ID = $ADMIN_CHAT_ID/" main.go

echo "Компиляция..."
go build -o "$EXECUTABLE_NAME" -ldflags="-s -w" main.go

if [ $? -eq 0 ]; then
    echo "Компиляция успешна!"
    echo "Исполняемый файл: $EXECUTABLE_PATH"
    chmod +x "$EXECUTABLE_PATH"
else
    echo "Ошибка компиляции!"
    exit 1
fi

USER_AUTOSTART_FILE="$HOME/.config/autostart/enclient.desktop"
mkdir -p "$(dirname "$USER_AUTOSTART_FILE")"

cat > "$USER_AUTOSTART_FILE" << EOF
[Desktop Entry]
Type=Application
Name=Enclient
Exec=$EXECUTABLE_PATH
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Comment=Enclient Telegram Bot
EOF

echo "Автозапуск создан: $USER_AUTOSTART_FILE"

echo "Запускаю приложение..."
"$EXECUTABLE_PATH" &

echo "Готово!"
echo "Приложение собрано и запущено"
echo "  • Папка:          $BUILD_DIR"
echo "  • Исполняемый:    $EXECUTABLE_PATH"
echo "  • Автозапуск:     ~/.config/autostart/enclient.desktop"
