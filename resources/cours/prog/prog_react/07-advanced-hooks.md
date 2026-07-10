# 07. useState, useEffect, useContext (поглиблення)

## useState

```jsx
const [state, setState] = useState(initialValue);

// Функціональне оновлення
setCount(prev => prev + 1);
```

## useEffect

```jsx
useEffect(() => {
  // side effects
  const subscription = ...;
  return () => subscription.unsubscribe(); // cleanup
}, [dependencies]);
```

- `[]` — тільки при монтуванні
- `[dep]` — при зміні залежності
- Без масиву — на кожному рендері

## useContext

```jsx
// Context.js
export const ThemeContext = createContext();

// Provider
<ThemeContext.Provider value={theme}>
  {children}
</ThemeContext.Provider>

// Consumer
const theme = useContext(ThemeContext);
```

**Практика:** Темна/світла тема через Context.

**Далі →** [08-react-router.md](./08-react-router.md)
