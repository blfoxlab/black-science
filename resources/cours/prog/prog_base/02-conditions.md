# 02. Умови (if/else, switch)

## if / else

```js
const age = 20;

if (age >= 18) {
  console.log("Повнолітній");
} else if (age >= 14) {
  console.log("Підліток");
} else {
  console.log("Дитина");
}
```

## Тернарний оператор

```js
const status = age >= 18 ? "Дорослий" : "Неповнолітній";
```

## Switch

```js
const day = "Monday";

switch (day) {
  case "Monday":
    console.log("Початок тижня");
    break;
  case "Friday":
    console.log("Кінець тижня!");
    break;
  default:
    console.log("Звичайний день");
}
```

---

## Практичні завдання

1. Напиши програму, яка визначає пору року за номером місяця.
2. Створи калькулятор (2 числа + операція).
3. Перевір пароль на складність (довжина + наявність цифр).

**Рекомендація:** Використовуй `prompt()` та `alert()` для простих тестів у браузері.

**Далі →** [03-loops.md](./03-loops.md)
