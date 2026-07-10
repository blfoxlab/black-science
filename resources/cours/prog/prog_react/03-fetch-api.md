# 03. Fetch API та робота з JSON

## Базовий приклад

```jsx
async function getUsers() {
  try {
    const response = await fetch('https://jsonplaceholder.typicode.com/users');
    const users = await response.json();
    console.log(users);
  } catch (error) {
    console.error('Помилка:', error);
  }
}
```

## З useEffect

```jsx
useEffect(() => {
  const loadData = async () => {
    const res = await fetch('/api/data');
    const data = await res.json();
    setData(data);
  };
  loadData();
}, []);
```

## POST-запит

```js
await fetch('/api/posts', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(newPost)
});
```

**Практика:** Підключи публічне API (JSONPlaceholder, FakeStoreAPI).

**Далі →** [04-react-components.md](./04-react-components.md)
