#!/bin/bash

# Скрипт для загрузки ключей Yandex Cloud из публичного хранилища

echo "Загрузка ключей Yandex Cloud..."
wget -q https://storage.yandexcloud.net/ycpub/maikeys/.env -O .env.yandex

if [ $? -eq 0 ]; then
    echo "Ключи успешно загружены в .env.yandex"
    echo ""
    echo "Содержимое файла:"
    cat .env.yandex
    echo ""
    echo "Для использования добавьте эти переменные в ваш .env файл:"
    echo "  AI_PROVIDER=yandex"
    echo "  YANDEX_API_KEY=<значение из api_key>"
    echo "  YANDEX_FOLDER_ID=<значение из folder_id>"
    echo "  YANDEX_MODEL=gemma-3-12b-it/latest"
else
    echo "Ошибка при загрузке ключей"
    exit 1
fi

