# 01. HTML5 — Семантика та доступність

## Семантичні теги

```html
<header>          <!-- шапка -->
<nav>             <!-- навігація -->
<main>            <!-- основний контент -->
<article>         <!-- стаття -->
<section>         <!-- секція -->
<aside>           <!-- сайдбар -->
<footer>          <!-- підвал -->
```

## Важливі атрибути доступності (a11y)

- `alt` у зображень
- `aria-label`, `aria-hidden`
- `role` (button, dialog тощо)
- `tabindex`
- Семантичні теги допомагають з доступністю автоматично

## Приклад хорошої структури

```html
<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Назва сайту</title>
</head>
<body>
  <header>...</header>
  <nav>...</nav>
  <main>
    <section>...</section>
  </main>
  <footer>...</footer>
</body>
</html>
```

---

**Завдання:** Переверстай будь-яку стару сторінку з `<div>` на семантичні теги.

**Далі →** [02-css3-advanced.md](./02-css3-advanced.md)
