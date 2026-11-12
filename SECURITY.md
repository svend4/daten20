# Security Policy

## 🔒 Защита репозитория / Repository Security

Этот документ описывает политику безопасности проекта Document Management System (DMS) и предоставляет рекомендации по защите репозитория от различных угроз.

This document describes the security policy for the Document Management System (DMS) project and provides guidelines on protecting the repository from various threats.

---

## 📊 Текущее состояние безопасности / Current Security Status

### ✅ Реализованные меры безопасности / Implemented Security Measures

#### 1. **Автоматизированное сканирование безопасности / Automated Security Scanning**

- ✅ **Dependabot** - Автоматическое обновление зависимостей (еженедельно)
  - Python dependencies
  - GitHub Actions
  - Docker images
  
- ✅ **GitHub Security Workflow** (`.github/workflows/security.yml`)
  - Dependency scanning (Safety, pip-audit)
  - Code security scanning (Bandit, Semgrep)
  - Secret detection (Gitleaks)
  - License compliance checking
  - Runs on: push to main/develop, PRs, and weekly schedule

#### 2. **Защита кода / Code Security**

- ✅ **Static Analysis Security Testing (SAST)**
  - Bandit scanner - регулярное сканирование на уязвимости
  - Semgrep scanner - паттерны безопасности
  - Результаты: 90% уязвимостей устранено (см. `SESSION_TASK54_SECURITY_AUDIT_REPORT.md`)

- ✅ **Pre-commit Hooks** (`.pre-commit-config.yaml`)
  - Code formatting validation
  - Syntax checking
  - Security linting
  - Prevents committing insecure code

#### 3. **Безопасность приложения / Application Security**

- ✅ **Authentication & Authorization**
  - JWT-based authentication (`src/core/auth.py`)
  - Role-Based Access Control (RBAC)
  - API key authentication
  - Multi-factor authentication ready

- ✅ **HTTPS/TLS Configuration** (`src/core/https_config.py`)
  - TLS 1.2/1.3 support
  - Strong cipher suites (ECDHE, AES-GCM, ChaCha20)
  - Security headers (HSTS, CSP, X-Frame-Options)
  - Certificate management

- ✅ **CSRF Protection** (`src/core/csrf_protection.py`)
  - Token-based validation
  - HMAC signatures
  - Time-limited tokens (1 hour expiry)

- ✅ **Input Validation**
  - Comprehensive validators (`src/validators/`)
  - SQL injection prevention
  - XSS protection
  - Path traversal prevention

- ✅ **Data Protection**
  - GDPR-compliant data anonymization (`doc-anonymizer.py`)
  - Backup encryption (`src/core/backup_encryption.py`)
  - Secure data storage
  - Audit logging

#### 4. **CI/CD Security** (`.github/workflows/`)

- ✅ **Automated Testing**
  - 284+ passing tests
  - Security-focused test suites
  - Integration tests
  - Performance tests

- ✅ **Code Quality Gates**
  - Required PR reviews
  - Automated PR validation
  - Test coverage tracking (CodeCov)
  - Build verification

---

## 🛡️ От чего защищён репозиторий / What the Repository is Protected From

### 1. **Уязвимости в зависимостях / Dependency Vulnerabilities**
- **Threat:** Использование устаревших библиотек с известными уязвимостями
- **Protection:** 
  - Dependabot автоматически создаёт PR для обновления уязвимых зависимостей
  - Weekly security scans (Safety, pip-audit)
  - Automated dependency updates

### 2. **Внедрение вредоносного кода / Malicious Code Injection**
- **Threat:** Злоумышленники могут попытаться внедрить вредоносный код
- **Protection:**
  - Pre-commit hooks prevent insecure code
  - Code review requirements
  - Bandit/Semgrep scanning on every PR
  - Branch protection rules

