# 03. Tailwind CSS (сучасний підхід)

## Встановлення (Vite + React рекомендується)

```bash
npm create vite@latest my-project -- --template react
cd my-project
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

## Основні класи

- **Layout**: `flex`, `grid`, `p-4`, `m-6`, `gap-4`
- **Типографіка**: `text-xl`, `font-bold`, `tracking-tight`
- **Кольори**: `bg-blue-600`, `text-white`, `hover:bg-blue-700`
- **Responsive**: `md:flex`, `lg:grid-cols-3`

**Приклад компонента:**

```html
<div class="max-w-sm mx-auto bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-2xl transition-all">
  <img src="..." class="w-full h-48 object-cover" alt="">
  <div class="p-6">
    <h3 class="text-2xl font-semibold mb-2">Назва</h3>
    <p class="text-gray-600">Опис...</p>
  </div>
</div>
```

**Переваги Tailwind:** швидкість, консистентність, відсутність "спагеті CSS".

**Далі →** [04-figma-basics.md](./04-figma-basics.md)
