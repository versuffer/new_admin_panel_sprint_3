FROM python:3.11

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip  \
    && pip install "poetry==1.6.1"  \
    && poetry config virtualenvs.create false

COPY ["poetry.lock", "pyproject.toml", ".env", "./"]

RUN poetry install --no-root --no-interaction --without dev

WORKDIR ./etl

COPY etl .

ENTRYPOINT python main.py