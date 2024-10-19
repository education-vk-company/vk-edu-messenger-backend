# Messenger Backend

Django Backend для курса Fullstack / 2

Django - http://localhost:8000

Centrifugo - http://localhost:9000

## Как поднять проект?

После клонирования репозитория вам нужно создать:

Файл .env в корне проекта, со следующим содержимым:

```
DJANGO_SECRET_KEY=my_django_secret_key

CENTRIFUGO_PORT=9000
CENTRIFUGO_TOKEN_HMAC_SECRET_KEY=my_centrifugo_token_hmac_secret_key
CENTRIFUGO_API_KEY=my_centrifugo_api_key
```

Файл config.json в корне проекта, со следующим содержимым:

```
{
  "port": "9000",
  "api_key": "my_centrifugo_api_key",
  "token_hmac_secret_key": "my_centrifugo_token_hmac_secret_key",
  "allowed_origins": ["*"]
}
```

### Вариант 1 (Docker)

1. Установите Docker и Docker Compose
   https://www.docker.com/

2. Выполните команду в корне проекта:
   `docker-compose up --build`

### Вариант 2 (Python + Centrifugo)

1. Установите Python (для разработки использовался Python 3.12)
   https://www.python.org/downloads/

2. Установите Centrifugo (если планируете использовать)
   https://centrifugal.dev/docs/getting-started/installation

3. Создайте виртуальное окружение:
   `python -m venv venv`

4. Активируйте виртуальное окружение:
   `source venv/bin/activate`

5. Установите зависимости:
   `pip install -r requirements.txt`

6. Создайте миграции:
   `python manage.py makemigrations`

7. Примините миграции:
   `python manage.py migrate`

8. Запустите django:
   `python manage.py runserver`

9. Запустите centrifugo (если выполнили пункт 2):
   Если вы добавили исполняемый файл в корень проекта, то это будет выглядеть примерно так:
   `./centrifugo --config=config.json`

## Подсказки

### Авторизация

Для авторизации в поле headers нужно добавить:

```
'Authorization': `Bearer ${accessToken}`,
```

### Заголовки

Заголовки, которые вам понадобятся:

```
{
  'Content-Type': 'application/json' или 'multipart/form-data',
  'Authorization': `Bearer ${accessToken}`,
}
```

### Отправка файлов

Пример отправки файлов в PATCH реквесте:

```
const  body  =  new  FormData();

body.append('avatar', avatar) // avatar - File
body.append('bio', 'Programmer in VK')

const  headers  = { 'Authorization': `Bearer ${accessToken}` };

const  res  =  await  fetch(`http://localhost:8000/api/user/${id}/`, {
  method: 'PATCH',
  body,
  headers,,
})

const  json  =  await res.json();
```

### Centrifugo

Официальный сайт: https://centrifugal.dev/

Клиент для js: https://github.com/centrifugal/centrifuge-js

**Каналом для подписки является ID вашего юзера**

Данные в канал публикует сервер после создания/изменения/удаления сообщения

Пример публикации:
```
{
  event: "create" | "update" | "delete",
  message: MessageResponse (смотреть GET /api/message/{uuid}/),
}
```

Пример коннекта к centrifugo:

```
import { Centrifuge } from  'centrifuge';

