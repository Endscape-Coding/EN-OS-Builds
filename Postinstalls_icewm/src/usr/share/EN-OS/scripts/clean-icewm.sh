#!/bin/bash
set -euo pipefail

log() { echo -e "[*] $*"; }
ok() { echo -e " ✓ $*"; }
warn(){ echo -e " ⚠ $*"; }
fail(){ echo -e " ✗ $*"; exit 1; }

check_root() {
    if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
        fail "Этот скрипт должен выполняться с правами root."
    fi
}

remove_sddm_autologin() {
    log "Удаление автоматического входа SDDM..."
    local sddm_conf="/etc/sddm.conf"
    local sddm_conf_d="/etc/sddm.conf.d"

    if [ -f "$sddm_conf" ]; then
        sed -i '/^User=/d;/^Session=/d;/^Autologin=/d' "$sddm_conf" 2>/dev/null || true
        ok "Основной конфиг SDDM очищен"
    fi

    if [ -d "$sddm_conf_d" ]; then
        find "$sddm_conf_d" -type f -name "*.conf" -exec sed -i '/Autologin/d;/User=/d' {} \; 2>/dev/null || true
        rm -f "$sddm_conf_d/autologin.conf" 2>/dev/null || true
        ok "Конфиги в sddm.conf.d очищены"
    fi

    if [ -f /usr/share/EN-OS/sddm/kde_settings.conf ]; then
        mkdir -p "$sddm_conf_d"
        cp -f /usr/share/EN-OS/sddm/kde_settings.conf "$sddm_conf_d/" 2>/dev/null || true
        ok "Восстановлены стандартные настройки SDDM"
    fi
}

