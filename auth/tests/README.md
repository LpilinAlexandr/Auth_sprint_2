# Tests

Отдельная среда на основе докер-образа `auth_api`

1. Перейдите в корень проекта `Auth` и введите команду:
``` 
docker build . -f Dockerfile -t auth_api
```
2. Запустите тесты командой:
``` 
docker-compose -f tests/functional/docker-compose.yml up --build
```

Для тестирования также поднимаются redis и postgres.
