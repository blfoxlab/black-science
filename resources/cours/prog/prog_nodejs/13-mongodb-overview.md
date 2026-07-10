# 13. NoSQL — MongoDB (огляд)

## Основні відмінності від SQL

- Документо-орієнтована
- Гнучка схема (не потрібні міграції)
- Добре масштабується горизонтально

## Основні поняття

- **Database** → **Collection** → **Document** (JSON-like)

## Приклад з Mongoose (або Prisma + Mongo)

```js
const userSchema = new Schema({
  name: String,
  email: String,
  age: Number
});

const User = model('User', userSchema);
```

**Коли використовувати MongoDB:**
- Блоги, соцмережі
- Контент-менеджмент
- Прототипи

**Рекомендація:** Для початку добре володій PostgreSQL + Prisma.

---

**Частина 3 завершена!**

Хочеш продовжити **Частину 4 — Автентифікація**?