remove_calamares_autostart() {
    log "Удаление Calamares из автозапуска..."

    rm -rf /etc/calamares 2>/dev/null || true
    find /etc/xdg/autostart /etc/skel/.config/autostart /root/.config/autostart /home/*/.config/autostart \
        -name "calamares.desktop" -delete 2>/dev/null || true

    rm -f /etc/systemd/system/calamares.service \
          /etc/systemd/system/multi-user.target.wants/calamares.service 2>/dev/null || true

    systemctl daemon-reload 2>/dev/null || true
    ok "Calamares успешно удалён из автозапуска"
}

remove_installer_packages() {
    log "Удаление пакетов установщика..."
    pacman -Rdd --noconfirm calamares arch-install-scripts 2>/dev/null || true
    ok "Пакеты установщика удалены"
}

clean_temporary_files() {
    log "Очистка временных файлов..."

    if command -v paccache >/dev/null 2>&1; then
        paccache -rk1 2>/dev/null || true
    fi

    rm -rf /var/log/calamares /tmp/calamares-* /var/tmp/calamares-* 2>/dev/null || true
    find /root /home/* -maxdepth 1 -name "calamares.log" -delete 2>/dev/null || true

    journalctl --vacuum-time=1d 2>/dev/null || true
    rm -rf /var/lib/systemd/coredump/* 2>/dev/null || true

    ok "Временные файлы очищены"
}

clean_history_and_cache() {
    log "Очистка истории и кэша..."

    find /root /home/* -maxdepth 1 -name ".bash_history" -delete 2>/dev/null || true
    find /root /home/* -maxdepth 1 -name ".cache" -type d -exec rm -rf {} \; 2>/dev/null || true
    find /home -type f -name "*.log" -size +10M -delete 2>/dev/null || true

    if [ -d /var/cache/pacman/pkg ]; then
        find /var/cache/pacman/pkg -name "*.part" -delete 2>/dev/null || true
    fi

    ok "История и кэш очищены"
}

disable_live_services() {
    log "Отключение live-служб..."

    local services=("live-setup.service" "installer-service.service" "autostart-calamares.service")
    for s in "${services[@]}"; do
        systemctl disable "$s" 2>/dev/null || true
        systemctl stop "$s" 2>/dev/null || true
    done

    systemctl daemon-reload 2>/dev/null || true
    ok "Live-службы отключены"
}

systemctl_starting() {
    log "Включение основных служб..."

    local services=("NetworkManager" "bluetooth" "lightdm" "postinstall.service")
    for s in "${services[@]}"; do
        systemctl enable "$s" 2>/dev/null || true
        if [ "$s" != "lightdm" ] && [ "$s" != "postinstall.service" ]; then
            systemctl start "$s" 2>/dev/null || true
        fi
    done

    chmod +x /usr/share/EN-OS/scripts/postinstall.sh 2>/dev/null || true

    if [ -f /usr/share/EN-OS/scripts/keys.sh ]; then
        bash /usr/share/EN-OS/scripts/keys.sh 2>/dev/null || true
    fi

    systemctl daemon-reload 2>/dev/null || true
    ok "Основные службы активированы"
}

plymouth_fix() {
    log "Настройка Plymouth..."

    if command -v plymouth-set-default-theme >/dev/null 2>&1; then
        if plymouth-set-default-theme -R en-os 2>/dev/null; then
            ok "Тема Plymouth установлена"
        else
            warn "Не удалось установить тему Plymouth"
        fi
    else
        warn "Plymouth не установлен, пропускаем"
    fi
}

zram_setup() {
    log "Настройка ZRAM..."

    local script_path="/usr/local/bin/zram-setup.sh"
    local service_path="/etc/systemd/system/zram.service"

    if ! modprobe -n zram 2>/dev/null; then
        warn "Модуль ZRAM недоступен, пропускаем настройку"
        return 0
    fi

    cat > "$script_path" <<'EOF'
#!/bin/bash
set -euo pipefail

log() { echo "[ZRAM] $*"; }
ok() { echo "[OK] $*"; }
warn() { echo "[WARN] $*" >&2; }

trap 'warn "Ошибка в скрипте ZRAM"; exit 1' ERR

if ! modprobe zram 2>/dev/null; then
    warn "Не удалось загрузить модуль zram"
    exit 0
fi

swapoff /dev/zram0 2>/dev/null || true
if [ -e /sys/block/zram0/reset ]; then
    echo 1 > /sys/block/zram0/reset 2>/dev/null || true
fi

mem_kb=$(awk '/MemTotal/ {print $2}' /proc/meminfo 2>/dev/null || echo "0")
[ "$mem_kb" -eq 0 ] && exit 0

mem_gb=$((mem_kb / 1024 / 1024))
mem_total_gb=$((mem_kb / 1024 / 1024))

if [ "$mem_total_gb" -le 2 ]; then
    zram_percent=25
    algorithm=lzo-rle
    streams=1
elif [ "$mem_total_gb" -le 4 ]; then
    zram_percent=33
    algorithm=lz4
    streams=1
elif [ "$mem_total_gb" -le 8 ]; then
    zram_percent=50
    algorithm=lz4
    streams=$(nproc 2>/dev/null || echo 1)
    streams=$((streams > 2 ? 2 : streams))
else
    zram_percent=25
    algorithm=zstd
    streams=$(nproc 2>/dev/null || echo 1)
    streams=$((streams > 4 ? 4 : streams))
fi

zram_size_mb=$((mem_kb * zram_percent / 100 / 1024))
[ "$zram_size_mb" -lt 256 ] && zram_size_mb=256
zram_size_bytes=$((zram_size_mb * 1024 * 1024))

echo "$algorithm" > /sys/block/zram0/comp_algorithm 2>/dev/null || true
echo "$streams" > /sys/block/zram0/max_comp_streams 2>/dev/null || true

if echo "$zram_size_bytes" > /sys/block/zram0/disksize 2>/dev/null; then
    if mkswap /dev/zram0 >/dev/null 2>&1; then
        if swapon /dev/zram0 -p 100 >/dev/null 2>&1; then
            ok "ZRAM: ${zram_size_mb}MB (${algorithm}, ${streams} потоков)"
            exit 0
        fi
    fi
fi

warn "Не удалось активировать ZRAM"
exit 0
EOF

    chmod 755 "$script_path"

    cat > "$service_path" <<'EOF'
[Unit]
Description=ZRAM Configuration
DefaultDependencies=no
Before=swap.target
After=local-fs.target
Conflicts=shutdown.target
ConditionVirtualization=!container

[Service]
Type=oneshot
ExecStart=/usr/local/bin/zram-setup.sh
RemainAfterExit=yes
TimeoutSec=30
StandardOutput=journal
Restart=no
User=root

[Install]
WantedBy=multi-user.target
EOF

    if systemctl daemon-reload 2>/dev/null && \
       systemctl enable zram.service 2>/dev/null && \
       systemctl start zram.service 2>/dev/null; then
        ok "ZRAM настроен и добавлен в автозапуск"
    else
        warn "Не удалось настроить службу ZRAM"
    fi
}

initramfs_fix() {
    log "Исправление mkinitcpio (удаление archiso)..."

    local conf="/etc/mkinitcpio.conf"
    local preset="/etc/mkinitcpio.d/linux.preset"
    local backup_suffix=".backup.$(date +%Y%m%d_%H%M%S)"

    if [ -f "$conf" ]; then
        cp "$conf" "${conf}${backup_suffix}" 2>/dev/null || true
    fi

    if [ -f "$preset" ]; then
        cp "$preset" "${preset}${backup_suffix}" 2>/dev/null || true
    fi

    if [ -f /etc/mkinitcpio.conf.d/en-os.conf ]; then
        if cp /etc/mkinitcpio.conf.d/en-os.conf "$conf" 2>/dev/null; then
            ok "Конфигурация en-os применена"
        fi
    fi

    if [ -f /etc/mkinitcpio.conf.d/archiso.conf ]; then
        sed -i 's/\barchiso\b//g; s/\barchiso_[^ ]*\b//g; s/  */ /g; s/^ //; s/ $//' \
            /etc/mkinitcpio.conf.d/archiso.conf 2>/dev/null || true
    fi

    if command -v mkinitcpio >/dev/null 2>&1; then
        if mkinitcpio -P 2>&1 | tee /tmp/mkinitcpio.log >/dev/null 2>&1; then
            ok "Initramfs переконфигурирован успешно!"
        else
            warn "Возникли проблемы с mkinitcpio, проверьте /tmp/mkinitcpio.log"
        fi
    else
        warn "mkinitcpio не установлен"
    fi
}

