# 03. Вбудований HTTP-модуль

## Простий сервер

```js
import http from 'http';

const server = http.createServer((req, res) => {
  console.log(req.method, req.url);

  res.setHeader('Content-Type', 'application/json');

  if (req.url === '/api/hello') {
    res.end(JSON.stringify({ message: 'Привіт від Node.js!' }));
  } else if (req.url === '/api/users') {
    res.end(JSON.stringify([
      { id: 1, name: 'Анна' },
      { id: 2, name: 'Іван' }
    ]));
  } else {
    res.statusCode = 404;
    res.end(JSON.stringify({ error: 'Сторінку не знайдено' }));
  }
});

const PORT = 3000;
server.listen(PORT, () => {
  console.log(`Сервер працює на http://localhost:${PORT}`);
});
```

**Запуск:** `node app.js`

**Практика:** Створи сервер з 4–5 різними роутами.

---

**Частина 1 завершена!**  
Готовий продовжити **Частину 2 — Express.js**?
