# 01. Робота з модулями в Node.js

## 1. CommonJS (require / module.exports)

```js
// utils.js
const add = (a, b) => a + b;
const PI = 3.14;

module.exports = { add, PI };
module.exports.multiply = (a, b) => a * b;
```

```js
// app.js
const utils = require('./utils');
console.log(utils.add(5, 3));
```

## 2. ES Modules (import / export) — Рекомендовано

Додай у `package.json`:
```json
{
  "type": "module"
}
```

```js
// utils.js
export const add = (a, b) => a + b;
export const PI = 3.14;

export default function greet(name) {
  return `Привіт, ${name}`;
}
```

```js
// app.js
import { add, PI } from './utils.js';
import greet from './utils.js';

console.log(add(2, 3));
console.log(greet("Олександр"));
```

**Практика:** Розділи свій код на кілька модулів (math, logger, config).

**Далі →** [02-file-system.md](./02-file-system.md)
