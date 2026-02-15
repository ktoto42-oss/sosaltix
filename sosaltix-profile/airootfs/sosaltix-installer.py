import os
import sys
import subprocess
import json
import re
from typing import List, Dict, Optional, Tuple
import shutil

# Цвета для вывода
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_step(message: str):
    """Вывод шага установки"""
    print(f"{Colors.BLUE}::{Colors.END} {message}")

def print_success(message: str):
    """Вывод успешного сообщения"""
    print(f"{Colors.GREEN}✓{Colors.END} {message}")

def print_error(message: str):
    """Вывод ошибки"""
    print(f"{Colors.FAIL}✗{Colors.END} {message}")

def print_warning(message: str):
    """Вывод предупреждения"""
    print(f"{Colors.WARNING}!{Colors.END} {message}")

def run_command(command: List[str], check: bool = True) -> bool:
    """Выполнение команды в shell"""
    try:
        subprocess.run(command, check=check)
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Ошибка выполнения команды: {' '.join(command)}")
        return False

class SosaltixInstaller:
    def __init__(self):
        self.disk = None
        self.hostname = "sosaltix"
        self.username = None
        self.password = None
        self.root_password = None
        self.locale = "en_US.UTF-8"
        self.keymap = "us"
        self.timezone = "UTC"
        self.desktop_environment = None
        self.kernel = "linux"
        self.bootloader = "grub"
        self.filesystem = "ext4"
        self.additional_packages = []
        
    def check_environment(self) -> bool:
        """Проверка окружения для установки"""
        print_step("Проверка окружения...")
        
        # Проверка, запущен ли скрипт с правами root
        if os.geteuid() != 0:
            print_error("Скрипт должен быть запущен с правами root")
            return False
            
        # Проверка наличия archiso
        if not os.path.exists("/run/archiso"):
            print_warning("Вы не в live-среде ArchISO. Установка может быть невозможна.")
            response = input("Продолжить? (y/N): ").lower()
            if response != 'y':
                return False
                
        print_success("Окружение проверено")
        return True
    
    def get_disks(self) -> List[str]:
        """Получение списка доступных дисков"""
        disks = []
        try:
            result = subprocess.run(['lsblk', '-d', '-o', 'NAME,SIZE,MODEL', '-n'], 
                                  capture_output=True, text=True)
            for line in result.stdout.strip().split('\n'):
                if line and not 'loop' in line:
                    disks.append(line)
        except:
            pass
        return disks
    
    def select_disk(self) -> bool:
        """Выбор диска для установки"""
        print_step("Выбор диска для установки")
        print("\nДоступные диски:")
        
        disks = self.get_disks()
        if not disks:
            print_error("Не найдено доступных дисков")
            return False
            
        for i, disk in enumerate(disks, 1):
            print(f"{i}. {disk}")
            
        while True:
            try:
                choice = int(input(f"\nВыберите диск (1-{len(disks)}): "))
                if 1 <= choice <= len(disks):
                    disk_info = disks[choice-1].split()[0]
                    self.disk = f"/dev/{disk_info}"
                    print_success(f"Выбран диск: {self.disk}")
                    return True
            except ValueError:
                pass
            print_error("Неверный выбор")
    
    def ask_hostname(self):
        """Запрос имени хоста"""
        hostname = input(f"\nИмя хоста [{self.hostname}]: ").strip()
        if hostname:
            self.hostname = hostname
        print_success(f"Имя хоста: {self.hostname}")
    
    def ask_user_credentials(self):
        """Запрос учетных данных пользователя"""
        print_step("Создание пользователя")
        
        # Имя пользователя
        while True:
            username = input("\nИмя пользователя: ").strip()
            if username and re.match(r'^[a-z_][a-z0-9_-]*$', username):
                self.username = username
                break
            print_error("Некорректное имя пользователя")
        
        # Пароль пользователя
        while True:
            password = input("Пароль пользователя: ")
            if password:
                confirm = input("Подтвердите пароль: ")
                if password == confirm:
                    self.password = password
                    break
                else:
                    print_error("Пароли не совпадают")
            else:
                print_error("Пароль не может быть пустым")
        
        # Пароль root
        print_step("Установка пароля root")
        while True:
            root_pass = input("Пароль root: ")
            if root_pass:
                confirm = input("Подтвердите пароль root: ")
                if root_pass == confirm:
                    self.root_password = root_pass
                    break
                else:
                    print_error("Пароли не совпадают")
            else:
                print_error("Пароль root не может быть пустым")
    
    def ask_locale(self):
        """Выбор локали"""
        print_step("Выбор локали")
        locales = [
            "en_US.UTF-8 UTF-8",
            "ru_RU.UTF-8 UTF-8",
            "de_DE.UTF-8 UTF-8",
            "fr_FR.UTF-8 UTF-8",
            "es_ES.UTF-8 UTF-8"
        ]
        
        print("\nДоступные локали:")
        for i, loc in enumerate(locales, 1):
            print(f"{i}. {loc}")
            
        while True:
            try:
                choice = int(input(f"\nВыберите локаль (1-{len(locales)}): "))
                if 1 <= choice <= len(locales):
                    self.locale = locales[choice-1].split()[0]
                    break
            except ValueError:
                pass
            print_error("Неверный выбор")
    
    def ask_keymap(self):
        """Выбор раскладки клавиатуры"""
        print_step("Выбор раскладки клавиатуры")
        keymaps = ["us", "ru", "de", "fr", "es"]
        
        print("\nДоступные раскладки:")
        for i, km in enumerate(keymaps, 1):
            print(f"{i}. {km}")
            
        while True:
            try:
                choice = int(input(f"\nВыберите раскладку (1-{len(keymaps)}): "))
                if 1 <= choice <= len(keymaps):
                    self.keymap = keymaps[choice-1]
                    break
            except ValueError:
                pass
            print_error("Неверный выбор")
    
    def ask_timezone(self):
        """Выбор часового пояса"""
        print_step("Выбор часового пояса")
        timezones = ["UTC", "Europe/Moscow", "Europe/Berlin", "America/New_York"]
        
        print("\nДоступные часовые пояса:")
        for i, tz in enumerate(timezones, 1):
            print(f"{i}. {tz}")
            
        while True:
            try:
                choice = int(input(f"\nВыберите часовой пояс (1-{len(timezones)}): "))
                if 1 <= choice <= len(timezones):
                    self.timezone = timezones[choice-1]
                    break
            except ValueError:
                pass
            print_error("Неверный выбор")
    
    def ask_desktop_environment(self):
        """Выбор окружения рабочего стола"""
        print_step("Выбор окружения рабочего стола")
        desktops = [
            {"name": "Без графического окружения", "packages": []},
            {"name": "Sosaltix Desktop (XFCE)", "packages": ["xfce4", "xfce4-goodies"]},
            {"name": "GNOME", "packages": ["gnome", "gnome-extra"]},
            {"name": "KDE Plasma", "packages": ["plasma-meta", "applications-meta"]},
            {"name": "MATE", "packages": ["mate", "mate-extra"]}
        ]
        
        print("\nДоступные окружения:")
        for i, de in enumerate(desktops, 1):
            print(f"{i}. {de['name']}")
            
        while True:
            try:
                choice = int(input(f"\nВыберите окружение (1-{len(desktops)}): "))
                if 1 <= choice <= len(desktops):
                    if choice > 1:  # Не выбираем "Без графического окружения"
                        self.desktop_environment = desktops[choice-1]["name"]
                        self.additional_packages.extend(desktops[choice-1]["packages"])
                    break
            except ValueError:
                pass
            print_error("Неверный выбор")
    
    def ask_additional_packages(self):
        """Запрос дополнительных пакетов"""
        print_step("Дополнительные пакеты")
        packages = input("Введите дополнительные пакеты для установки (через пробел): ").strip()
        if packages:
            self.additional_packages.extend(packages.split())
    
    def partition_disk(self) -> bool:
        """Разметка диска"""
        print_step(f"Разметка диска {self.disk}")
        print_warning("ВНИМАНИЕ: Все данные на диске будут уничтожены!")
        response = input("Продолжить? (y/N): ").lower()
        if response != 'y':
            return False
        
        # Создание меток разделов
        commands = [
            ['parted', '-s', self.disk, 'mklabel', 'gpt'],
            ['parted', '-s', self.disk, 'mkpart', 'primary', 'fat32', '1MiB', '513MiB'],
            ['parted', '-s', self.disk, 'set', '1', 'esp', 'on'],
            ['parted', '-s', self.disk, 'mkpart', 'primary', 'ext4', '513MiB', '100%']
        ]
        
        for cmd in commands:
            if not run_command(cmd):
                return False
        
        # Форматирование разделов
        run_command(['mkfs.fat', '-F32', f'{self.disk}1'])
        run_command([f'mkfs.{self.filesystem}', '-F', f'{self.disk}2'])
        
        # Монтирование
        run_command(['mount', f'{self.disk}2', '/mnt'])
        run_command(['mkdir', '-p', '/mnt/boot'])
        run_command(['mount', f'{self.disk}1', '/mnt/boot'])
        
        print_success("Диск размечен и отформатирован")
        return True
    
    def install_base_system(self) -> bool:
        """Установка базовой системы"""
        print_step("Установка базовой системы")
        
        # Список базовых пакетов
        base_packages = [
            'base', 'base-devel', 'linux', 'linux-firmware',
            'sudo', 'vim', 'nano', 'networkmanager', 'grub', 'efibootmgr'
        ]
        
        # Установка через pacstrap
        cmd = ['pacstrap', '/mnt'] + base_packages
        if not run_command(cmd):
            return False
        
        # Генерация fstab
        run_command(['genfstab', '-U', '/mnt'], check=False)
        with open('/mnt/etc/fstab', 'w') as f:
            subprocess.run(['genfstab', '-U', '/mnt'], stdout=f)
        
        print_success("Базовая система установлена")
        return True
    
    def configure_system(self) -> bool:
        """Настройка системы"""
        print_step("Настройка системы")
        
        # Установка часового пояса
        if os.path.exists(f'/usr/share/zoneinfo/{self.timezone}'):
            os.system(f'ln -sf /usr/share/zoneinfo/{self.timezone} /mnt/etc/localtime')
            run_command(['arch-chroot', '/mnt', 'hwclock', '--systohc'])
        
        # Настройка локали
        with open('/mnt/etc/locale.gen', 'a') as f:
            f.write(f'{self.locale} UTF-8\n')
        run_command(['arch-chroot', '/mnt', 'locale-gen'])
        
        with open('/mnt/etc/locale.conf', 'w') as f:
            f.write(f'LANG={self.locale}\n')
        
        # Настройка раскладки клавиатуры
        with open('/mnt/etc/vconsole.conf', 'w') as f:
            f.write(f'KEYMAP={self.keymap}\n')
        
        # Настройка имени хоста
        with open('/mnt/etc/hostname', 'w') as f:
            f.write(f'{self.hostname}\n')
        
        # Настройка hosts
        with open('/mnt/etc/hosts', 'w') as f:
            f.write(f'127.0.0.1\tlocalhost\n')
            f.write(f'::1\t\tlocalhost\n')
            f.write(f'127.0.1.1\t{self.hostname}.localdomain\t{self.hostname}\n')
        
        print_success("Система настроена")
        return True
    
    def install_bootloader(self) -> bool:
        """Установка загрузчика"""
        print_step("Установка загрузчика GRUB")
        
        # Установка GRUB
        run_command(['arch-chroot', '/mnt', 'grub-install', '--target=x86_64-efi', 
                    '--efi-directory=/boot', '--bootloader-id=GRUB'])
        
        # Создание конфигурации GRUB
        run_command(['arch-chroot', '/mnt', 'grub-mkconfig', '-o', '/boot/grub/grub.cfg'])
        
        print_success("Загрузчик установлен")
        return True
    
    def setup_users(self) -> bool:
        """Настройка пользователей"""
        print_step("Настройка пользователей")
        
        # Установка пароля root
        proc = subprocess.Popen(['arch-chroot', '/mnt', 'passwd'], 
                               stdin=subprocess.PIPE)
        proc.communicate(input=f'{self.root_password}\n{self.root_password}\n'.encode())
        
        # Создание пользователя
        run_command(['arch-chroot', '/mnt', 'useradd', '-m', self.username])
        
        # Установка пароля пользователя
        proc = subprocess.Popen(['arch-chroot', '/mnt', 'passwd', self.username], 
                               stdin=subprocess.PIPE)
        proc.communicate(input=f'{self.password}\n{self.password}\n'.encode())
        
        # Добавление пользователя в группы
        run_command(['arch-chroot', '/mnt', 'usermod', '-aG', 'wheel,audio,video,storage', self.username])
        
        # Настройка sudo
        with open('/mnt/etc/sudoers.d/wheel', 'w') as f:
            f.write('%wheel ALL=(ALL) ALL\n')
        
        print_success("Пользователи настроены")
        return True
    
    def enable_services(self) -> bool:
        """Включение необходимых сервисов"""
        print_step("Включение сервисов")
        
        services = ['NetworkManager', 'systemd-timesyncd']
        for service in services:
            run_command(['arch-chroot', '/mnt', 'systemctl', 'enable', service])
        
        print_success("Сервисы включены")
        return True
    
    def install_additional_packages(self) -> bool:
        """Установка дополнительных пакетов"""
        if self.additional_packages:
            print_step("Установка дополнительных пакетов")
            run_command(['arch-chroot', '/mnt', 'pacman', '-S', '--noconfirm'] + self.additional_packages)
            print_success("Дополнительные пакеты установлены")
        return True
    
    def finalize(self):
        """Завершение установки"""
        print_step("Завершение установки")
        
        # Размонтирование
        run_command(['umount', '-R', '/mnt'], check=False)
        
        print_success("Установка Sosaltix завершена!")
        print("\nВы можете перезагрузить систему.")
        response = input("Перезагрузить сейчас? (y/N): ").lower()
        if response == 'y':
            run_command(['reboot'])
    
    def run(self):
        """Основной процесс установки"""
        print(f"{Colors.BOLD}{Colors.HEADER}")
        print("╔════════════════════════════════════╗")
        print("║     Установщик Sosaltix 1.0        ║")
        print("╚════════════════════════════════════╝")
        print(f"{Colors.END}")
        
        if not self.check_environment():
            return
        
        # Сбор информации
        if not self.select_disk():
            return
        self.ask_hostname()
        self.ask_user_credentials()
        self.ask_locale()
        self.ask_keymap()
        self.ask_timezone()
        self.ask_desktop_environment()
        self.ask_additional_packages()
        
        # Подтверждение
        print(f"\n{Colors.BOLD}Параметры установки:{Colors.END}")
        print(f"Диск: {self.disk}")
        print(f"Имя хоста: {self.hostname}")
        print(f"Пользователь: {self.username}")
        print(f"Локаль: {self.locale}")
        print(f"Раскладка: {self.keymap}")
        print(f"Часовой пояс: {self.timezone}")
        print(f"Окружение: {self.desktop_environment or 'Нет'}")
        print(f"Доп. пакеты: {' '.join(self.additional_packages) or 'Нет'}")
        
        response = input(f"\n{Colors.WARNING}Начать установку? (y/N): {Colors.END}").lower()
        if response != 'y':
            print("Установка отменена")
            return
        
        # Выполнение установки
        steps = [
            ("Разметка диска", self.partition_disk),
            ("Установка базовой системы", self.install_base_system),
            ("Настройка системы", self.configure_system),
            ("Установка загрузчика", self.install_bootloader),
            ("Настройка пользователей", self.setup_users),
            ("Включение сервисов", self.enable_services),
            ("Установка доп. пакетов", self.install_additional_packages)
        ]
        
        for step_name, step_func in steps:
            print(f"\n{Colors.BOLD}[ {step_name} ]{Colors.END}")
            if not step_func():
                print_error(f"Ошибка на шаге: {step_name}")
                return
        
        self.finalize()

if __name__ == "__main__":
    installer = SosaltixInstaller()
    try:
        installer.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Установка прервана пользователем{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Критическая ошибка: {e}")
        sys.exit(1)