optimize_system() {
    log "Оптимизация системы для слабых ПК..."

    local cpu_count=$(nproc 2>/dev/null || echo 1)
    local mem_gb=$(awk '/MemTotal/ {print int($2/1024/1024)}' /proc/meminfo 2>/dev/null || echo 4)

    if [ "$mem_gb" -le 4 ]; then
        warn "Обнаружен слабый ПК (${mem_gb}GB RAM), применяем оптимизации"

        if [ -f /etc/systemd/system.conf ]; then
            sed -i 's/^#DefaultTimeoutStartSec=.*/DefaultTimeoutStartSec=30s/' /etc/systemd/system.conf 2>/dev/null || true
            sed -i 's/^#DefaultTimeoutStopSec=.*/DefaultTimeoutStopSec=15s/' /etc/systemd/system.conf 2>/dev/null || true
        fi

        if [ -f /etc/sysctl.d/99-sysctl.conf ] || [ -f /etc/sysctl.conf ]; then
            local sysctl_conf="/etc/sysctl.d/99-optimize.conf"
            cat > "$sysctl_conf" <<'EOF'
vm.swappiness=60
vm.vfs_cache_pressure=50
vm.dirty_ratio=10
vm.dirty_background_ratio=5
vm.dirty_writeback_centisecs=1500
vm.dirty_expire_centisecs=3000
kernel.numa_balancing=0
EOF
            sysctl -p "$sysctl_conf" 2>/dev/null || true
        fi
    fi

    if [ "$cpu_count" -le 2 ]; then
        if command -v systemctl >/dev/null 2>&1; then
            systemctl set-property user.slice CPUQuota=100% 2>/dev/null || true
        fi
    fi

    ok "Оптимизации применены"
}

clean_package_cache() {
    log "Оптимизация кэша пакетов..."

    if command -v paccache >/dev/null 2>&1; then
        paccache -rk0 2>/dev/null || true
    fi

    if [ -d /var/cache/pacman/pkg ]; then
        find /var/cache/pacman/pkg -name "*.pkg.tar.*" -atime +30 -delete 2>/dev/null || true
    fi

    ok "Кэш пакетов оптимизирован"
}

main() {
    check_root

    rm -f /root/.automated_script.sh 2>/dev/null || true

    echo "=== Выполняется постустановочная очистка системы ==="

    remove_sddm_autologin
    remove_calamares_autostart
    remove_installer_packages
    initramfs_fix
    systemctl_starting
    plymouth_fix
    zram_setup
    optimize_system
    clean_temporary_files
    clean_history_and_cache
    clean_package_cache
    disable_live_services

    echo "=== Очистка завершена успешно! ==="
    echo "Рекомендуется перезагрузить систему для применения изменений."
}

main "$@"
