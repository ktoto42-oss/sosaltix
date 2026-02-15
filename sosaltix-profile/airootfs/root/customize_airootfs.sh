#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     SoSaltix Live/Installer Configuration          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"

#==============================================================================
# 1. НАСТРОЙКА ЛОКАЛИ И ШРИФТОВ (кириллица)
#==============================================================================
echo -e "${YELLOW}[1/5] Настройка локали и шрифтов...${NC}"

# Генерация локалей
cat > /etc/locale.gen << 'EOF'
en_US.UTF-8 UTF-8
ru_RU.UTF-8 UTF-8
uk_UA.UTF-8 UTF-8
EOF
locale-gen

# Настройка системной локали
cat > /etc/locale.conf << 'EOF'
LANG=en_US.UTF-8
LC_CTYPE="ru_RU.UTF-8"
LC_NUMERIC="ru_RU.UTF-8"
LC_TIME="ru_RU.UTF-8"
LC_COLLATE="ru_RU.UTF-8"
LC_MONETARY="ru_RU.UTF-8"
LC_MESSAGES="en_US.UTF-8"
LC_PAPER="ru_RU.UTF-8"
LC_NAME="ru_RU.UTF-8"
LC_ADDRESS="ru_RU.UTF-8"
LC_TELEPHONE="ru_RU.UTF-8"
LC_MEASUREMENT="ru_RU.UTF-8"
LC_IDENTIFICATION="ru_RU.UTF-8"
EOF

# Настройка виртуальной консоли для кириллицы
cat > /etc/vconsole.conf << 'EOF'
KEYMAP=ru
FONT=cyr-sun16
FONT_MAP=8859-1_to_koi8-r
EOF

# Установка шрифтов для терминала
pacman -S --noconfirm terminus-font ttf-dejavu ttf-liberation

#==============================================================================
# 2. МОНТИРОВАНИЕ ЛОКАЛЬНОГО РЕПОЗИТОРИЯ
#==============================================================================
echo -e "${YELLOW}[2/5] Монтирование локального репозитория...${NC}"

mkdir -p /run/archiso/repo
mount --bind /run/archiso/bootmnt/repo /run/archiso/repo

#==============================================================================
# 3. НАСТРОЙКА СЕТИ
#==============================================================================
echo -e "${YELLOW}[3/5] Настройка сети...${NC}"

systemctl enable NetworkManager
systemctl enable sshd

# Настройка хоста
echo "sosaltix-live" > /etc/hostname

cat > /etc/hosts << 'EOF'
127.0.0.1   localhost.localdomain localhost
::1         localhost.localdomain localhost
127.0.1.1   sosaltix-live.localdomain sosaltix-live
EOF

#==============================================================================
# 4. НАСТРОЙКА BASH (с поддержкой кириллицы)
#==============================================================================
echo -e "${YELLOW}[4/5] Настройка Bash...${NC}"

cat > /root/.bashrc << 'EOF'
# SoSaltix Live Bash Configuration

# Поддержка кириллицы
export LANG=ru_RU.UTF-8
export LC_ALL=ru_RU.UTF-8

# Алиасы
alias ls='ls --color=auto'
alias ll='ls -la'
alias la='ls -A'
alias grep='grep --color=auto'

# Приглашение командной строки
PS1='\[\e[36m\][sosaltix@live \W]\$ \[\e[0m\]'

# Информация при входе
echo "╔════════════════════════════════════════════════════╗"
echo "║     SoSaltix Live/Installer                        ║"
echo "║     Версия: 1.0                                    ║"
echo "║                                                    ║"
echo "║     Для запуска установщика введите:               ║"
echo "║     python3 /root/offline_installer.py             ║"
echo "╚════════════════════════════════════════════════════╝"
EOF

#==============================================================================
# 5. КОПИРОВАНИЕ УСТАНОВЩИКА
#==============================================================================
echo -e "${YELLOW}[5/5] Копирование офлайн-установщика...${NC}"

# Установщик будет добавлен отдельно
chmod +x /root/offline_installer.py

# Создание символической ссылки для удобства
ln -s /root/offline_installer.py /usr/local/bin/sosaltix-install

echo -e "${GREEN}✅ Настройка live-системы завершена!${NC}"