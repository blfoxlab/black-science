# 04. Основи Docker

## Dockerfile (приклад для Node.js)

```dockerfile
FROM node:20-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 5000
CMD ["node", "index.js"]
```

## docker-compose.yml (локально)

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
  backend:
    build: .
    ports:
      - "5000:5000"
    depends_on:
      - db
```

**Далі →** [05-cicd.md](./05-cicd.md)
