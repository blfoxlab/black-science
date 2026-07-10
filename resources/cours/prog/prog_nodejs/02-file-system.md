# 02. File System (fs)

## Асинхронна робота (рекомендовано)

```js
import fs from 'fs/promises';

async function main() {
  // Читання файлу
  const data = await fs.readFile('data.txt', 'utf-8');
  console.log(data);

  // Запис
  await fs.writeFile('log.txt', 'Новий запис\n', { flag: 'a' });

  // Створення папки
  await fs.mkdir('uploads', { recursive: true });
}

main().catch(console.error);
```

## Корисні методи
- `fs.readdir()` — список файлів
- `fs.stat()` — інформація про файл
- `fs.unlink()` — видалити файл
- `fs.rm()` — видалити папку

**Практика:**
1. Створи скрипт для логування подій у файл.
2. Напиши утиліту для копіювання файлів.

**Далі →** [03-http-module.md](./03-http-module.md)
