# 06. Middleware в Express

## Що таке Middleware?

Функція, яка має доступ до `req`, `res` та `next()`.

## Приклади

```js
// Logging middleware
app.use((req, res, next) => {
  console.log(`${req.method} ${req.url}`);
  next();
});

// Парсинг JSON
app.use(express.json());

// Статичні файли
app.use(express.static('public'));
```

## Кастомний middleware

```js
const logger = (req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  next();
};

app.use(logger);
```

**Далі →** [07-rest-api.md](./07-rest-api.md)
