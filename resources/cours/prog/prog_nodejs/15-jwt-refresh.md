# 15. JWT + Refresh Tokens

## Встановлення
```bash
npm install jsonwebtoken bcryptjs
```

## Приклад

```js
// auth.js
import jwt from 'jsonwebtoken';

const generateToken = (userId) => {
  return jwt.sign({ userId }, process.env.JWT_SECRET, { expiresIn: '15m' });
};

const generateRefreshToken = (userId) => {
  return jwt.sign({ userId }, process.env.REFRESH_SECRET, { expiresIn: '7d' });
};
```

## Рефреш токенів (схема)
1. Клієнт логіниться → отримує `accessToken` + `refreshToken`
2. `accessToken` живе 15 хв
3. При закінченні — клієнт відправляє `refreshToken` на `/refresh`
4. Сервер видає нову пару токенів

**Далі →** [16-password-hashing.md](./16-password-hashing.md)
