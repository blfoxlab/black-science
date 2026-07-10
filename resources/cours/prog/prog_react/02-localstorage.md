# 02. LocalStorage та SessionStorage

## Основи

```js
// Збереження
localStorage.setItem('token', 'abc123');
localStorage.setItem('user', JSON.stringify({ name: 'Оля' }));

// Читання
const token = localStorage.getItem('token');
const user = JSON.parse(localStorage.getItem('user'));

// Видалення
localStorage.removeItem('token');
localStorage.clear();
```

## Хук для зручності

```jsx
import { useState, useEffect } from 'react';

function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    const saved = localStorage.getItem(key);
    return saved ? JSON.parse(saved) : initialValue;
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue];
}
```

**Практика:** Зберігай тему сайту та todo-лист у LocalStorage.

**Далі →** [03-fetch-api.md](./03-fetch-api.md)
