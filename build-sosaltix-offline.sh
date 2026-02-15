#!/bin/bash
# build-sosaltix-offline.sh

set -e

echo "🚀 Начало сборки SoSaltix Offline Edition"

# 1. Подготовка репозитория
echo "📦 Подготовка офлайн-репозитория..."
python3 prepare-offline-repo.py

# 2. Копирование установщика
echo "📋 Копирование установщика..."
cp offline_installer.py sosaltix-profile/airootfs/root/
cp packages.json sosaltix-profile/airootfs/root/

# 3. Настройка прав
chmod +x sosaltix-profile/airootfs/root/offline_installer.py

# 4. Сборка ISO
echo "🔨 Сборка ISO..."
sudo mkarchiso -v -w work -o out sosaltix-profile/

# 5. Результат
echo "✅ Готово!"
ls -lh out/*.iso