### 3. **Утечка секретов / Secret Leakage**
- **Threat:** Случайная фиксация паролей, API ключей, токенов
- **Protection:**
  - Gitleaks scanner in CI/CD pipeline
  - `.gitignore` excludes sensitive files
  - `.env.example` для конфигурации (не `.env`)
  - Secret scanning на каждом push

### 4. **SQL Injection / XSS / CSRF**
- **Threat:** Веб-атаки на приложение
- **Protection:**
  - SQLAlchemy ORM (parameterized queries)
  - Input validation and sanitization
  - CSRF token validation
  - Content Security Policy headers
  - XSS protection headers

### 5. **Unauthorized Access / Несанкционированный доступ**
- **Threat:** Неавторизованный доступ к данным и функциям
- **Protection:**
  - JWT authentication
  - Role-Based Access Control (RBAC)
  - API key validation
  - Audit logging

### 6. **Data Breaches / Утечки данных**
- **Threat:** Раскрытие персональных или конфиденциальных данных
- **Protection:**
  - Data anonymization (GDPR-compliant)
  - Backup encryption (AES-256)
  - Secure data storage
  - Access control

### 7. **Path Traversal Attacks**
- **Threat:** Доступ к файлам за пределами разрешённых директорий
- **Protection:**
  - Safe path validation
  - Secure tar extraction (fixed B202 vulnerability)
  - Input sanitization

### 8. **Information Disclosure**
- **Threat:** Раскрытие внутренней информации через debug mode
- **Protection:**
  - Flask debug mode controlled by environment variable
  - Error handling without stack traces in production
  - Secure logging

---

## 🔍 Поддерживаемые версии / Supported Versions

| Version | Supported          | Security Updates |
| ------- | ------------------ | ---------------- |
| 4.2.x   | ✅ Yes            | Active           |
| 4.1.x   | ✅ Yes            | Active           |
| 4.0.x   | ⚠️ Limited       | Critical only    |
| < 4.0   | ❌ No             | Not supported    |

**Note:** Рекомендуется использовать последнюю версию для получения всех обновлений безопасности.

---

## 🚨 Reporting a Vulnerability / Сообщение об уязвимости

### Как сообщить о проблеме безопасности / How to Report a Security Issue

Если вы обнаружили уязвимость в безопасности, **не создавайте публичный issue**. Вместо этого:

If you discover a security vulnerability, **do not create a public issue**. Instead:

