# 04. Функції

## Function Declaration

```js
function sum(a, b) {
  return a + b;
}
```

## Function Expression

```js
const multiply = function(a, b) {
  return a * b;
};
```

## Arrow Function (сучасний стандарт)

```js
const divide = (a, b) => a / b;

// Багаторядкова
const greet = (name) => {
  return `Привіт, ${name}!`;
};
```

## Параметри за замовчуванням

```js
function greet(name = "Гість") {
  console.log(`Привіт, ${name}`);
}
```

## Rest та Spread

```js
function sumAll(...numbers) {
  return numbers.reduce((a, b) => a + b, 0);
}
```

---

## Практика

1. Напиши функцію для перевірки паролю.
2. Функція, яка повертає максимальне число з масиву.
3. Калькулятор з функціями.

**Далі →** [05-arrays-objects.md](./05-arrays-objects.md)
