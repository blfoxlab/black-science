# 17. CORS, Helmet, Rate Limiting

## Helmet (захист заголовків)

```bash
npm install helmet
```

```js
import helmet from 'helmet';
app.use(helmet());
```

## CORS

```bash
npm install cors
```

```js
import cors from 'cors';
app.use(cors({
  origin: ['http://localhost:5173', 'https://yourdomain.com'],
  credentials: true
}));
```

## Rate Limiting (захист від DDoS)

```bash
npm install express-rate-limit
```

```js
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100
});

app.use('/api', limiter);
```

**Далі →** [18-auth-practice.md](./18-auth-practice.md)
