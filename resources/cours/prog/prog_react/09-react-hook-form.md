# 09. Робота з формами — React Hook Form

## Встановлення
```bash
npm install react-hook-form
```

## Приклад

```jsx
import { useForm } from 'react-hook-form';

function MyForm() {
  const { register, handleSubmit, formState: { errors } } = useForm();

  const onSubmit = data => console.log(data);

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register("name", { required: true })} />
      {errors.name && <span>Поле обов’язкове</span>}

      <button type="submit">Надіслати</button>
    </form>
  );
}
```

**Переваги:**
- Мінімум коду
- Вбудована валідація
- Хороша продуктивність

**Далі →** [10-state-management.md](./10-state-management.md)
