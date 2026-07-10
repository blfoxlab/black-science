# 11. SQL Основи (PostgreSQL)

## Основні команди

```sql
-- Створення таблиці
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Вставка даних
INSERT INTO users (name, email) VALUES ('Оля', 'olya@example.com');

-- Вибірка
SELECT * FROM users;
SELECT name, email FROM users WHERE age > 18 ORDER BY name;

-- Оновлення
UPDATE users SET name = 'Олександр' WHERE id = 1;

-- Видалення
DELETE FROM users WHERE id = 5;
```

## JOIN-и, Foreign Key — обов’язково вивчити пізніше.

**Інструменти:** 
- pgAdmin
- DBeaver
- TablePlus

**Далі →** [12-prisma.md](./12-prisma.md)
