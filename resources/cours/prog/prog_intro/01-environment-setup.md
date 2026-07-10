# 01. Налаштування середовища

## 1. VS Code — основний редактор

### Встановлення
1. Завантаж з офіційного сайту: [code.visualstudio.com](https://code.visualstudio.com/)
2. Встанови

### Рекомендовані розширення (обов’язково встанови всі):

- **ESLint** — перевірка коду
- **Prettier - Code formatter** — автоматичне форматування
- **ES7+ React/Redux/React-Native snippets** — швидке створення компонентів
- **Tailwind CSS IntelliSense**
- **GitLens** — покращена робота з Git
- **Thunder Client** — для тестування API (замість Postman)
- **Live Server** — для запуску HTML файлів
- **Auto Rename Tag**
- **Material Icon Theme** (для красивих іконок)

### Налаштування VS Code
1. Відкрий **Settings** (`Ctrl + ,`)
2. Увімкни **Auto Save**: `"files.autoSave": "afterDelay"`
3. Встанови Prettier як форматер за замовчуванням
4. Додай в settings.json:
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "prettier.singleQuote": true,
  "prettier.semi": true,
  "prettier.tabWidth": 2
}
```

---

## 2. Node.js

Завантаж **LTS версію** з [nodejs.org](https://nodejs.org/)

Перевір встановлення в терміналі:
```bash
node --version
npm --version
```

---

## 3. Git

Завантаж з [git-scm.com](https://git-scm.com/downloads)

Після встановлення налаштуй:
```bash
git config --global user.name "Твоє Ім'я"
git config --global user.email "твоя-пошта@gmail.com"
git config --global core.editor "code --wait"
```

---

## 4. Браузер

**Google Chrome** — основний для розробки.

Встанови розширення:
- React Developer Tools
- Redux DevTools
- JSON Formatter
- Lighthouse
- ColorZilla

**Готово!** Перейди до наступного файлу → [02-terminal-basics.md](./02-terminal-basics.md)
