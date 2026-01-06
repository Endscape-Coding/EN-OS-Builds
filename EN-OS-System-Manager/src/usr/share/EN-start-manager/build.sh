#!/bin/bash

show_help() {
    echo "Usage: encreator --token=\"BOT_TOKEN\" --id=ADMIN_CHAT_ID"
    echo "Options:"
    echo "  --token=BOT_TOKEN      Telegram Bot Token from BotFather"
    echo "  --id=ADMIN_CHAT_ID     Your Telegram Chat ID"
    echo "  --help                 Show this help message"
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

if ! command -v go &> /dev/null; then
    echo "Installing Go..."

    wget https://golang.org/dl/go1.21.4.linux-amd64.tar.gz -O /tmp/go.tar.gz
    sudo rm -rf /usr/local/go
    sudo tar -C /usr/local -xzf /tmp/go.tar.gz
    rm /tmp/go.tar.gz

    echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
    source ~/.bashrc

    echo "Go successfully installed"
else
    echo "Go is already installed"
fi

echo "Installing dependencies..."
go mod download
echo "Dependencies installed"

EXECUTABLE_PATH="$(pwd)/enclient"

echo "Checking for existing installation..."

if pgrep -f "$EXECUTABLE_PATH" > /dev/null; then
    echo "Stopping running enclient..."
    pkill -f "$EXECUTABLE_PATH"
    sleep 1
fi

if [ -f "$EXECUTABLE_PATH" ]; then
    echo "Removing old binary..."
    rm -f "$EXECUTABLE_PATH"
fi

USER_AUTOSTART_FILE="$HOME/.config/autostart/enclient.desktop"
if [ -f "$USER_AUTOSTART_FILE" ]; then
    echo "Removing user autostart..."
    rm -f "$USER_AUTOSTART_FILE"
fi

SYSTEM_AUTOSTART_FILE="/etc/xdg/autostart/enclient.desktop"
if [ -f "$SYSTEM_AUTOSTART_FILE" ]; then
    echo "Removing system autostart..."
    sudo rm -f "$SYSTEM_AUTOSTART_FILE"
fi

echo "Old installation removed"

echo "Updating configuration..."
sed -i "s/BOT_TOKEN *= *\".*\"/BOT_TOKEN = \"$BOT_TOKEN\"/" main.go
sed -i "s/ADMIN_CHAT_ID *= *[0-9]*/ADMIN_CHAT_ID = $ADMIN_CHAT_ID/" main.go
echo "Configuration updated"

echo "Compiling binary..."
go build -o enclient -ldflags="-s -w" main.go

if [ $? -eq 0 ]; then
    echo "Compilation successful! Executable file: enclient"
else
    echo "Compilation error!"
    exit 1
fi

echo "Creating user autostart shortcut for KDE..."
USER_AUTOSTART_DIR="$HOME/.config/autostart"
USER_AUTOSTART_FILE="$USER_AUTOSTART_DIR/enclient.desktop"

mkdir -p "$USER_AUTOSTART_DIR"

EXECUTABLE_PATH="$(pwd)/enclient"

cat > "$USER_AUTOSTART_FILE" << EOF
[Desktop Entry]
Type=Application
Name=Enclient
Exec=$EXECUTABLE_PATH
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
X-KDE-autostart-after=panel
Comment=Enclient Telegram Bot
EOF

echo "User autostart shortcut created: $USER_AUTOSTART_FILE"

echo "Creating system-wide autostart shortcut..."
SYSTEM_AUTOSTART_DIR="/etc/xdg/autostart"
SYSTEM_AUTOSTART_FILE="$SYSTEM_AUTOSTART_DIR/enclient.desktop"

sudo bash -c "cat > \"$SYSTEM_AUTOSTART_FILE\" << EOF
[Desktop Entry]
Type=Application
Name=Enclient
Exec=$EXECUTABLE_PATH
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
X-KDE-autostart-after=panel
Comment=Enclient Telegram Bot
OnlyShowIn=KDE;XFCE;GNOME;
EOF"

echo "System-wide autostart shortcut created: $SYSTEM_AUTOSTART_FILE"

sudo chmod 644 "$SYSTEM_AUTOSTART_FILE"

echo "Starting the application..."
chmod +x "$EXECUTABLE_PATH"
"$EXECUTABLE_PATH" &

echo "Application started and configured for autostart!"
echo "The application will automatically start:"
echo "1. For current user: via ~/.config/autostart/"
echo "2. System-wide: via /etc/xdg/autostart/ (for all users)"
echo "3. Specifically optimized for KDE with X-KDE-autostart-after=panel"
