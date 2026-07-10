# 05. WebSockets (Socket.io) — огляд

## Встановлення

```bash
npm install socket.io socket.io-client
```

## Базовий приклад

```js
// server
io.on('connection', (socket) => {
  socket.on('chat message', (msg) => {
    io.emit('chat message', msg);
  });
});
```

**Застосування:** Чати, онлайн-ігри, реал-тайм оновлення.

**Далі →** [06-graphql.md](./06-graphql.md)
