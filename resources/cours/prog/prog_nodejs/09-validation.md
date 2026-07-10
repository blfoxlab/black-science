# 09. Валідація (Zod — рекомендовано)

## Встановлення
```bash
npm install zod
```

## Приклад схеми

```js
import { z } from 'zod';

const userSchema = z.object({
  name: z.string().min(2, "Ім'я повинно бути не менше 2 символів"),
  email: z.string().email("Невірний формат email"),
  age: z.number().min(18, "Вік має бути від 18 років"),
  password: z.string().min(8)
});

// Використання
const result = userSchema.safeParse(req.body);

if (!result.success) {
  return res.status(400).json({ errors: result.error.errors });
}
```

**Альтернатива:** Joi

**Практика:** Створи повноцінний CRUD для користувачів з валідацією.

---

**Частина 2 завершена!**  
Готовий до **Частини 3 — Бази даних**?
