FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Copy только файлы зависимостей для кэширования
COPY pyproject.toml uv.lock ./

# Кэшируем установку зависимостей
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

COPY . .

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
