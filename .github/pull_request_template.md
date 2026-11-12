## 📋 Description
<!-- Provide a brief description of your changes -->

## 🔗 Related Issue
<!-- Link to the issue this PR addresses -->
Closes #

## 🛠️ Type of Change
<!-- Mark the relevant option with an 'x' -->
- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🔒 Security fix
- [ ] 🎨 Code style update (formatting, renaming)
- [ ] ♻️ Code refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] ✅ Test update

## 🔒 Security Considerations
<!-- Answer the following security questions -->
- [ ] This PR does not introduce any new security vulnerabilities
- [ ] I have reviewed the code for potential SQL injection, XSS, or CSRF issues
- [ ] Sensitive data is not exposed in logs or error messages
- [ ] No secrets or credentials are committed
- [ ] Input validation is properly implemented
- [ ] Authentication/authorization is properly enforced (if applicable)

## ✅ Testing
<!-- Describe the tests you ran -->
- [ ] All existing tests pass
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have run security scanners (bandit, pip-audit) locally

**Test commands run:**
```bash
# Example:
# pytest tests/
# bandit -r src/
```

## 📸 Screenshots (if applicable)
<!-- Add screenshots to help explain your changes -->

## 📝 Checklist
<!-- Mark all that apply -->
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] I have checked my code for security issues using `bandit -r src/`
- [ ] I have checked dependencies for vulnerabilities using `pip-audit`
- [ ] I have updated the CHANGELOG.md (if applicable)

## 🔍 Code Quality
<!-- Automated checks results -->
- [ ] Code passes linting (`flake8`, `black`, `mypy`)
- [ ] Security scans pass (Bandit, Semgrep)
- [ ] All CI/CD checks pass

## 📖 Additional Notes
<!-- Add any additional information about the PR here -->

---

**For Reviewers:**
- Please verify all security considerations are addressed
- Check that new code follows security best practices
- Ensure no sensitive data is exposed
- Validate that tests adequately cover the changes
