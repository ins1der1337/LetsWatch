# LetsWatch - Backend

## Как запустить API?

Запускать backend необходимо из этой папки - `backend/`!!!  
Иначе импорты не будут работать правильно

Для запуска backend необходимо: [Docker](https://www.docker.com/products/docker-desktop/)

1. Запустить docker контейнеры с БД

    ```shell
    # Подгрузить образы 
    docker compose pull
    
    # Для запуска контейнеров в фоновом режиме
    docker compose up -d
    
    # Для остановки контейнеров (не забывайте закрывать)
    docker compose down
    ```

2. Установить зависимости

    ```shell
    # Для первого запуска создать venv
    python -m venv venv
    venv/Scripts/activate 
    
    # Установка зависимостей
    pip install -r requirements.txt
    ```

3. Апргейднуться до последней миграции БД

    ```shell
    alembic upgrade head
    ```

4. Запустить код

5. `python src.main.py`
