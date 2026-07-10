# 05. CI/CD — Базові поняття

## Що таке CI/CD?

- **CI** (Continuous Integration) — автоматична перевірка коду
- **CD** (Continuous Deployment) — автоматичний деплой

## Популярні інструменти

- GitHub Actions (безкоштовно)
- Vercel / Railway мають вбудовані CI/CD

## Приклад GitHub Actions (простий)

```yaml
name: Deploy
on:
  push:
    branches: [ main ]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Railway
        uses: railwayapp/actions@v1
```

**Далі →** [06-final-project.md](./06-final-project.md)
