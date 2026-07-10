# 07. DOM маніпуляції (базовий рівень)

## Що таке DOM?

**Document Object Model** — це об’єктна модель документа. Браузер перетворює HTML у дерево об’єктів JavaScript.

## Основні методи

```js
// Пошук елементів
document.getElementById('id')
document.querySelector('.class')     // CSS-селектор
document.querySelectorAll('li')      // повертає NodeList

// Зміна вмісту
element.textContent = "Новий текст"
element.innerHTML = "<strong>Жирний</strong>"

// Робота з класами
element.classList.add('active')
element.classList.remove('active')
element.classList.toggle('active')

// Атрибути
element.setAttribute('href', 'https://example.com')
element.getAttribute('src')
```

## Події

```js
button.addEventListener('click', () => {
  console.log('Кнопку натиснули!');
});

// Делегування подій (ефективніше)
document.body.addEventListener('click', (e) => {
  if (e.target.matches('.btn')) {
    // обробка
  }
});
```

---

## Практика

1. Створи список і кнопку "Додати елемент".
2. Реалізуй темну/світлу тему.
3. Створи модальне вікно (відкрити/закрити).

**Міні-проєкт:** Інтерактивна форма з валідацією в реальному часі.

**Далі →** [08-async-basics.md](./08-async-basics.md)
