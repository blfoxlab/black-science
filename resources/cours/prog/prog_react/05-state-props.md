# 05. State та Props

## Props (властивості)

```jsx
// Parent
<UserCard name="Анна" age={28} isActive={true} />

// Child
function UserCard({ name, age, isActive }) {
  return (
    <div>
      <h2>{name}</h2>
      <p>Вік: {age}</p>
    </div>
  );
}
```

## State

```jsx
const [count, setCount] = useState(0);

const increment = () => setCount(prev => prev + 1);
```

## Lifting State Up

Коли кілька компонентів потребують одного стану — піднімай його вище.

**Практика:** Todo List з додаванням, видаленням та позначкою виконаних.

**Далі →** [06-react-projects.md](./06-react-projects.md)
