# 01. Підключення Frontend (React) до Backend

## Налаштування Proxy (Vite)

У `vite.config.js`:

```js
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      }
    }
  }
})
```

## Використання в компонентах

```js
const response = await fetch('/api/posts'); // замість http://localhost:5000/api/posts
```

**Важливо:** Налаштуй CORS на бекенді правильно.

**Далі →** [02-frontend-auth.md](./02-frontend-auth.md)
