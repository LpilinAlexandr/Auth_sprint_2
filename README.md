# Проектная работа 7 спринта

Проект делится на 2 части:

###1 часть. [Async API](https://github.com/LpilinAlexandr/Cinema)
###2 часть. [Сервис авторизации](https://github.com/LpilinAlexandr/Auth_sprint_2)

Проекты находятся в разных репозиториях. 
Не стал их объединять в один для упрощения работы над каждым в отдельности.

##Запуск проекта
Пропишите в терминале команду `sudo nano /etc/hosts`.
Добавьте туда следующие адреса:
```
127.0.0.1       auth.cinema.local
127.0.0.1       cinema.local
```
`auth.cinema.local` - это будет сервис авторизации
`cinema.local` - это будет Async API

Создайте файл `.env` в директории [auth](/auth). За основу возьмите [.env.sample](/auth/.env.sample)

Перейдите в директорию [auth](/auth) и запустите команду:

```
docker-compose up --build
```

Вам будут доступны:
1) [Auth API](http://auth.cinema.local/apidocs) - сервис авторизации
2) [Jaeger](http://127.0.0.1:16686/search) - трассировка запросов

Инструкция по запуску Async API находится внутри того проекта.
Для удачной интеграции после запуска Async API вы должны открывать его в браузере по адресу http://cinema.local

