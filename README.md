# Auth and Access Control API

Backend-приложение с собственной системой аутентификации и авторизации.

## Реализовано

- регистрация пользователя;
- login по email и паролю;
- logout через JWT blacklist;
- soft delete пользователя;
- JWT Bearer authentication;
- ролевая модель доступа;
- разграничение прав по системным модулям;
- права на собственные объекты и на все объекты;
- API для назначения роли пользователю;
- API для просмотра и изменения правил доступа;
- mock-модуль `products` для демонстрации авторизации.

---

## Стек

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy Async
- Alembic
- Pydantic
- python-jose
- passlib / bcrypt

---

## Запуск

### 1. Клонировать репозиторий

```bash
git clone <repository_url>
cd test_task_Effective_Mobile
```

### 2. Создать и активировать виртуальное окружение

```bash
python -m venv .venv
```

Windows PowerShell:

```bash
.\.venv\Scripts\activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Создать `.env`

В корне проекта создать `.env` по примеру `.env.example`.

### 5. Применить миграции

```bash
alembic upgrade head
```

### 6. Заполнить тестовые данные

```bash
python -m src.seed
```

### 7. Запустить приложение

```bash
uvicorn src.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## Тестовые пользователи

```text
admin@example.com / admin123
seller@example.com / seller123
buyer@example.com / buyer123
```

---

## Переменные окружения

`.env.example` используется как шаблон.

---

## Аутентификация

Используется JWT access token.

После успешного login возвращается:

```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

Для защищённых endpoints используется заголовок:

```text
Authorization: Bearer <access_token>
```
В Swagger токен указывается через кнопку **Authorize** в правом верхнем углу страницы.

Порядок действий:

1. Выполнить `POST /auth/login`.
2. Скопировать значение `access_token` из ответа.
3. Нажать **Authorize**.
4. Вставить токен в поле авторизации.
5. Подтвердить авторизацию.

После этого Swagger будет автоматически отправлять токен в заголовке:

```text
Authorization: Bearer <access_token>
```

Если токен не передан, защищённые endpoints вернут `401 Unauthorized`.

JWT payload содержит:

```text
sub — user id
exp — срок действия токена
jti — уникальный идентификатор токена
```

---

## Logout

Logout реализован через blacklist токенов.

При logout `jti` текущего токена сохраняется в таблицу `blacklisted_tokens`.

Токен, добавленный в blacklist, больше не принимается системой.

Поле expires_at хранит время истечения токена. После этого времени токен уже невалиден сам по себе, поэтому запись в 
blacklist можно удалить.

Автоматическая очистка истёкших записей blacklist в текущей версии не реализована. 
В production-решении её можно добавить через периодическую задачу, например cron, Celery Beat, APScheduler или отдельный 
scheduled job.

---

## Модель доступа

Система доступа построена на ролях и правилах доступа к системным модулям.

Основные таблицы:

```text
users
roles
user_roles
system_modules
role_permissions
```

---

## users

Пользователь приложения.

Основные поля:

```text
id
email
hashed_password
is_active
```

Soft delete реализован через:

```text
is_active = False
deleted_at = <datetime>
```

После деактивации пользователь остаётся в БД, но не может авторизоваться.

---

## roles

Роли пользователей.

Seed создаёт роли:

```text
admin
seller
buyer
```

---

## user_roles

Связь пользователя с ролью.

В проекте действует ограничение:

```text
один пользователь — одна роль
```

На уровне БД добавлен unique constraint на `user_id`.

---

## system_modules

Системные модули, к которым применяются правила доступа.

Seed создаёт модули:

```text
users
products
user_role_management
```

---

## role_permissions

Правила доступа роли к модулю.

Поля:

```text
role_id
module_id

read_own_permission
read_all_permission

create_permission

update_own_permission
update_all_permission

