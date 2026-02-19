#!/bin/bash

for arg in "$@"; do
    case $arg in
        --token=*)
            BOT_TOKEN="${arg#*=}"
            ;;
        --id=*)
            ADMIN_CHAT_ID="${arg#*=}"
            ;;
    esac
done

[ -z "$BOT_TOKEN" ] || [ -z "$ADMIN_CHAT_ID" ] && exit 1

BUILD_DIR="$HOME/.enclient"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

cp -r main.go go.mod go.sum assets "$BUILD_DIR/" 2>/dev/null

cd "$BUILD_DIR" || exit 1

command -v go >/dev/null || {
    wget https://go.dev/dl/go1.23.1.linux-amd64.tar.gz -O /tmp/go.tar.gz
    sudo rm -rf /usr/local/go
    sudo tar -C /usr/local -xzf /tmp/go.tar.gz
    rm /tmp/go.tar.gz
    echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
    source ~/.bashrc
}

go mod download

EXECUTABLE_NAME="enclient"
EXECUTABLE_PATH="$BUILD_DIR/$EXECUTABLE_NAME"

pkill -f "$EXECUTABLE_PATH" 2>/dev/null
sleep 1
rm -f "$EXECUTABLE_PATH"

sed -i "s/BOT_TOKEN *= *\".*\"/BOT_TOKEN = \"$BOT_TOKEN\"/" main.go
sed -i "s/ADMIN_CHAT_ID *= *[0-9]*/ADMIN_CHAT_ID = $ADMIN_CHAT_ID/" main.go

go build -o "$EXECUTABLE_NAME" -ldflags="-s -w" main.go || exit 1

chmod +x "$EXECUTABLE_PATH"

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

# Запуск в полном фоне — без вывода в терминал и без привязки к сессии
nohup "$EXECUTABLE_PATH" >/dev/null 2>&1 &

# Даём секунду на запуск
sleep 1

echo "Готово!"
echo "Приложение собрано, запущено в фоне и настроено на автозапуск"
echo " • Папка:          $BUILD_DIR"
echo " • Исполняемый:    $EXECUTABLE_PATH"
echo " • Автозапуск:     ~/.config/autostart/enclient.desktop"
echo " • Процесс отсоединён — скрипт завершил работу"

exit 0
