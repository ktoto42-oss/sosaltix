#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║             НАСТРОЙКА Sosaltix Linux 1.0                       ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"

#==============================================================================
# 1. БАЗОВАЯ ИНФОРМАЦИЯ О СИСТЕМЕ
#==============================================================================
echo -e "${YELLOW}[1/15] Настройка базовой информации системы...${NC}"

# /etc/os-release - главный файл идентификации
cat > /etc/os-release << 'EOF'
NAME="Sosaltix"
PRETTY_NAME="Sosaltix Linux 1.0"
VERSION_ID="1.0"
VERSION="1.0"
ID=sosaltix
ID_LIKE=arch
BUILD_ID=rolling
ANSI_COLOR="1;36"
HOME_URL="https://github.com/ktoto42-oss/sosaltix"
DOCUMENTATION_URL="https://docs.github.com/ktoto42-oss/sosaltix"
SUPPORT_URL="https://t.me/ktotop640kg"
BUG_REPORT_URL="https://github.com/sosaltix/issues"
LOGO=sosaltix
EOF

# /etc/lsb-release - для совместимости с LSB
cat > /etc/lsb-release << 'EOF'
DISTRIB_ID=Sosaltix
DISTRIB_RELEASE=1.0
DISTRIB_CODENAME=rolling
DISTRIB_DESCRIPTION="Sosaltix Linux 1.0"
EOF

# Релизный файл
echo "Sosaltix Linux 1.0" > /etc/sosaltix-release
rm -f /etc/arch-release
ln -s /etc/sosaltix-release /etc/arch-release

#==============================================================================
# 2. FASTFETCH НАСТРОЙКИ
#==============================================================================
echo -e "${YELLOW}[2/15] Настройка fastfetch с вашим логотипом...${NC}"

# Проверяем наличие логотипа
if [ -f /logo.txt ]; then
    echo -e "${GREEN}✓ Найден логотип в /logo.txt${NC}"
    
    # Копируем логотип в системную директорию
    mkdir -p /usr/share/sosaltix
    cp /logo.txt /usr/share/sosaltix/logo.txt
    
    # Создаем конфигурацию fastfetch
    mkdir -p /etc/fastfetch
    
    # Создаем пресет для Sosaltix
    cat > /etc/fastfetch/sosaltix.jsonc << 'EOF'
{
    "$schema": "https://github.com/fastfetch-cli/fastfetch/raw/master/doc/json_schema.json",
    "logo": {
        "source": "/usr/share/sosaltix/logo.txt",
        "color": {
            "1": "cyan",
            "2": "blue"
        },
        "padding": {
            "left": 2,
            "right": 1
        }
    },
    "display": {
        "separator": " ➜ ",
        "color": "cyan"
    },
    "modules": [
        {
            "type": "title",
            "key": "   Sosaltix",
            "keyColor": "cyan"
        },
        {
            "type": "separator"
        },
        {
            "type": "os",
            "key": "   OS",
            "keyColor": "cyan"
        },
        {
            "type": "kernel",
            "key": "   Kernel",
            "keyColor": "cyan"
        },
        {
            "type": "uptime",
            "key": "   Uptime",
            "keyColor": "cyan"
        },
        {
            "type": "packages",
            "key": "   Packages",
            "keyColor": "cyan"
        },
        {
            "type": "shell",
            "key": "   Shell",
            "keyColor": "cyan"
        },
        {
            "type": "display",
            "key": "   Display",
            "keyColor": "cyan"
        },
        {
            "type": "de",
            "key": "   DE",
            "keyColor": "cyan"
        },
        {
            "type": "wm",
            "key": "   WM",
            "keyColor": "cyan"
        },
        {
            "type": "terminal",
            "key": "   Terminal",
            "keyColor": "cyan"
        },
        {
            "type": "cpu",
            "key": "   CPU",
            "keyColor": "cyan"
        },
        {
            "type": "gpu",
            "key": "   GPU",
            "keyColor": "cyan"
        },
        {
            "type": "memory",
            "key": "   Memory",
            "keyColor": "cyan"
        },
        {
            "type": "disk",
            "key": "   Disk",
            "keyColor": "cyan"
        },
        {
            "type": "localip",
            "key": "   LAN IP",
            "keyColor": "cyan"
        },
        {
            "type": "break"
        },
        {
            "type": "colors",
            "symbol": "circle"
        }
    ]
}
EOF

    # Создаем пользовательскую конфигурацию fastfetch
    mkdir -p /etc/skel/.config/fastfetch
    cp /etc/fastfetch/sosaltix.jsonc /etc/skel/.config/fastfetch/config.jsonc

