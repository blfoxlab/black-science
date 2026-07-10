# 01. Робота з формами в React

## Контрольовані компоненти

```jsx
import { useState } from 'react';

function Form() {
  const [value, setValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Відправлено:', value);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Введіть текст"
      />
      <button type="submit">Надіслати</button>
    </form>
  );
}
```

## Бібліотеки
- **React Hook Form** (рекомендовано)
- Formik + Yup

---

**Практика:** Форма реєстрації з валідацією (email, пароль, підтвердження).

**Далі →** [02-localstorage.md](./02-localstorage.md)
