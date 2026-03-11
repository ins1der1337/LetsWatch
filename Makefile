DOCKER_COMPOSE := docker compose
SERVICE_NAME := backend

EXEC_PYTHON := $(DOCKER_COMPOSE) exec $(SERVICE_NAME) python

.PHONY: help up down build logs shell prune

# Отображение справки
help:
	@echo "Доступные команды:"
	@echo "  make up          - Запустить контейнеры в фоновом режиме"
	@echo "  make down        - Остановить и удалить контейнеры"
	@echo "  make build       - Пересобрать образы"
	@echo "  make rebuild     - Пересобрать образы и запустить контейнер"
	@echo "  make logs        - Показать логи контейнеров
	@echo "  make shell       - Войти в оболочку контейнера (bash)"
	@echo "  make prune       - Очищает ненужные контейнеры"

# Запуск контейнеров
up:
	$(DOCKER_COMPOSE) up -d

# Остановка контейнеров
down:
	$(DOCKER_COMPOSE) down

# Пересборка образов (полезно после изменения Dockerfile или requirements.txt)
build:
	$(DOCKER_COMPOSE) build --no-cache

# Пересборка и запуск контейнеров
rebuild:
	$(DOCKER_COMPOSE) up -d --build

# Просмотр логов
logs:
	$(DOCKER_COMPOSE) logs $(SERVICE_NAME) -f

# Вход в контейнер
shell:
	$(DOCKER_COMPOSE) exec $(SERVICE_NAME) bash

# Очистка неиспользуемых образов, контейнеров и сетей
prune:
	docker system prune -f
