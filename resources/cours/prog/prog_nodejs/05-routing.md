# 05. Роутинг в Express

## Базовий роутинг

```js
app.get('/api/users', (req, res) => { ... });
app.post('/api/users', (req, res) => { ... });
app.put('/api/users/:id', (req, res) => { ... });
app.delete('/api/users/:id', (req, res) => { ... });
```

## Router (рекомендовано)

```js
// routes/users.js
import { Router } from 'express';
const router = Router();

router.get('/', getAllUsers);
router.post('/', createUser);
router.get('/:id', getUserById);

export default router;
```

```js
// index.js
import userRouter from './routes/users.js';
app.use('/api/users', userRouter);
```

**Далі →** [06-middleware.md](./06-middleware.md)
