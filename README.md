# Backend for VK-Education messenger

## Описание

Local:

- http://localhost:8080

Deploy:

- https://vkedu-fullstack-div2.ru

Redoc (могут быть расхождения, обязательно читать [API](#api)):

- https://vkedu-fullstack-div2.ru/api/schema/redoc/

Swagger (могут быть расхождения, обязательно читать [API](#api)):

- https://vkedu-fullstack-div2.ru/api/schema/swagger/

Ставим звездочку и внимательно читаем `README.md`

## Как поднять проект?

Создать файл `.env` в корне проекта, со следующим содержимым:

```
DJANGO_SECRET_KEY=my_django_secret_key

CENTRIFUGO_ALLOWED_ORIGINS=*
CENTRIFUGO_API_KEY=my_centrifugo_api_key
CENTRIFUGO_TOKEN_HMAC_SECRET_KEY=my_centrifugo_token_hmac_secret_key
```

Если хотите включить `Production Mode` и лимиты:

```
PRODUCTION=on
```

Установить `Docker` и `Docker Compose`:

- https://www.docker.com/

Выполнить команду в корне проекта:

- `docker-compose up --build`

Управление лимитами (на деплое они будут такими как в репозитории):

- Все лимиты хранятся в `application.settings.py` в `Constants`

## Подсказки

### Proxy (по желанию)

**На `gh-pages` должна идти версия с прямым запросом без Proxy**

Пример конфига для `Vite`:

```
import { isDev, isGHPagesBuild } from './utils/env'

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  base: '2024-2-VK-EDU-Frontend-I-Ivanov',
  server: {
    proxy: isGHPagesBuild
      ? {}
      : {
        '/api': {
          target: isDev
            ? 'http://localhost:8080/api'
            : 'https://vkedu-fullstack-div2.ru/api',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
    },
    watch: {
      usePolling: true,
    },
  },
  plugins: [react()],
});
```

Пример запроса:

```
import { isGHPagesBuild } from './utils/env'

const baseURL = isGHPagesBuild
  ? 'https://vkedu-fullstack-div2.ru/api/'
  : ''

const fetchURL = `${baseURL}api/register/`

const res = await fetch(fetchURL, {
  method: 'POST',
  body,
  headers,
});

const json = await res.json();
```

### Авторизация

**Время жизни `access` токена - 1 час**

**Время жизни `refresh` токена - 24 часa**

**После рефреша `access` и `refresh` токены протухают**

Для авторизации в поле `headers` нужно добавить:

```
'Authorization': `Bearer ${accessToken}`,
```

### Заголовки

Заголовки, которые вам понадобятся:

```
{
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${accessToken}`,
}
```

Если отправляется `FormData`, то заголовок `multipart/form-data` указывать не надо

### Отправка файлов

**Максимальный размер `body` реквеста - 10MB**

Пример отправки файлов в `PATCH` реквесте:

```
const body = new FormData();

body.append('avatar', avatar)
body.append('bio', 'Programmer in VK')

const headers = { 'Authorization': `Bearer ${accessToken}` };

const res = await fetch(`http://vkedu-fullstack-div2.ru/api/user/${id}/`, {
  method: 'PATCH',
  body,
  headers,
})

const json = await res.json();
```

### Centrifugo (по желанию)

Официальный сайт:

- https://centrifugal.dev/

Centrifugal Labs:

- https://github.com/centrifugal

Клиент для JavaScript:

- https://github.com/centrifugal/centrifuge-js

Local:

- [ws://localhost:8080/connection/websocket/](http://localhost:8080/connection/websocket/)

Deploy:

- [wss://vkedu-fullstack-div2.ru/connection/websocket/](https://vkedu-fullstack-div2.ru/connection/websocket/)

**Время жизни `centrifugo` токена - 1 час**

**Каналом для подписки является `ID` вашего юзера**

Пример коннекта к `centrifugo`:

```
import { Centrifuge } from  'centrifuge';

let centrifuge;
let subscription;

// connect (передаем id канала и слушатель)
const connect = (channel, callback) => {
  if (!centrifuge) {
    centrifuge = new Centrifuge('wss://vkedu-fullstack-div2.ru/connection/websocket/', {
      minReconnectDelay: 1000 * 60 * 50,
      getToken: (ctx) =>
        new Promise((resolve, reject)  =>
          fetch('https://vkedu-fullstack-div2.ru/api/centrifugo/connect/', {
            body: JSON.stringify(ctx),
            method: 'POST',
            headers: headers,
          })
          .then((res) => res.json())
          .then((data) => resolve(data.token))
          .catch((err) => reject(err))
        )
    });

    centrifuge.connect();
  }

  if (!subscription) {
    subscription = centrifuge.newSubscription(channel, {
      minResubscribeDelay: 1000 * 60 * 50,
      getToken: (ctx) =>
        new Promise((resolve, reject) =>
          fetch('https://vkedu-fullstack-div2.ru/api/centrifugo/subscribe/', {
            body: JSON.stringify(ctx),
            method: 'POST',
            headers: headers,
          })
          .then((res) => res.json())
          .then((data) => resolve(data.token))
          .catch((err) => reject(err))
        )
    });

    subscription.on('publication', callback);
    subscription.subscribe();
  }
}

// unconnect (отписываем все слушатели)
const unconnect = () => {
  subscription.removeAllListeners();
  subscription.unsubscribe();
  centrifuge.disconnect();
}
```

**Данные в канал публикует сервер после создания, изменения, удаления, прочтения сообщения**

Пример публикаций:

```
{
  event: "create" | "update" | "delete" | "read",
  message: {
    id: string,
    text: string | null,
    voice: string | null,
    chat: string,
    sender: {
      id: string,
      username: string,
      first_name: string,
      last_name: string,
      bio: string | null,
      avatar: string | null,
      last_online_at: string,
      is_online: boolean,
    },
    files: [
      {
        item: string,
      }
    ],
    was_read_by: [{
      id: string,
      username: string,
      first_name: string,
      last_name: string,
      bio: string | null,
      avatar: string | null,
      last_online_at: string,
      is_online: boolean,
    }]
    updated_at: string,
    created_at: string,
  },
}
```

```
{
  event: "read_all",
  message: {
    chat: string,
    user: string,
    messages: string[],
  }
}
```

## <a id="api">API</a>

### `POST /api/register/`

Описание:

- Регистрация пользователя (создание нового пользователя)

Пример запроса:

```
{
  username: string,
  password: string,
  first_name: string,
  last_name: string,
  bio: string | null,
  avatar: File | null,
}
```

### `POST /api/auth/`

Описание:

- Авторизация пользователя (пользователь должен быть зарегестрирован).
- Возвращает `access` и `refresh` токены

Пример запроса:

```
{
  username: string,
  password: string,
}
```

Пример ответа:

```
{
  access: string,
  refresh: string,
}
```

### `POST /api/auth/refresh/`

Описание:

- Обновление `access` токена пользователя

Пример запроса:

```
{
  refresh: string,
}
```

Пример ответа:

```
{
  refresh: string,
  access: string,
}
```

### `GET /api/user/{uuid}/`

Описание:

- Получение информации о юзере
- Требует аутентификации

**Чтобы получить информацию о текущем юзере - `GET /api/user/current/`**

Пример ответа:

```
{
  id: string,
  username: string,
  first_name: string,
  last_name: string,
  bio: string | null,
  avatar: string | null,
  last_online_at: string,
  is_online: boolean,
}
```

### `PATCH /api/user/{uuid}/`

Описание:

- Изменение данных юзера.
- Данные о себе может менять только сам юзер.
- Требует аутентификации.

Поле `id` - неизменяемое

Пример запроса:

```
{
  bio: string,
  avatar: File,
}
```

Примера ответа:

```
{
  id: string,
  username: string,
  first_name: string,
  last_name: string,
  bio: string | null,
  avatar: string | null,
  last_online_at: string,
  is_online: boolean,
}
```

### `HEAD /api/user/online/`

**Поля `last_online_at` и `is_online` обновляются с любым аутентифицированным запросом**

**Если пользователь не активен больше 5 минут, то `is_online` автоматически станет `false`**

Описание:

- Принужденно установит флаг `is_online` в `true` и обновит поле `last_online_at`.
- Данные о себе может установить только сам юзер.
- Требует аутентификации.

### `DELETE /api/user/{uuid}/`

Описание:

- Удаление пользователя.
- Данные о себе может удалить только сам юзер.
- Требует аутентификации.

### `GET /api/users/`

Описание:

- Получить список пользователей
- Требует аутентификации.

Пример `GET` параметров:

- `search` - поиск по `username`, `last_name`, `first_name`
- `page_size` - количество пользователей в ответе (пагинация)
- `page` - текущая страница пагинации

Пример ответа:

```
{
  count: number,
  next: string,
  previous: string,
  results: [
    {
      id: string,
      username: string,
      first_name: string,
      last_name: string,
      bio: string | null,
      avatar: string | null,
      last_online_at: string,
      is_online: boolean,
    }
  ]
}
```

### `POST /api/chats/`

Описание:

- Создание чата.
- Требует аутентификации

Пример `GET` параметров:

- `fallback` - флаг, если установлен в значение `on`, то при попытке создания существующего приватного чата вернет существующий, а не выкинет исключение

Пример запроса:

```
{
  members: string[],
  is_private: boolean,
  title: string | null,
  avatar: File | null:
}
```

Пример ответа:

```
{
  id: string,
  title: string,
  members: [
    {
      id: string,
      username: string,
      first_name: string,
      last_name: string,
      bio: string | null,
      avatar: string | null,
      last_online_at: string,
      is_online: boolean,
    }
  ],
  creator: {
    id: string,
    username: string,
    first_name: string,
    last_name: string,
    bio: string | null,
    avatar: string | null,
    last_online_at: string,
    is_online: boolean,
  },
  avatar: string | null,
  created_at: string,
  updated_at: string,
  is_private: boolean,
  last_message: object | null,
  unread_messages_count: number,
}
```

### `GET /api/chats/`

Описание:

- Получение списка чатов
- Требует аутентицикации
- Возвращает только чаты пользователя

Пример `GET` параметров:

- `search` - поиск по `title`
- `page_size` - количество чатов в ответе (пагинация)
- `page` - текущая страница пагинации

Пример ответа:

```
{
  count: number,
  next: string,
  previous: string,
  results: [
    {
      id: string,
      title: string,
      members: [
        {
          id: string,
          username: string,
          first_name: string,
          last_name: string,
          bio: string | null,
          avatar: string | null,
          last_online_at: string,
          is_online: boolean,
        }
      ],
      creator: {
        id: string,
        username: string,
        first_name: string,
        last_name: string,
        bio: string | null,
        avatar: string | null,
        last_online_at: string,
        is_online: boolean,
      },
      avatar: string | null,
      created_at: string,
      updated_at: string,
      is_private: boolean,
      last_message: object | null,
      unread_messages_count: number,
    }
  ]
}
```

### `GET /api/chat/{uuid}/`

Описание:

- Получить информацию о чате
- Требует аутентификации
- Чтобы получить информацию о чате, нужно быть его участником

Пример ответа:

```
{
  id: string,
  title: string,
  members: [
    {
      id: string,
      username: string,
      first_name: string,
      last_name: string,
      bio: string | null,
      avatar: string | null,
      last_online_at: string,
      is_online: boolean,
    }
  ],
  creator: {
    id: string,
    username: string,
    first_name: string,
    last_name: string,
    bio: string | null,
    avatar: string | null,
    last_online_at: string,
    is_online: boolean,
  },
  avatar: string | null,
  created_at: string,
  updated_at: string,
  is_private: boolean,
  last_message: object | null,
  unread_messages_count: number,
}
```

### `PATCH /api/chat/{uuid}/`

Описание:

- Изменить данные чата
- Требует аутентификации
- ЛС чаты невозможно изменить
- Для изменения нужно быть создателем чата

Пример запроса:

```
{
  title: string | null,
  members: string[],
}
```

Пример ответа:

```
{
  id: string,
  title: string,
  members: [
    {
      id: string,
      username: string,
      first_name: string,
      last_name: string,
      bio: string | null,
      avatar: string | null,
      last_online_at: string,
      is_online: boolean,
    }
  ],
  creator: {
    id: string,
    username: string,
    first_name: string,
    last_name: string,
    bio: string | null,
    avatar: string | null,
    last_online_at: string,
    is_online: boolean,
  },
  avatar: string | null,
  created_at: string,
  updated_at: string,
  is_private: boolean,
  last_message: object | null,
  unread_messages_count: number,
}
```

### `POST /api/chat/{uuid}/leave/`

Описание:

- Покинуть чат
- Требует аутентификации
- Нужно быть участником чата
- Только для групповых чатов

### `DELETE /api/chat/{uuid}/`

Описание:

- Удаление чата
- Требует аутентификации
- Для удаления группового чата нужно быть создателем

### `POST /api/messages/`

Описание:

- Создание сообщения
- Требует аутентификации
- Нужно быть участником чата, в который добавляется сообщение

Пример запроса:

```
{
  chat: string,
  voice: File | null,
  text: string | null,
  files: File[] | null,
}
```

Пример ответа:

```
{
  id: string,
  text: string | null,
  voice: string | null,
  chat: string,
  files: [
    {
      item: string,
    }
  ],
  updated_at: string,
  created_at: string,
}
```

### `GET /api/messages/`

Описание:

- Получение списка сообщений
- Требует аутентификации
- Получить список сообщений чата может только его участник

Пример `GET` параметров

- `chat` - `uuid` чата
- `search` - поиск по `text`, `sender_username`, `sender_first_name`, `sender_last_name`
- `page_size` - количество сообщений в ответе (пагинация)
- `page` - текущая страница пагинации

Пример ответа:

```
{
  count: number,
  next: string,
  previous: string,
  results: [
    {
      id: string,
      text: string | null,
      voice: string | null,
      chat: string,
      sender: {
        id: string,
        username: string,
        first_name: string,
        last_name: string,
        bio: string | null,
        avatar: string | null,
        last_online_at: string,
        is_online: boolean,
      },
      files: [
        {
          item: string,
        }
      ],
      was_read_by: [{
        id: string,
        username: string,
        first_name: string,
        last_name: string,
        bio: string | null,
        avatar: string | null,
        last_online_at: string,
        is_online: boolean,
      }]
      updated_at: string,
      created_at: string,
    }
  ]
}
```

### `GET /api/message/{uuid}/`

Описание:

- получение информации о сообщении
- требует аутентификации
- нужно быть участником чата, в котором это сообщение

Пример ответа:

```
{
  id: string,
  text: string | null,
  voice: string | null,
  chat: string,
  sender: {
    id: string,
    username: string,
    first_name: string,
    last_name: string,
    bio: string | null,
    avatar: string | null,
    last_online_at: string,
    is_online: boolean,
  },
  files: [
    {
      item: string,
    }
  ],
  was_read_by: [{
    id: string,
    username: string,
    first_name: string,
    last_name: string,
    bio: string | null,
    avatar: string | null,
    last_online_at: string,
    is_online: boolean,
  }]
  updated_at: string,
  created_at: string,
}
```

### `PATCH /api/message/{uuid}/`

Описание:

- Обновление сообщения
- Требует аутентификации
- Для изменения нужно быть создателем сообщения
- Изменить можно только текст сообщения

Пример запроса:

```
{
  text: string,
}
```

Пример ответа:

```
{
  id: string,
  text: string | null,
  voice: string | null,
  chat: string,
  sender: {
    id: string,
    username: string,
    first_name: string,
    last_name: string,
    bio: string | null,
    avatar: string | null,
    last_online_at: string,
    is_online: boolean,
  },
  files: [
    {
      item: string,
    }
  ],
  was_read_by: [{
    id: string,
    username: string,
    first_name: string,
    last_name: string,
    bio: string | null,
    avatar: string | null,
    last_online_at: string,
    is_online: boolean,
  }]
  updated_at: string,
  created_at: string,
}
```

### `DELETE /api/message/{uuid}/`

Описание:

- Удаление сообщения
- Требует аутентификации
- Для удаления нужно быть создателем сообщения

### `POST /api/message/{uuid}/read/`

Описание:

- Добавляет текущего юзера в список тех, кто прочитал сообщение (`was_read_by`)
- Требует аутентификации
- Для прочтения нужно быть участником чата и не быть создателем сообщения

Пример ответа:

```
{
  id: string,
  text: string | null,
  voice: string | null,
  chat: string,
  sender: {
    id: string,
    username: string,
    first_name: string,
    last_name: string,
    bio: string | null,
    avatar: string | null,
    last_online_at: string,
    is_online: boolean,
  },
  files: [
    {
      item: string,
    }
  ],
  was_read_by: [{
    id: string,
    username: string,
    first_name: string,
    last_name: string,
    bio: string | null,
    avatar: string | null,
    last_online_at: string,
    is_online: boolean,
  }]
  updated_at: string,
  created_at: string,
}
```

### `POST /api/messages/read_all/`

Описание:

- Устанавливает все непрочитанные сообщения юзера в чате, как прочитанные (`was_read_by`)
- Требует аутентификации
- Для прочтения нужно быть участником чата и не быть создателем сообщения

Пример `GET` параметров:

- `chat` - `uuid` чата

### `POST /api/centrifugo/connect/`

Описание:

- Получение токена для подключения к `centrifugo`
- Требуется аутентификация

Пример ответа:

```
{
  token: string,
}
```

### `POST /api/centrifugo/subscribe/`

Описание:

- Получение токена для подписки на канал `centrifugo`
- Требуется аутентификация

Пример ответа:

```
{
  token: string,
}
```
