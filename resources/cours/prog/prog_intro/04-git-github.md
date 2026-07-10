# 04. Git та GitHub

## Основи Git

### Команди

```bash
git init                    # ініціалізувати репозиторій
git status                  # стан файлів
git add файл.txt            # додати файл
git add .                   # додати всі зміни
git commit -m "повідомлення" # коміт
git log                     # історія комітів
git branch                  # показати гілки
git checkout -b назва-гілки # створити і перейти
git merge гілка             # змерджити
```

### .gitignore
Створи файл `.gitignore` і додай туди:
```
node_modules/
.DS_Store
.env
dist/
```

---

## GitHub

1. Створи акаунт на [github.com](https://github.com)
2. Створи репозиторій `web-dev-learning`
3. Клонуй його:
   ```bash
   git clone https://github.com/твій-нік/web-dev-learning.git
   ```

### Основний workflow
```bash
git pull origin main
# робиш зміни
git add .
git commit -m "опис змін"
git push origin main
```

**Хороші повідомлення до комітів** — це важливо!

**Далі →** [05-final-task.md](./05-final-task.md)