delete_own_permission
delete_all_permission
```

На уровне БД добавлен unique constraint на пару:

```text
role_id + module_id
```

---

## Own / All permissions

Права с суффиксом `_own_permission` применяются только к объектам, где пользователь является владельцем.

Права с суффиксом `_all_permission` применяются ко всем объектам модуля.

Для mock-товаров владелец определяется через поле:

```text
owner_id
```

---

## Роли

### admin

`users`:

```text
read_all
delete_all
```

`products`:

```text
read_all
create
update_all
delete_all
```

`user_role_management`:

```text
read_all
update_all
```

---

### seller

`users`:

```text
read_own
update_own
delete_own
```

`products`:

```text
read_all
create
update_own
delete_own
```

`user_role_management`:

```text
нет доступа
```

---

### buyer

`users`:

```text
read_own
update_own
delete_own
```

`products`:

```text
read_all
```

`user_role_management`:

```text
нет доступа
```

---

## API

### Auth

```text
POST /auth/register
POST /auth/login
POST /auth/logout
```

---

### Users

```text
GET    /users/me
PATCH  /users/me
DELETE /users/me

GET    /users/
DELETE /users/{user_id}
```

---

### Products

```text
GET    /products/
GET    /products/{product_id}
POST   /products/
PATCH  /products/{product_id}
DELETE /products/{product_id}
```

`products` реализован как mock resource без таблицы в БД.

---

### User role management

Назначение роли пользователю:

```text
PATCH /user-role-management/users/{user_id}/role
```

Пример:

```json
{
  "role_name": "seller"
}
```

---

### Access rules management

Получение правил доступа:

```text
GET /user-role-management/permissions
```

Изменение существующего правила доступа:

```text
PATCH /user-role-management/permissions
```

Пример:

```json
{
  "role_name": "seller",
  "module_code": "products",
  "update_all_permission": true
}
```

Правило ищется по паре:

```text
role_name + module_code
```

Создание новых правил доступа через API не реализовано. Начальные правила создаются через `seed.py`.

---

## Ограничение на изменение прав администратора

Запрещено изменять правило:

```text
admin + user_role_management
```

Это защищает администратора от потери доступа к управлению ролями и правилами доступа.

При попытке изменить это правило возвращается:

```text
400 Bad Request
```

---

## Mock products

Модуль `products` реализован без таблицы в БД.

Данные находятся в памяти приложения:

```python
mock_products = [
    {"id": 1, "name": "iPhone", "owner_id": 1},
    {"id": 2, "name": "Laptop", "owner_id": 2},
]
```

Изменения mock-данных сохраняются только в рамках текущего запуска приложения.

После перезапуска сервера данные возвращаются к начальному состоянию.

---

## Коды ошибок

### 401 Unauthorized

Возвращается, если пользователь не определён:

```text
нет токена
токен невалидный
токен истёк
токен находится в blacklist
пользователь не найден
пользователь неактивен
```

### 403 Forbidden

Возвращается, если пользователь определён, но действие запрещено правилами доступа.

Примеры:

```text
buyer пытается создать товар
seller пытается изменить чужой товар
buyer пытается получить список правил доступа
```

---

## Проверка сценариев

### Admin

```text
admin@example.com / admin123
```

Доступно:

```text
GET /users/
GET /user-role-management/permissions
PATCH /user-role-management/permissions
POST /products/
PATCH /products/{id}
DELETE /products/{id}
```

---

### Seller

```text
seller@example.com / seller123
```

Доступно:

```text
GET /products/
POST /products/
PATCH своего товара
DELETE своего товара
```

Недоступно:

```text
PATCH чужого товара
DELETE чужого товара
GET /user-role-management/permissions
```

---

### Buyer

```text
buyer@example.com / buyer123
```

Доступно:

```text
GET /products/
GET /users/me
PATCH /users/me
DELETE /users/me
```

Недоступно:

```text
POST /products/
PATCH /products/{id}
DELETE /products/{id}
GET /user-role-management/permissions
```

---

## Структура проекта

```text
src/
  core/
    config.py
    security.py

  db/
    base.py
    session.py

  models/
    users.py
    roles.py
    user_roles.py
    system_modules.py
    role_permissions.py
    blacklisted_tokens.py

  routers/
    auth.py
    users.py
    products.py
    user_role_management.py

  schemas/
    auth.py
    users.py
    products.py
    user_roles.py
    role_permissions.py

  services/
    auth_service.py
    users_service.py
    product_service.py
    permissions_service.py
    access_rules_service.py
    token_blacklist_service.py
    user_role_management_service.py

  mock/
    products_data.py

  seed.py
  main.py
```

---