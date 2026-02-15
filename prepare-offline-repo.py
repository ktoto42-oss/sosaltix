#!/usr/bin/env python3

import os
import subprocess
import sys
from pathlib import Path

class OfflineRepoBuilder:
    def __init__(self):
        self.build_dir = Path.home() / 'sosaltix-build'
        self.repo_dir = self.build_dir / 'sosaltix-profile' / 'repo' / 'x86_64'
        
        # Пакеты для разных вариантов установки
        self.packages = {
            'base': [
                'base',
                'linux-zen',
                'linux-firmware',
                'sudo',
                'grub',
                'efibootmgr',
                'networkmanager',
                'dhcpcd',
                'iwd',
                'wireless_tools',
                'wpa_supplicant',
                'dialog',
                'bash-completion',
                'man-db',
                'man-pages',
                'texinfo',
                'nano',
                'vim',
                'htop',
                'neofetch',
                'git',
                'curl',
                'wget',
                'openssh',
                'rsync',
                'unzip',
                'p7zip',
                'ntfs-3g',
                'exfat-utils',
                'dosfstools',
                'mesa',
                'xf86-video-vesa',
                'xf86-video-intel',
                'xf86-video-amdgpu',
                'xf86-video-nouveau',
                'pipewire',
                'pipewire-alsa',
                'pipewire-pulse',
                'pipewire-jack'
            ],
            'kde': [
                'plasma-desktop',
                'plasma-workspace',
                'plasma-nm',
                'plasma-pa',
                'bluedevil',
                'powerdevil',
                'kde-gtk-config',
                'sddm',
                'dolphin',
                'konsole',
                'kate',
                'kwrite',
                'ark',
                'gwenview',
                'spectacle',
                'okular',
                'firefox',
                'vlc',
                'kdegraphics-thumbnailers',
                'ffmpegthumbs'
            ]
        }
        
    def setup_directories(self):
        """Создание необходимых директорий"""
        print("📁 Создание директорий...")
        self.repo_dir.mkdir(parents=True, exist_ok=True)
        
    def download_packages(self):
        """Скачивание всех пакетов в локальный репозиторий"""
        print("📦 Скачивание пакетов для офлайн-установки...")
        
        # Объединяем все пакеты
        all_packages = []
        for group in self.packages.values():
            all_packages.extend(group)
        
        # Удаляем дубликаты
        all_packages = list(set(all_packages))
        
        print(f"Всего пакетов: {len(all_packages)}")
        print(f"Примерный размер: {len(all_packages) * 5} MB")
        
        # Создаем временную базу данных pacman
        db_path = Path('/tmp/sosaltix-db')
        db_path.mkdir(exist_ok=True)
        
        # Скачиваем пакеты
        cmd = f"sudo pacman -Syw --cachedir {self.repo_dir} --dbpath {db_path} {' '.join(all_packages)}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ Ошибка при скачивании пакетов:")
            print(result.stderr)
            sys.exit(1)
            
        # Создаем базу данных репозитория
        print("🗄️ Создание базы данных репозитория...")
        os.chdir(self.repo_dir)
        subprocess.run(f"repo-add ./sosaltix.db.tar.gz *.pkg.tar.zst", 
                      shell=True, check=True)
        
        # Считаем размер
        total_size = sum(f.stat().st_size for f in self.repo_dir.glob('*.pkg.tar.zst'))
        print(f"✅ Репозиторий создан: {total_size / 1024**3:.2f} GB")
        
    def create_package_list(self):
        """Создание файла со списком пакетов для установщика"""
        list_path = self.build_dir / 'sosaltix-profile' / 'airootfs' / 'root' / 'packages.json'
        
        import json
        with open(list_path, 'w') as f:
            json.dump(self.packages, f, indent=2)
            
        print(f"📋 Список пакетов сохранен: {list_path}")
        
    def run(self):
        """Запуск процесса"""
        print("🚀 Подготовка офлайн-репозитория SoSaltix")
        self.setup_directories()
        self.download_packages()
        self.create_package_list()
        print("✨ Готово! Репозиторий подготовлен.")

if __name__ == "__main__":
    builder = OfflineRepoBuilder()
    builder.run()