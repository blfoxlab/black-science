# 10. Основи стану — Zustand (рекомендовано для початку)

## Встановлення
```bash
npm install zustand
```

## Приклад Store

```js
import { create } from 'zustand';

const useStore = create((set) => ({
  count: 0,
  user: null,

  increment: () => set((state) => ({ count: state.count + 1 })),
  setUser: (user) => set({ user }),

  fetchUser: async () => {
    const res = await fetch('/api/user');
    const user = await res.json();
    set({ user });
  }
}));
```

## Використання в компоненті

```jsx
function Counter() {
  const { count, increment } = useStore();
  return <button onClick={increment}>{count}</button>;
}
```

**Альтернатива:** Redux Toolkit (більш складний, але потужний).

**Підсумок:** Після цих тем ти вже можеш будувати серйозні React-додатки.

Готовий до **Backend**?
