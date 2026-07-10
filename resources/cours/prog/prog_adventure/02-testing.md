# 02. Тестування

## Jest + React Testing Library

```bash
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
```

## Приклад

```tsx
import { render, screen } from '@testing-library/react';

test('renders todo', () => {
  render(<TodoItem text="Купити молоко" />);
  expect(screen.getByText('Купити молоко')).toBeInTheDocument();
});
```

**Корисно тестувати:**
- Рендеринг компонентів
- Кліки
- Форми

**Далі →** [03-algorithms.md](./03-algorithms.md)