const  connect  =  ()  => {
  const  centrifuge  =  new  Centrifuge('ws://localhost:9000/connection/websocket', {
    getToken: (ctx)  =>
    new  Promise((resolve, reject)  =>
    fetch('http://localhost:8000/api/centrifugo/connect/', {
    body: JSON.stringify(ctx),
    method: 'POST',
    headers: headers,
  })
    .then((res)  => res.json())
    .then((data)  =>  resolve(data.token))
    .catch((err)  =>  reject(err))
    )
  });

  const  subscription  = centrifuge.newSubscription(id, {
    getToken: (ctx)  =>
    new  Promise((resolve, reject)  =>
    fetch('http://localhost:8000/api/centrifugo/subscribe/', {
    body: JSON.stringify(ctx),
    method: 'POST',
    headers: headers,
  })
    .then((res)  => res.json())
    .then((data)  =>  resolve(data.token))
    .catch((err)  =>  reject(err))
    )
  });

  subscription.on('publication', function(ctx) {
    console.log(ctx.data);
  });

  subscription.subscribe();
  centrifuge.connect();
}
```

## API

### POST /api/register/

Описание:

- Регистрация пользователя (создание нового пользователя)

Пример запроса:

```
{
  username: "username", // логин (обязательное поле, должно быть уникальным)
  password: "password", // пароль (обязательное поле)
  first_name: "Ivan", // имя (обязательное поле)
  last_name: "Ivanov", // фамилия (обязательное поле)
  bio: "some info about user", // информация о юзере,
  avatar: File // аватар пользователя (чтобы отправить нужно использовать FormData)
}
```

### POST /api/auth/

Описание:

- Авторизация пользователя (пользователь должен быть зарегестрирован).
- Возвращает access и refresh токены

Пример запроса:

```
{
  username: "username", // логин
  password: "password", // пароль
}
```

Пример ответа:

```
{
  access: "uhdwbhjcbwhbc...", // access токен
  refresh: "aknxklanklxakx...", // refresh токен
}
```

### POST /api/auth/refresh/

Описание:

- Обновление access токена пользователя

Пример запроса:

```
{
  refresh: "ajnxjanxjkajx..."
}
```

Пример ответа:

```
{
  refresh: "aklnxcajnxka...",
  access: "aklxnklanxkna...",
}
```

### GET /api/user/{uuid}/

Описание:

- Получение информации о юзере.
- Требует аутентификации

Пример ответа:

```
{
  id: "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  username: "username",
  first_name: "string",
  last_name: "string",
  bio: "string" | null,
  avatar: "string" | null,
}
```

### PATCH /api/user/{uuid}/

Описание:

- Изменение данных юзера.
- Данные о себе может менять только сам юзер.
- Требует аутентификации.

Поле id - неизменяемое

Пример запроса:

```
{
  bio: "new bio", // новое био
  avatar: File // новый аватар
}
```

Примера ответа:

- Совпадает с ответом GET /api/user/{uuid}/

### DELETE /api/user/{uuid}/

Описание:

- Удаление пользователя.
- Данные о себе может удалить только сам юзер.
- Требует аутентификации.

### GET /api/users/

Описание:

- Получить список пользователей
- Требует аутентификации.

Пример GET параметров:

- search - поиск по username, last_name, first_name
- page_size - количество пользователей в ответе (пагинация)
- page - текущая страница пагинации

Пример ответа:

```
{
  "count": 1,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "username": "string",
      "first_name": "string",
      "last_name": "string",
      "bio": "string" | null,
      "avatar": "string" | null
    }
  ]
}
```

### POST /api/chats/

Описание:

- Создание чата.
- Требует аутентификации

Пример запроса:

```
{
  "members": [
    // список uuid пользователей (обязательное поле)
    // если is_private - true, то максимальное число пользователей - 2
    // если is_private- false, то максимальное число пользователей неограничено
  ],
  "is_private": true/false // (обязательное поле) - лс или беседа
  "title": "string" // если is_private - true, то является обязательным полем
  "avatar": File // возможно установить аватар чата, если is_private - false
}
```

### GET /api/chats/

Описание:

- Получение списка чатов
- Требует аутентицикации
- Возвращает только чаты пользователя

Пример GET параметров:

- search - поиск по title (только для групповых чатов)
- page_size - количество чатов в ответе (пагинация)
- page - текущая страница пагинации

Пример ответа:

```
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "title": "string", // автоматически вернет ник собеседника для лс чата
      "members": [
        {
          "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
          "username": "string",
          "first_name": "string",
          "last_name": "string",
          "bio": "string",
          "avatar": "string"
        }
      ],
      "creator": {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "username": "string",
        "first_name": "string",
        "last_name": "string",
        "bio": "string",
        "avatar": "string"
      },
      "avatar": "string", // автоматически вернет аватар собеседника для лс чата
      "created_at": "2024-10-19T11:51:21.063Z",
      "updated_at": "2024-10-19T11:51:21.063Z",
      "is_private": true/false,
      "last_message": {...}
    }
  ]
}
```

### GET /api/chat/{uuid}/

Описание:

- Получить информацию о чате
- Требует аутентификации
- Чтобы получить информацию о чате, нужно быть его участником

Пример ответа:

```
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "string", // автоматически вернет ник собеседника для лс чата
  "members": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "username": "K@lFGbtBfE-9LwS@8q4Y8sHN8WCjNG2P+LIzK6aV9R",
      "first_name": "string",
      "last_name": "string",
      "bio": "string",
      "avatar": "string"
    }
  ],
  "creator": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "username": "string",
    "first_name": "string",
    "last_name": "string",
    "bio": "string" | null,
    "avatar": "string" | null
  },
  "avatar": "string", // автоматически вернет аватар собеседника для лс чата
  "created_at": "2024-10-19T11:57:41.719Z",
  "updated_at": "2024-10-19T11:57:41.719Z",
  "is_private": true,
  "last_message": {...}
}
```

### PATCH /api/chat/{uuid}/

Описание:

- Изменить данные чата
- Требует аутентификации
- ЛС чаты невозможно изменить
- Для изменения нужно быть создателем чата

Пример запроса:

```
{
  "title": "string",
  "members": [
    "3fa85f64-5717-4562-b3fc-2c963f66afa6" // новые пользователи (если нужно сохранить старых, то они также должны быть указаны в списке)
  ]
}
```

Пример ответа:

- Совпадает с GET /api/chat/{uuid}/

### DELETE /api/chat/{uuid}/

Описание:

- Удаление чата
- Требует аутентификации
- Для удаления нужно быть создателем чата

### POST /api/messages/

Описание:

- Создание сообщения
- Требует аутентификации
- Нужно быть участником чата, в который добавляется сообщение

Пример запроса:

```
{
  "text": "string",
  "voice": File //если передано поле voice, то запрос не может содержать полей text и files, так как данное поле является флагом, что сообщение - голосовое
  "chat": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "files": File[] // Максимальное число файлов - 5
}
```

Пример ответа:

```
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "text": "string",
  "voice": "string",
  "chat": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "files": [
    {
      "item": "string"
    }
  ],
  "updated_at": "2024-10-19T12:04:48.360Z",
  "created_at": "2024-10-19T12:04:48.360Z"
}
```

### GET /api/messages/

Описание:

- Получение списка сообщений
- Требует аутентификации
- Получить список сообщений чата может только его участник

Пример GET параметров

- chat - uuid чата
- search - поиск по text, sender_username, sender_first_name, sender_last_name
- page_size - количество сообщений в ответе (пагинация)
- page - текущая страница пагинации

Пример ответа:

```
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "text": "string" | null,
      "voice": "string" | null,
      "sender": {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "username": "string",
        "first_name": "string",
        "last_name": "string",
        "bio": "string" | null,
        "avatar": "string" | null
      },
      "chat": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "files": [
        {
          "item": "string"
        }
      ],
      "updated_at": "2024-10-19T12:09:31.147Z",
      "created_at": "2024-10-19T12:09:31.148Z"
    }
  ]
}
```

### GET /api/message/{uuid}/

Описание:

- получение информации о сообщении
- требует аутентификации
- нужно быть участником чата, в котором это сообщение

Пример ответа:

```
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "text": "string" | null,
  "voice": "string" | null,
  "sender": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "username": "kek",
    "first_name": "string",
    "last_name": "string",
    "bio": "string" | null,
    "avatar": "string" | null
  },
  "chat": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "files": [
    {
      "item": "string"
    }
  ],
  "updated_at": "2024-10-19T12:11:31.521Z",
  "created_at": "2024-10-19T12:11:31.521Z"
}
```

### PATCH /api/message/{uuid}/

Описание:

- Обновление сообщения
- Требует аутентификации
- Для изменения нужно быть создателем сообщения
- Изменить можно только текст сообщения

Пример запроса:

```
{
  "text": "string",
}
```

Пример ответа:

- Совпадает с GET /api/message/{uuid}/

### DELETE /api/message/{uuid}/

Описание:

- Удаление сообщения
- Требует аутентификации
- Для удаления нужно быть создателем сообщения

### POST /api/centrifugo/connect/

Описание:

- Получение токена для подключения к centrifugo
- Требуется аутентификация

Пример ответа:

```
{
  "token": "string"
}
```

### POST /api/centrifugo/subscribe/

Описание:

- Получение токена для подписки на канал centrifugo
- Требуется аутентификация

Пример ответа:

```
{
  "token": "string"
}
```
