# 07. REST API принципи

## Основні принципи REST

- **Stateless** — кожен запит містить всю інформацію
- **Resource-based** — працюємо з ресурсами (users, posts)
- **HTTP методи**:
  - GET — отримати
  - POST — створити
  - PUT — оновити повністю
  - PATCH — часткове оновлення
  - DELETE — видалити

## Приклад структури

```
GET    /api/users
GET    /api/users/:id
POST   /api/users
PUT    /api/users/:id
DELETE /api/users/:id
```

**Добрі практики:**
- Використовуй іменники (не дієслова)
- Версіонування (`/api/v1/users`)
- Правильні статус-коди (200, 201, 400, 404, 500)

**Далі →** [08-error-handling.md](./08-error-handling.md)
