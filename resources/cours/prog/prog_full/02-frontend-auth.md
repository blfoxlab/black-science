# 02. Авторизація на фронтенді

## Варіанти зберігання токена

1. **localStorage** (просто, але вразливо до XSS)
2. **HttpOnly cookies** (безпечніше)

## Context + useAuth Hook

Створи `AuthContext` з `login`, `logout`, `user`.

```js
const [user, setUser] = useState(null);
const [token, setToken] = useState(localStorage.getItem('token'));

// Автоматичний logout при 401
```

**Рекомендація:** Використовуй `axios` з interceptor для автоматичного додавання токена в заголовки.

**Далі →** [03-deployment.md](./03-deployment.md)
