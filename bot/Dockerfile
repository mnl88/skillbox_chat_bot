# FROM — задаёт базовый (родительский) образ
FROM python:3.11.3-slim-buster
LABEL authors="Nikita_Matyushenkov"

# set environment variables
# Prevents Python from writing pyc files to disc (equivalent to python -B option)
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr (equivalent to python -u option)
ENV PYTHONUNBUFFERED 1

# RUN - выполняет команду и создаёт слой образа. Используется для установки в контейнер пакетов
# WORKDIR — задаёт рабочую директорию для следующей инструкции
RUN mkdir -p /usr/src/app
# (-p тут означает, что мы создаем все папки из заданного пути)

# set work directory
WORKDIR /usr/src/app
# копирует в контейнер файлы и папки (в данном случае точка означает, что из нашей активной директории)
COPY . /usr/src/app
COPY ./requirements.txt /usr/src/app/requirements.txt

EXPOSE 8080

ENV TZ Europe/Moscow

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


# описывает команду с аргументами, которую нужно выполнить когда контейнер будет запущен.
# Аргументы могут быть переопределены при запуске контейнера. В файле может присутствовать лишь одна инструкция CMD
#CMD ["python", "./bot/__main__.py"]
ENTRYPOINT ["python", "__main__.py"]