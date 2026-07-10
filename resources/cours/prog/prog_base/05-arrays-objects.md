# 05. Масиви та об’єкти

## Масиви

```js
const numbers = [1, 2, 3, 4, 5];

// Основні методи
numbers.push(6);        // додати в кінець
numbers.pop();          // видалити з кінця
numbers.shift();        // видалити з початку
numbers.unshift(0);     // додати на початок

// Важливі методи
numbers.map(x => x * 2);
numbers.filter(x => x > 3);
numbers.find(x => x > 3);
numbers.forEach(x => console.log(x));
```

## Об’єкти

```js
const user = {
  name: "Іван",
  age: 30,
  isAdmin: false,
  address: {
    city: "Київ"
  }
};

// Доступ
console.log(user.name);
console.log(user["age"]);

// Деструктуризація
const { name, age, address: { city } } = user;
```

## Методи об’єктів

- `Object.keys()`, `Object.values()`, `Object.entries()`

---

## Практичні завдання

1. Створи масив студентів і виведи їхні імена.
2. Фільтруй масив за віком (> 18).
3. Створи об’єкт "Книга" з властивостями.

**Міні-проєкт:** Система управління контактами (додавання, видалення, пошук).

**Далі →** [06-practice.md](./06-practice.md)
