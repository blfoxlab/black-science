# 01. TypeScript (дуже рекомендовано)

## Основи

```ts
interface User {
  id: number;
  name: string;
  email?: string; // optional
}

const user: User = {
  id: 1,
  name: "Олександр"
};

function greet(name: string): string {
  return `Привіт, ${name}`;
}
```

## Ключові фічі
- Типи (`string`, `number`, `boolean`, `any`)
- Інтерфейси та типи
- Generics
- Utility types (`Partial`, `Omit`, `Pick`)

**Перехід з JS:** Почни з `any` → поступово типізуй.

**Далі →** [02-testing.md](./02-testing.md)
