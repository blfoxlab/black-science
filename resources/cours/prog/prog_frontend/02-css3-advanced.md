# 02. CSS3 — Flexbox, Grid, Responsive, Анімації

## Flexbox

```css
.container {
  display: flex;
  justify-content: center;     /* головна вісь */
  align-items: center;         /* поперечна вісь */
  gap: 1rem;
  flex-wrap: wrap;
}
```

## CSS Grid

```css
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}
```

## Responsive Design

```css
/* Mobile First */
.container {
  padding: 1rem;
}

@media (min-width: 768px) {
  .container {
    padding: 2rem;
  }
}

@media (min-width: 1024px) { ... }
```

## Анімації та Transition

```css
button {
  transition: all 0.3s ease;
}

button:hover {
  transform: scale(1.05);
  box-shadow: 0 10px 15px rgba(0,0,0,0.1);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

---

**Практика:** Верстай компоненти (картка, навігація, hero-секція) з Flex/Grid.

**Далі →** [03-tailwind-css.md](./03-tailwind-css.md)
