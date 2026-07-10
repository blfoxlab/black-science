# 12. Prisma (ORM)

## Встановлення

```bash
npm install prisma --save-dev
npm install @prisma/client
npx prisma init
```

## schema.prisma

```prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        Int      @id @default(autoincrement())
  name      String
  email     String   @unique
  posts     Post[]
  createdAt DateTime @default(now())
}

model Post {
  id        Int      @id @default(autoincrement())
  title     String
  content   String?
  authorId  Int
  author    User     @relation(fields: [authorId], references: [id])
}
```

## Основні операції

```js
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();

// Create
const user = await prisma.user.create({ data: { name: "Іван", email: "ivan@test.com" } });

// Read
const users = await prisma.user.findMany({ include: { posts: true } });

// Update / Delete
```

**Далі →** [13-mongodb-overview.md](./13-mongodb-overview.md)
