# 08. Routing (React Router v6+)

## Встановлення
```bash
npm install react-router-dom
```

## Основне використання

```jsx
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Головна</Link>
        <Link to="/about">Про нас</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/users/:id" element={<User />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
```

## Хуки Router
- `useParams()`
- `useNavigate()`
- `useLocation()`

**Практика:** Багатосторінковий сайт (Головна, Каталог, Профіль, 404).

**Далі →** [09-react-hook-form.md](./09-react-hook-form.md)