else
    echo -e "${RED}✗ Логотип /logo.txt не найден! Использую стандартный ASCII${NC}"
    
    # Создаем запасной ASCII логотип
    mkdir -p /usr/share/sosaltix
    cat > /usr/share/sosaltix/logo.txt << 'EOF'
${c1}
            .-::-.            
         .:+ssssss+:.         
       .+ssssssssssss+.       
      .ssssssssssssssss.      
     -ssssssssssssssssss-     
    .ssssssssssssssssssss.    
    ossssssssssssssssssssso    
    ossssssssssssssssssssso    
    .ssssssssssssssssssss.     
     -ssssssssssssssssss-      
      .ssssssssssssssss.       
       .+ssssssssssss+.        
         .:+ssssss+:.          
            .-::-.             
                                
${c2}         Sosaltix Linux        
EOF
fi

# Алиас для быстрого запуска fastfetch с нашим логотипом
cat > /usr/local/bin/sosaltix-fetch << 'EOF'
#!/bin/bash
fastfetch -c /etc/fastfetch/sosaltix.jsonc
EOF
chmod +x /usr/local/bin/sosaltix-fetch

#==============================================================================
# 3. СЕТЕВЫЕ НАСТРОЙКИ
#==============================================================================
echo -e "${YELLOW}[3/15] Настройка сетевой идентификации...${NC}"

# Имя хоста
echo "sosaltix" > /etc/hostname

# /etc/hosts
cat > /etc/hosts << 'EOF'
# Sosaltix hosts file
127.0.0.1   localhost.localdomain localhost
::1         localhost.localdomain localhost
127.0.1.1   sosaltix.localdomain sosaltix
EOF

#==============================================================================
# 4. ПРИВЕТСТВИЯ И СООБЩЕНИЯ
#==============================================================================
echo -e "${YELLOW}[4/15] Настройка приветствий...${NC}"

# /etc/issue
cat > /etc/issue << 'EOF'
╭────────────────────────────────────────────────────╮
│     Sosaltix Linux 1.0                             │
│     https://github.com/ktoto42-oss/sosaltix        │
╰────────────────────────────────────────────────────╯

Kernel \r on \l (\s \m \n)

EOF

# /etc/motd
cat > /etc/motd << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║                    Welcome to Sosaltix!                      ║
║                                                              ║
║                 Fastfetch is ready to use!                   ║
║                                                              ║
║  • Type 'fastfetch' to see system information                ║
║  • Type 'sosaltix-fetch' for custom view                     ║
║  • Type 'sosaltix-help' for assistance                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF

#==============================================================================
# 5. PACMAN
#==============================================================================
echo -e "${YELLOW}[5/15] Настройка pacman...${NC}"

cat > /etc/pacman.conf << 'EOF'
#
# /etc/pacman.conf for Sosaltix
#

[options]
Architecture = auto
Color
ILoveCandy
ParallelDownloads = 5
CheckSpace
VerbosePkgLists

[core]
Include = /etc/pacman.d/mirrorlist

[extra]
Include = /etc/pacman.d/mirrorlist

[community]
Include = /etc/pacman.d/mirrorlist

[multilib]
Include = /etc/pacman.d/mirrorlist
EOF

#==============================================================================
# 6. BASH НАСТРОЙКИ (с fastfetch)
#==============================================================================
echo -e "${YELLOW}[6/15] Настройка Bash...${NC}"

# Системный bashrc
cat >> /etc/bash.bashrc << 'EOF'
# Sosaltix bash configuration
if [ -f /etc/sosaltix-release ]; then
    echo -e "\e[36m◈ Sosaltix Linux ◈\e[0m"
fi

# Запуск fastfetch при входе (если установлен)
if command -v fastfetch &> /dev/null; then
    fastfetch
fi

alias sosaltix-fetch='fastfetch -c /etc/fastfetch/sosaltix.jsonc'
alias sosaltix-help='cat /etc/motd'
alias update='sudo pacman -Syu'
alias install='sudo pacman -S'
alias remove='sudo pacman -R'
alias search='pacman -Ss'
EOF

