#!/usr/bin/env python3
# offline_installer.py - Офлайн-установщик SoSaltix

import os
import sys
import subprocess
import json
import time
from pathlib import Path

# Цвета для вывода
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

class SoSaltixInstaller:
    def __init__(self):
        self.repo_path = "/run/archiso/repo/x86_64"
        self.mount_point = "/mnt"
        self.packages_file = "/root/packages.json"
        
    def print_banner(self):
        """Вывод баннера"""
        os.system('clear')
        print(f"""{Colors.BLUE}
╔════════════════════════════════════════════════════╗
║     SoSaltix Linux 1.0 Offline Installer          ║
║                                                    ║
║     ███████╗ ██████╗ ███████╗ █████╗ ██╗     ████████╗██╗██╗  ██╗
║     ██╔════╝██╔═══██╗██╔════╝██╔══██╗██║     ╚══██╔══╝██║╚██╗██╔╝
║     ███████╗██║   ██║███████╗███████║██║        ██║   ██║ ╚███╔╝ 
║     ╚════██║██║   ██║╚════██║██╔══██║██║        ██║   ██║ ██╔██╗ 
║     ███████║╚██████╔╝███████║██║  ██║███████╗   ██║   ██║██╔╝ ██╗
║     ╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝╚═╝  ╚═╝
║                                                    ║
║              Офлайн-установщик v1.0                ║
╚════════════════════════════════════════════════════╝{Colors.END}""")
        
    def check_repo(self):
        """Проверка наличия локального репозитория"""
        print(f"\n{Colors.YELLOW}🔍 Проверка локального репозитория...{Colors.END}")
        
        if not os.path.exists(self.repo_path):
            print(f"{Colors.RED}❌ Репозиторий не найден!{Colors.END}")
            return False
            
        packages = list(Path(self.repo_path).glob("*.pkg.tar.zst"))
        print(f"{Colors.GREEN}✅ Найдено пакетов: {len(packages)}{Colors.END}")
        return True
        
    def select_installation_type(self):
        """Выбор типа установки"""
        print(f"\n{Colors.BLUE}📦 Выберите тип установки:{Colors.END}")
        print("  1) Минимальная (только base, без DE)")
        print("  2) KDE Plasma (полная рабочая станция)")
        print("  3) Выход")
        
        choice = input(f"\n{Colors.YELLOW}Ваш выбор [1-3]:{Colors.END} ").strip()
        
        if choice == "1":
            return "minimal"
        elif choice == "2":
            return "kde"
        elif choice == "3":
            sys.exit(0)
        else:
            print(f"{Colors.RED}Неверный выбор!{Colors.END}")
            return self.select_installation_type()
            
    def get_packages(self, install_type):
        """Получение списка пакетов для установки"""
        with open(self.packages_file, 'r') as f:
            packages = json.load(f)
            
        if install_type == "minimal":
            return packages['base']
        else:  # kde
            return packages['base'] + packages['kde']
            
    def prepare_disk(self):
        """Подготовка диска"""
        print(f"\n{Colors.BLUE}💾 Подготовка диска...{Colors.END}")
        
        # Показать доступные диски
        subprocess.run("lsblk", shell=True)
        
        disk = input(f"\n{Colors.YELLOW}Введите диск для установки (например, /dev/sda):{Colors.END} ").strip()
        
        if not os.path.exists(disk):
            print(f"{Colors.RED}❌ Диск не найден!{Colors.END}")
            return self.prepare_disk()
            
        print(f"\n{Colors.RED}⚠ ВНИМАНИЕ: Все данные на {disk} будут уничтожены!{Colors.END}")
        confirm = input(f"{Colors.YELLOW}Продолжить? (yes/no):{Colors.END} ").strip()
        
        if confirm.lower() != 'yes':
            print(f"{Colors.YELLOW}Установка отменена{Colors.END}")
            return None
            
        return disk
        
    def partition_disk(self, disk):
        """Разметка диска"""
        print(f"\n{Colors.BLUE}🔨 Разметка диска...{Colors.END}")
        
        # Создание разделов
        # BIOS boot partition
        subprocess.run(f"parted {disk} mklabel gpt", shell=True, check=True)
        subprocess.run(f"parted {disk} mkpart primary fat32 1MiB 512MiB", shell=True, check=True)
        subprocess.run(f"parted {disk} set 1 esp on", shell=True, check=True)
        subprocess.run(f"parted {disk} mkpart primary ext4 512MiB 100%", shell=True, check=True)
        
        # Форматирование
        subprocess.run(f"mkfs.fat -F32 {disk}1", shell=True, check=True)
        subprocess.run(f"mkfs.ext4 -F {disk}2", shell=True, check=True)
        
        # Монтирование
        subprocess.run(f"mount {disk}2 {self.mount_point}", shell=True, check=True)
        subprocess.run(f"mkdir -p {self.mount_point}/boot", shell=True, check=True)
        subprocess.run(f"mount {disk}1 {self.mount_point}/boot", shell=True, check=True)
        
        return True
        
    def install_system(self, packages):
        """Установка системы"""
        print(f"\n{Colors.BLUE}📦 Установка пакетов...{Colors.END}")
        
        # Создание временного pacman.conf для установки
        pacman_conf = """
[options]
Architecture = auto
Color
ParallelDownloads = 5

[sosaltix]
SigLevel = Optional TrustAll
Server = file:///run/archiso/repo/x86_64
"""
        with open("/tmp/pacman.conf", "w") as f:
            f.write(pacman_conf)
            
        # Копирование базы данных репозитория
        subprocess.run(f"mkdir -p {self.mount_point}/var/lib/pacman/local", shell=True)
        subprocess.run(f"mkdir -p {self.mount_point}/opt/sosaltix-repo", shell=True)
        subprocess.run(f"cp -r /run/archiso/repo/* {self.mount_point}/opt/sosaltix-repo/", shell=True)
        
        # Установка базовой системы
        cmd = f"pacstrap -C /tmp/pacman.conf -c -G {self.mount_point} {' '.join(packages)}"
        result = subprocess.run(cmd, shell=True)
        
        if result.returncode != 0:
            print(f"{Colors.RED}❌ Ошибка установки!{Colors.END}")
            return False
            
        return True
        
    def configure_system(self):
        """Настройка установленной системы"""
        print(f"\n{Colors.BLUE}⚙ Настройка системы...{Colors.END}")
        
        # Генерация fstab
        subprocess.run(f"genfstab -U {self.mount_point} >> {self.mount_point}/etc/fstab", shell=True)
        
        # Настройка локального репозитория в установленной системе
        repo_conf = """
[sosaltix]
SigLevel = Optional TrustAll
Server = file:///opt/sosaltix-repo/x86_64
"""
        with open(f"{self.mount_point}/etc/pacman.conf", "a") as f:
            f.write(repo_conf)
            
        # Chroot команды
        chroot_cmds = [
            "ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime",
            "hwclock --systohc",
            "sed -i 's/^#ru_RU.UTF-8/ru_RU.UTF-8/' /etc/locale.gen",
            "locale-gen",
            'echo "LANG=ru_RU.UTF-8" > /etc/locale.conf',
            'echo "KEYMAP=ru" > /etc/vconsole.conf',
            'echo "FONT=cyr-sun16" >> /etc/vconsole.conf',
            'echo "sosaltix" > /etc/hostname',
            "systemctl enable NetworkManager",
            "systemctl enable sshd",
            "mkinitcpio -P"
        ]
        
        for cmd in chroot_cmds:
            subprocess.run(f"arch-chroot {self.mount_point} {cmd}", shell=True)
            
        # Установка пароля root
        print(f"\n{Colors.YELLOW}🔐 Установка пароля root:{Colors.END}")
        subprocess.run(f"arch-chroot {self.mount_point} passwd", shell=True)
        
        return True
        
    def install_bootloader(self, disk):
        """Установка загрузчика"""
        print(f"\n{Colors.BLUE}🖥 Установка загрузчика...{Colors.END}")
        
        # Установка GRUB
        subprocess.run(f"arch-chroot {self.mount_point} grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=SoSaltix", shell=True)
        subprocess.run(f"arch-chroot {self.mount_point} grub-mkconfig -o /boot/grub/grub.cfg", shell=True)
        
        return True
        
    def run(self):
        """Запуск установщика"""
        self.print_banner()
        
        if not self.check_repo():
            input(f"\n{Colors.YELLOW}Нажмите Enter для выхода...{Colors.END}")
            return
            
        install_type = self.select_installation_type()
        packages = self.get_packages(install_type)
        
        print(f"\n{Colors.GREEN}Будет установлено пакетов: {len(packages)}{Colors.END}")
        
        disk = self.prepare_disk()
        if not disk:
            return
            
        print(f"\n{Colors.YELLOW}Начинаем установку на {disk}...{Colors.END}")
        
        try:
            self.partition_disk(disk)
            self.install_system(packages)
            self.configure_system()
            self.install_bootloader(disk)
            
            print(f"\n{Colors.GREEN}✅ Установка успешно завершена!{Colors.END}")
            print(f"{Colors.GREEN}🎉 SoSaltix установлен на {disk}{Colors.END}")
            
        except Exception as e:
            print(f"{Colors.RED}❌ Ошибка установки: {e}{Colors.END}")
            
        input(f"\n{Colors.YELLOW}Нажмите Enter для выхода...{Colors.END}")

if __name__ == "__main__":
    installer = SoSaltixInstaller()
    
    # Проверка прав root
    if os.geteuid() != 0:
        print(f"{Colors.RED}❌ Установщик должен быть запущен от root!{Colors.END}")
        sys.exit(1)
        
    installer.run()