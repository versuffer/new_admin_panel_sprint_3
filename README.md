# Инструкция по запуску ETL

ETL запускается с помощью ```Docker Compose```. 

1) Перед запуском необходимо создать в корневой директории проекта файл ```.env``` и скопировать в него содержимое файла ```.env.example```. 


Это позволит ```Docker Compose``` использовать переменные окружения при создании сервисов;


2) Далее необходимо выполнить следующую команду:

```bash
docker compose up -d --build
```

Эта команда создаст три сервиса (контейнера): ```postgres_database```, ```elasticsearch``` и ```etl```.

Сервис ```postgres_database``` при первом запуске (при создании тома) запустит скрипт для загрузки дампа БД (лежит в папке ```dumps```).

При повторном запуске скрипт будет проигнорирован.

3) Для того, чтобы посмотреть логи ETL, необходимо выполнить следующую команду:

```bash
docker compose logs -f etl
```

4) Чтобы полностью удалить все сервисы вместе томами, необходимо выполнить следующую команду:

```bash
docker compose down -v
```