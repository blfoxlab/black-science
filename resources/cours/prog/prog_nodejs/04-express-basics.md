# 04. Express.js — Основи

## Встановлення

```bash
npm init -y
npm install express
npm install --save-dev nodemon
```

Додай у `package.json`:
```json
"scripts": {
  "dev": "nodemon index.js"
}
```

**Простий сервер:**

```js
import express from 'express';

const app = express();
const PORT = 5000;

app.get('/', (req, res) => {
  res.send('Hello from Express!');
});

app.listen(PORT, () => {
  console.log(`Сервер запущено на http://localhost:${PORT}`);
});
```

**Далі →** [05-routing.md](./05-routing.md)
