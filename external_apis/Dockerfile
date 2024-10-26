FROM python:3.10

WORKDIR /app

COPY . . 

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN uv sync --frozen 

# RUN uv run main.py

CMD ["uv", "run", "main.py"]