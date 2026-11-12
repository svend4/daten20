# 🛡️ Руководство по защите репозитория / Repository Protection Guide

Это руководство объясняет, как правильно настроить защиту GitHub репозитория.

This guide explains how to properly configure GitHub repository protection.

---

## 📋 Содержание / Table of Contents

1. [Branch Protection Rules](#branch-protection-rules)
2. [Security Settings](#security-settings)
3. [Access Control](#access-control)
4. [Secrets Management](#secrets-management)
5. [Dependency Management](#dependency-management)
6. [Monitoring and Alerts](#monitoring-and-alerts)

---

## 🔒 1. Branch Protection Rules

### Настройка защиты ветки main/master / Configure main/master Branch Protection

**Путь / Path:** `Settings → Branches → Add rule`

#### Обязательные настройки / Required Settings:

```yaml
Branch name pattern: main (или master)

✅ Require pull request reviews before merging
   - Required approving reviews: 1 (минимум)
   - Dismiss stale pull request approvals when new commits are pushed
   - Require review from Code Owners (если используете CODEOWNERS)

✅ Require status checks to pass before merging
   - Require branches to be up to date before merging
   Статусы для проверки / Status checks to require:
   - tests
   - security-scan
   - code-quality
   - codeql

✅ Require conversation resolution before merging
   (Все комментарии должны быть разрешены)

✅ Require signed commits (рекомендуется для критичных проектов)

✅ Require linear history (опционально, для чистой истории)

✅ Include administrators
   (Правила применяются даже к администраторам)

✅ Restrict who can push to matching branches
   (Только определённые пользователи/команды)

✅ Allow force pushes: OFF
   (Запретить force push для защиты истории)

✅ Allow deletions: OFF
   (Запретить удаление защищённой ветки)
```

### Зачем это нужно? / Why is this needed?

- **Код-ревью** - Предотвращает внесение необдуманных или вредоносных изменений
- **Статус-проверки** - Гарантирует, что код прошёл все тесты и проверки безопасности
- **Подписанные коммиты** - Подтверждает подлинность автора изменений
- **Запрет force push** - Защищает от потери истории и злонамеренных изменений

---

## 🔐 2. Security Settings

### Настройка функций безопасности / Configure Security Features

**Путь / Path:** `Settings → Security → Code security and analysis`

#### Включите следующее / Enable the following:

```yaml
✅ Dependency graph
   Автоматическое отслеживание зависимостей проекта

✅ Dependabot alerts
   Уведомления о уязвимостях в зависимостях
   
✅ Dependabot security updates
   Автоматические PR для исправления уязвимостей
   
✅ Dependabot version updates
   Настроено через .github/dependabot.yml

✅ Code scanning (CodeQL)
   Автоматический анализ кода на уязвимости
   Настроено через .github/workflows/codeql.yml
   
✅ Secret scanning
   Обнаружение случайно зафиксированных секретов
   (Автоматически включено для публичных репозиториев)
   
✅ Secret scanning push protection (для приватных репозиториев)
   Блокирует push'ы с обнаруженными секретами
```

### Настройка уведомлений / Configure Notifications

**Путь / Path:** `Settings → Notifications`

```yaml
✅ Email notifications for:
   - Security alerts
   - Dependabot alerts
   - Failed workflow runs
   - Pull request reviews

✅ Web notifications
   Проверяйте вкладку Notifications на GitHub
```

---

## 👥 3. Access Control / Контроль доступа

### Управление правами доступа / Manage Access Rights

**Путь / Path:** `Settings → Collaborators and teams`

#### Принципы / Principles:

1. **Least Privilege Principle** - Минимально необходимые права
2. **Role-Based Access** - Права на основе роли
3. **Regular Audit** - Регулярная проверка прав доступа

#### Роли GitHub / GitHub Roles:

| Role | Права / Permissions | Кому назначать / Assign to |
|------|---------------------|---------------------------|
| **Read** | Просмотр кода | Внешние пользователи, auditors |
| **Triage** | Read + управление issues | Community managers |
| **Write** | Triage + push код | Разработчики |
| **Maintain** | Write + manage settings | Team leads |
| **Admin** | Full access | Project owners только |

#### Рекомендации / Recommendations:

```yaml
✅ Используйте Teams для группового управления правами
✅ Регулярно проверяйте список collaborators
✅ Удаляйте неактивных пользователей
✅ Используйте CODEOWNERS для критичных файлов
✅ Включите two-factor authentication (2FA) для всех
```

### Two-Factor Authentication (2FA)

**Настоятельно рекомендуется / Strongly Recommended:**

```yaml
Для организаций / For organizations:
Settings → Security → Authentication security
✅ Require two-factor authentication for everyone in the organization

Для личных аккаунтов / For personal accounts:
Profile → Settings → Password and authentication
✅ Enable two-factor authentication
```

---

## 🔑 4. Secrets Management / Управление секретами

### GitHub Secrets

**Путь / Path:** `Settings → Secrets and variables → Actions`

#### Правила работы с секретами / Rules for Secrets:

```yaml
✅ НИКОГДА не коммитьте секреты в код / NEVER commit secrets to code
✅ Используйте GitHub Secrets для CI/CD
✅ Используйте .env файлы локально (в .gitignore)
✅ Используйте .env.example как шаблон
✅ Ротируйте секреты регулярно
✅ Используйте разные секреты для dev/staging/prod
```

#### Как добавить секрет / How to add a secret:

1. Go to `Settings → Secrets and variables → Actions`
2. Click "New repository secret"
3. Name: `MY_SECRET_NAME`
4. Value: your secret value
5. Click "Add secret"

#### Использование в workflows / Using in workflows:

```yaml
# .github/workflows/deploy.yml
steps:
  - name: Deploy
    env:
      API_KEY: ${{ secrets.API_KEY }}
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
    run: |
      ./deploy.sh
```

---

## 📦 5. Dependency Management / Управление зависимостями

### Dependabot Configuration

Файл `.github/dependabot.yml` уже настроен для:
- Python dependencies (requirements.txt)
- GitHub Actions
- Docker images

### Как обрабатывать Dependabot PR / How to handle Dependabot PRs:

```yaml
1. ✅ Проверьте changelog библиотеки
2. ✅ Убедитесь, что CI проходит
3. ✅ Проверьте security alerts (если есть)
4. ✅ Для major updates - проверьте breaking changes
5. ✅ Merge автоматически для patch/minor updates (если CI проходит)
6. ✅ Тестируйте major updates вручную
```

### Security Advisories

**Путь / Path:** `Security → Advisories`

```yaml
✅ Регулярно проверяйте security advisories
✅ Обновляйте зависимости с уязвимостями немедленно
✅ Используйте альтернативы для abandoned packages
```

---

## 📊 6. Monitoring and Alerts / Мониторинг и алерты

### Security Dashboard

**Путь / Path:** `Security → Overview`

Здесь вы увидите / Here you'll see:
- Open security alerts
- Dependabot alerts
- Code scanning alerts
- Secret scanning alerts

### Регулярные проверки / Regular Checks:

```yaml
✅ Еженедельно / Weekly:
   - Проверяйте Security dashboard
   - Проверяйте Dependabot PRs
   - Обновляйте критичные зависимости

✅ Ежемесячно / Monthly:
   - Audit права доступа
   - Проверяйте audit log
   - Обновляйте документацию безопасности
   - Проверяйте CODEOWNERS актуальность

✅ Ежеквартально / Quarterly:
   - Полный security audit
   - Penetration testing
   - Обновление security policy
   - Обучение команды
```

### GitHub Advanced Security (для Enterprise)

Если у вас GitHub Enterprise:

```yaml
✅ Code scanning (CodeQL) - включено
✅ Secret scanning - включено
✅ Dependency review - в PR проверках
✅ Security overview - dashboard для организации
```

---

## 🚀 Quick Start Checklist / Быстрая настройка

Используйте этот чеклист для быстрой настройки защиты репозитория:

### Базовая защита / Basic Protection (15 минут):

- [ ] Включить branch protection для main/master
- [ ] Require PR reviews (минимум 1)
- [ ] Включить Dependabot alerts
- [ ] Включить Dependabot security updates
- [ ] Настроить .gitignore (исключить .env, credentials)
- [ ] Добавить SECURITY.md

### Продвинутая защита / Advanced Protection (30 минут):

- [ ] Настроить CODEOWNERS
- [ ] Включить CodeQL scanning
- [ ] Настроить Dependabot version updates
- [ ] Включить required status checks
- [ ] Настроить issue templates
- [ ] Добавить PR template
- [ ] Включить signed commits
- [ ] Настроить security workflow

### Enterprise защита / Enterprise Protection (1+ час):

- [ ] Настроить SSO/SAML
- [ ] Включить audit logging
- [ ] Настроить IP allowlist
- [ ] Настроить organization security policy
- [ ] Penetration testing
- [ ] Security training для команды
- [ ] Incident response plan
- [ ] Regular security audits

---

## 🆘 Troubleshooting / Решение проблем

### Проблема: PR не может быть смержен из-за required checks

**Решение:**
1. Проверьте, что все required status checks прошли
2. Убедитесь, что ветка обновлена (merge/rebase с main)
3. Проверьте, нет ли failed workflows в Actions
4. Temporarily отключите specific checks (если необходимо) в Settings

### Проблема: Dependabot не создаёт PR

**Решение:**
1. Проверьте `.github/dependabot.yml` конфигурацию
2. Убедитесь, что достигнут лимит open-pull-requests-limit
3. Проверьте, что файл requirements.txt корректен
4. Проверьте Insights → Dependency graph

### Проблема: Secret scanning блокирует push

**Решение:**
1. Удалите секрет из кода
2. Используйте .env файл (добавьте в .gitignore)
3. Rotate секрет (сгенерируйте новый)
4. Если это false positive - можно dismiss alert

---

## 📞 Дополнительные ресурсы / Additional Resources

- [GitHub Security Best Practices](https://docs.github.com/en/code-security/getting-started/securing-your-repository)
- [Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [Secret Scanning](https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning)

---

**Последнее обновление / Last Updated:** 21 января 2026  
**Версия / Version:** 1.0  
**Автор / Author:** DMS Security Team
