# 04. Компоненти в React

## Функціональні компоненти

```jsx
function Button({ text, onClick }) {
  return <button onClick={onClick}>{text}</button>;
}
```

## Хуки

- `useState` — стан
- `useEffect` — побічні ефекти
- `useContext` — контекст
- `useRef` — посилання на DOM
- `useMemo`, `useCallback` — оптимізація

**Правила хуків:**
- Викликай тільки на верхньому рівні
- Не викликай в умовах, циклах, вкладених функціях

**Далі →** [05-state-props.md](./05-state-props.md)
