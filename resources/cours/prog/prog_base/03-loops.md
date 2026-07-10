# 03. Цикли

## for

```js
for (let i = 0; i < 10; i++) {
  console.log(i);
}
```

## while / do-while

```js
let i = 0;
while (i < 5) {
  console.log(i);
  i++;
}
```

## for...of (для масивів)

```js
const fruits = ["яблуко", "банан", "вишня"];

for (const fruit of fruits) {
  console.log(fruit);
}
```

## for...in (для об’єктів)

```js
const person = { name: "Оля", age: 28 };

for (const key in person) {
  console.log(key, person[key]);
}
```

---

## Практика

1. Виведи всі парні числа від 1 до 50.
2. Порахуй суму чисел від 1 до 100.
3. Створи таблицю множення (5x5).

**Міні-проєкт:** Гра "Вгадай число" (комп'ютер загадує число від 1 до 100).

**Далі →** [04-functions.md](./04-functions.md)