1. **Отправьте приватное сообщение / Send a private message:**
   - Email: security@example.com (или email владельца репозитория)
   - GitHub Security Advisories: [Create a security advisory](https://github.com/svend4/daten20/security/advisories/new)

2. **Включите следующую информацию / Include the following information:**
   - Описание уязвимости / Vulnerability description
   - Шаги для воспроизведения / Steps to reproduce
   - Потенциальное влияние / Potential impact
   - Предложенное решение (если есть) / Suggested fix (if any)
   - Версия ПО / Software version

3. **Ожидаемый ответ / Expected Response:**
   - Подтверждение получения: в течение 48 часов
   - Первоначальная оценка: в течение 7 дней
   - Исправление критических уязвимостей: в течение 30 дней
   - Публичное раскрытие: координируется с исследователем

### Severity Levels / Уровни серьёзности

- **🔴 Critical:** Немедленное исправление (RCE, authentication bypass)
- **🟠 High:** Высокий приоритет (SQL injection, XSS, data exposure)
- **🟡 Medium:** Средний приоритет (CSRF, information disclosure)
- **🟢 Low:** Низкий приоритет (minor information leaks)

---

## 🔧 Как защитить форк репозитория / How to Protect a Fork

Если вы создали форк этого репозитория, следуйте этим рекомендациям:

If you forked this repository, follow these guidelines:

### 1. **Включите Dependabot / Enable Dependabot**

```yaml
# В вашем форке: Settings → Security → Dependabot
# Enable:
- Dependabot alerts
- Dependabot security updates
- Dependabot version updates
```

### 2. **Настройте Branch Protection / Configure Branch Protection**

```
Settings → Branches → Add rule для main/master:
✅ Require pull request reviews before merging (минимум 1 reviewer)
✅ Require status checks to pass before merging
✅ Require branches to be up to date before merging
✅ Include administrators
✅ Restrict who can push to matching branches
```

### 3. **Включите Security Features / Enable Security Features**

```
Settings → Security:
✅ Dependency graph
✅ Dependabot alerts
✅ Dependabot security updates
✅ Code scanning (если доступно)
✅ Secret scanning (для публичных репозиториев)
```

### 4. **Настройте Workflows / Configure Workflows**

Убедитесь, что `.github/workflows/security.yml` активирован:
- Проверьте, что workflow выполняется успешно
- Настройте уведомления о провалах
- Регулярно проверяйте отчёты безопасности

### 5. **Используйте .env для секретов / Use .env for Secrets**

```bash
# НИКОГДА не коммитьте файл .env
# NEVER commit .env file

# Используйте .env.example как шаблон
cp .env.example .env

# Редактируйте .env с вашими секретами
# Edit .env with your secrets

# .gitignore уже содержит .env
```

### 6. **Регулярные обновления / Regular Updates**

```bash
# Синхронизируйте с upstream
git remote add upstream https://github.com/svend4/daten20.git
git fetch upstream
git merge upstream/main

# Проверьте обновления безопасности
pip-audit
bandit -r src/
```

---

## 🔐 Best Practices for Contributors / Рекомендации для контрибьюторов

### При разработке / During Development

1. **Никогда не коммитьте секреты / Never commit secrets:**
   ```bash
   # Плохо / Bad:
   API_KEY = "sk_live_abc123..."
   
   # Хорошо / Good:
   API_KEY = os.getenv("API_KEY")
   ```

2. **Используйте безопасные функции / Use secure functions:**
   ```python
   # Плохо / Bad:
   eval(user_input)
   exec(user_input)
   
   # Хорошо / Good:
   # Валидируйте и санитизируйте ввод
   ```

3. **Валидируйте входные данные / Validate inputs:**
   ```python
   from src.validators import validate_input
   
   validated_data = validate_input(user_data, schema)
   ```

4. **Используйте параметризованные запросы / Use parameterized queries:**
   ```python
   # SQLAlchemy ORM (безопасно)
   User.query.filter_by(username=username).first()
   
   # Не используйте string concatenation
   ```

5. **Запускайте тесты безопасности / Run security tests:**
   ```bash
   # Перед коммитом / Before commit:
   bandit -r src/
   pip-audit
   safety check
   ```

### При создании PR / When Creating PRs

1. ✅ Убедитесь, что все тесты проходят
2. ✅ Запустите security scanners локально
3. ✅ Обновите документацию
4. ✅ Следуйте coding standards
5. ✅ Опишите изменения в PR description

---

## 📚 Дополнительные ресурсы / Additional Resources

### Документация безопасности / Security Documentation

- [Security Enhancements Guide](docs/SECURITY_ENHANCEMENTS_GUIDE.md)
- [Security Audit Report](SESSION_TASK54_SECURITY_AUDIT_REPORT.md)
- [Security Fixes Report](SESSION_TASK55_SECURITY_FIXES_REPORT.md)

### Инструменты / Tools Used

- **Bandit** - Python security linter
- **Semgrep** - Static analysis security scanner
- **Safety** - Dependency vulnerability scanner
- **pip-audit** - Python package auditing
- **Gitleaks** - Secret detection
- **Dependabot** - Automated dependency updates

### Полезные ссылки / Useful Links

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

---

## 📞 Контакты / Contact

- **Repository:** https://github.com/svend4/daten20
- **Issues:** https://github.com/svend4/daten20/issues (только для не-security issues)
- **Security:** Use GitHub Security Advisories for vulnerabilities

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Security policy is maintained and updated by the project maintainers.

**Last Updated:** January 21, 2026
**Version:** 4.2
