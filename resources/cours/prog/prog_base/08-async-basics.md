# 08. Основи асинхронності

## setTimeout та setInterval

```js
setTimeout(() => {
  console.log("Виконалося через 2 секунди");
}, 2000);

const timer = setInterval(() => {
  console.log("Кожні 1 сек");
}, 1000);

clearInterval(timer); // зупинка
```

## Promises

```js
const promise = new Promise((resolve, reject) => {
  setTimeout(() => {
    const success = true;
    if (success) resolve("Дані отримані");
    else reject("Помилка");
  }, 1500);
});

promise
  .then(result => console.log(result))
  .catch(error => console.error(error))
  .finally(() => console.log("Завершено"));
```

## async / await (сучасний спосіб)

```js
async function fetchData() {
  try {
    const response = await fetch('https://api.example.com/data');
    const data = await response.json();
    console.log(data);
  } catch (error) {
    console.error("Помилка:", error);
  }
}
```

---

## Практика

1. Симуляція завантаження даних з затримкою.
2. Кнопка "Завантажити" → показати лоадер → вивести дані.
3. Паралельне завантаження кількох даних (`Promise.all`).

**Далі →** [09-modules.md](./09-modules.md)
