# 16. Хешування паролів (bcrypt / argon2)

## bcrypt (популярний)

```js
import bcrypt from 'bcryptjs';

const saltRounds = 12;

// Хешування
const hashedPassword = await bcrypt.hash(password, saltRounds);

// Перевірка
const isMatch = await bcrypt.compare(enteredPassword, hashedPassword);
```

**Argon2** — більш сучасний і безпечний (рекомендується для нових проєктів).

**Правило:** Ніколи не зберігай паролі у відкритому вигляді!

**Далі →** [17-security-headers.md](./17-security-headers.md)
