# 09. Модулі (import/export)

## ES6 Modules

### Експорт
```js
// utils.js
export const PI = 3.14;

export function sum(a, b) {
  return a + b;
}

export default function multiply(a, b) {
  return a * b;
}
```

### Імпорт
```js
// main.js
import multiply, { PI, sum } from './utils.js';

console.log(PI);
console.log(sum(2, 3));
console.log(multiply(4, 5));
```

## Важливі правила

- Кожен файл — окремий модуль
- `type="module"` у `<script>` в HTML
- Шляхи повинні бути відносними (`./`, `../`)
- `default` експорт може бути тільки один

---

## Практика

1. Створи модуль `math.js` з математичними функціями.
2. Створи модуль `dom.js` з допоміжними функціями для DOM.
3. Організуй маленький проєкт з кількома модулями.

**Підсумок модуля 1:**  
Тепер ти знаєш основи JS + DOM + асинхронність + модулі.

Готовий перейти до **Модуля 2 — Frontend Верстка** (HTML + CSS + Tailwind)?

Напиши, і я відразу створу файли.
