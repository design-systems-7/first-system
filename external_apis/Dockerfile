FROM python:3.10

WORKDIR /app

COPY . . 

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN uv sync --frozen 

CMD ["uv", "run", "--", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3629", "--workers", "4"]