# Пользовательский bashrc
cat > /etc/skel/.bashrc << 'EOF'
# Sosaltix user bashrc
source /etc/bash.bashrc

export EDITOR=nano
export BROWSER=firefox

# Кастомный промпт
PS1='\[\e[36m\][sosaltix\[\e[0m\] \w]$ '
EOF

# Для liveuser
cp /etc/skel/.bashrc /home/liveuser/.bashrc 2>/dev/null || true

#==============================================================================
# 7. СИСТЕМНЫЕ УТИЛИТЫ
#==============================================================================
echo -e "${YELLOW}[7/15] Создание системных утилит...${NC}"

mkdir -p /usr/local/bin

# Утилита информации о системе
cat > /usr/local/bin/sosaltix-info << 'EOF'
#!/bin/bash
echo "╔════════════════════════════════════╗"
echo "║     Sosaltix System Information    ║"
echo "╠════════════════════════════════════╣"
echo "║ Version: 1.0                       ║"
echo "║ Kernel: $(uname -r)                ║"
echo "║ Uptime: $(uptime -p)                ║"
echo "║ Shell: $SHELL                       ║"
echo "║ Fastfetch: $(command -v fastfetch &>/dev/null && echo '✓' || echo '✗')"
echo "╚════════════════════════════════════╝"
EOF

# Утилита помощи
cat > /usr/local/bin/sosaltix-help << 'EOF'
#!/bin/bash
cat /etc/motd
echo ""
echo "Available commands:"
echo "  fastfetch        - Show system information with ASCII logo"
echo "  sosaltix-fetch   - Show system information (custom preset)"
echo "  sosaltix-info    - Show basic system information"
echo "  sosaltix-update  - Update system"
EOF

# Утилита обновления
cat > /usr/local/bin/sosaltix-update << 'EOF'
#!/bin/bash
echo "◈ Updating Sosaltix..."
sudo pacman -Syu
echo ""
echo "◈ Update complete! Type 'fastfetch' to see system info"
EOF

chmod +x /usr/local/bin/sosaltix-*

#==============================================================================
# 8. ПРОВЕРКА FASTFETCH
#==============================================================================
echo -e "${YELLOW}[8/15] Проверка fastfetch...${NC}"

# Создаем скрипт проверки
cat > /tmp/check_fastfetch.sh << 'EOF'
#!/bin/bash
echo "Проверка fastfetch:"
if command -v fastfetch &> /dev/null; then
    echo "✓ fastfetch установлен"
    echo "✓ Конфигурация: /etc/fastfetch/sosaltix.jsonc"
    echo "✓ Логотип: /usr/share/sosaltix/logo.txt"
else
    echo "✗ fastfetch НЕ установлен"
    echo "  Установите: sudo pacman -S fastfetch"
fi
EOF

chmod +x /tmp/check_fastfetch.sh
/tmp/check_fastfetch.sh

#==============================================================================
# 9. ПРАВА ДОСТУПА
#==============================================================================
echo -e "${YELLOW}[9/15] Настройка прав доступа...${NC}"

# Права на системные файлы
chmod 644 /etc/os-release
chmod 644 /etc/lsb-release
chmod 644 /etc/hostname
chmod 644 /etc/issue*
chmod 644 /etc/motd

# Права на логотип
chmod 644 /usr/share/sosaltix/logo.txt 2>/dev/null || true

# Права на домашнюю директорию
chown -R liveuser:liveuser /home/liveuser 2>/dev/null || true

#==============================================================================
# 10. ЗАВЕРШЕНИЕ
#==============================================================================
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      НАСТРОЙКА Sosaltix ЗАВЕРШЕНА УСПЕШНО!                    ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"

# Информация о системе
echo -e "\n${CYAN}Информация о системе:${NC}"
echo "  • Дистрибутив: Sosaltix Linux 1.0"
echo "  • Fastfetch: $(command -v fastfetch &>/dev/null && echo 'установлен' || echo 'НЕ установлен')"

# Информация о логотипе
if [ -f /usr/share/sosaltix/logo.txt ]; then
    echo "  • Логотип: /usr/share/sosaltix/logo.txt"
    echo -e "\n${CYAN}Предпросмотр логотипа:${NC}"
    cat /usr/share/sosaltix/logo.txt
fi
