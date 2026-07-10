# 05. Події та делегування подій (поглиблення)

## Основні події

- `click`, `dblclick`
- `input`, `change`
- `keydown`, `keyup`
- `scroll`, `resize`
- `load`, `DOMContentLoaded`

## Делегування подій (найкраща практика)

```js
// Погано — багато слухачів
// buttons.forEach(btn => btn.addEventListener(...))

// Добре — один слухач
document.getElementById('parent').addEventListener('click', (e) => {
  if (e.target.closest('.delete-btn')) {
    // видалити елемент
  }
});
```

**Переваги делегування:**
- Менше слухачів
- Працює з динамічно доданими елементами
- Краща продуктивність

---

**Міні-проєкт модуля:** Зверстати лендінг за Figma-макетом + зробити його інтерактивним (меню, модалки, форми).

Готовий до **React**?
