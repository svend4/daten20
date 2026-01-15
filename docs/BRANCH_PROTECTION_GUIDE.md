# GitHub Branch Protection Rules Setup Guide

## Overview

Branch protection rules help maintain code quality by requiring specific checks to pass before merging code into protected branches. This guide explains how to configure branch protection for the Document Management System project.

---

## 📋 Table of Contents

1. [Why Branch Protection?](#why-branch-protection)
2. [Recommended Configuration](#recommended-configuration)
3. [Step-by-Step Setup](#step-by-step-setup)
4. [Protection Rules Reference](#protection-rules-reference)
5. [Troubleshooting](#troubleshooting)

---

## Why Branch Protection?

Branch protection rules provide several benefits:

- ✅ **Prevent Direct Pushes** - Require pull requests for all changes
- ✅ **Enforce Code Review** - Require at least one approval before merging
- ✅ **Automated Testing** - Require CI/CD checks to pass
- ✅ **Prevent Force Pushes** - Protect branch history
- ✅ **Maintain Code Quality** - Ensure linting and tests pass
- ✅ **Track Changes** - All changes go through pull requests

---

## Recommended Configuration

### Protected Branches

We recommend protecting these branches:

1. **`main`** - Production-ready code
2. **`develop`** - Development integration branch

### Protection Rules

| Rule | main | develop | Feature Branches |
|------|------|---------|------------------|
| Require pull request | ✅ Yes | ✅ Yes | ❌ No |
| Require approvals | ✅ 1+ | ✅ 1+ | ❌ No |
| Require CI to pass | ✅ Yes | ✅ Yes | ❌ No |
| Require branch up-to-date | ✅ Yes | ✅ Yes | ❌ No |
| Require code owners review | ✅ Yes | ⚠️ Optional | ❌ No |
| Prevent force push | ✅ Yes | ✅ Yes | ❌ No |
| Prevent deletion | ✅ Yes | ✅ Yes | ❌ No |
| Allow admin bypass | ⚠️ Emergency only | ⚠️ Optional | ❌ N/A |

---

## Step-by-Step Setup

### Step 1: Access Repository Settings

1. Go to your GitHub repository: `https://github.com/svend4/daten20`
2. Click on **Settings** (gear icon in the top menu)
3. In the left sidebar, click **Branches** under "Code and automation"

### Step 2: Add Branch Protection Rule for `main`

1. Click **Add branch protection rule**
2. Enter branch name pattern: `main`
3. Configure the following settings:

#### Protect matching branches

**Require a pull request before merging:**
- ✅ Enable this option
- ✅ **Require approvals:** Set to `1` (minimum)
- ✅ **Dismiss stale pull request approvals when new commits are pushed**
- ⚠️ Optional: **Require review from Code Owners**

**Require status checks to pass before merging:**
- ✅ Enable this option
- ✅ **Require branches to be up to date before merging**
- Add required status checks:
  - `test (3.9, ubuntu-latest)` - Python 3.9 tests
  - `test (3.10, ubuntu-latest)` - Python 3.10 tests
  - `test (3.11, ubuntu-latest)` - Python 3.11 tests
  - `lint` - Code quality checks

**Require conversation resolution before merging:**
- ✅ Enable this option (all review comments must be resolved)

**Require signed commits:**
- ⚠️ Optional (recommended for high-security environments)

**Require linear history:**
- ⚠️ Optional (prevents merge commits, requires rebase or squash)

**Require deployments to succeed before merging:**
- ❌ Disable (not needed for this project)

**Lock branch:**
- ❌ Disable (allows contributions)

**Do not allow bypassing the above settings:**
- ✅ Enable for maximum protection
- ⚠️ Or configure who can bypass (administrators only)

**Restrict who can push to matching branches:**
- ⚠️ Optional: Add specific users/teams who can push
- Recommended: Leave empty to require PRs from everyone

**Allow force pushes:**
- ❌ Disable

**Allow deletions:**
- ❌ Disable

4. Click **Create** to save the rule

### Step 3: Add Branch Protection Rule for `develop`

Repeat Step 2 with these modifications:

1. Branch name pattern: `develop`
2. Same settings as `main`, but with these differences:
   - **Require approvals:** Can be set to `1` or `0` (for faster development)
   - **Require code owners review:** Optional (not required)
   - **Do not allow bypassing:** Optional (can allow admin bypass)

### Step 4: Create CODEOWNERS File (Optional)

If you want to enforce code owner reviews, create a `.github/CODEOWNERS` file:

```bash
# CODEOWNERS file
# These owners will be requested for review when someone opens a pull request

# Default owners for everything in the repo
* @yourusername

# Specific owners for different parts of the codebase
/src/core/ @coreTeam
/src/ai/ @aiTeam
/tests/ @qaTeam
/docs/ @docTeam

# CLI applications
/doc-*.py @cliTeam

# CI/CD and configuration
/.github/ @devopsTeam
/pytest.ini @qaTeam
/requirements.txt @devopsTeam
```

### Step 5: Test the Protection Rules

1. Create a new feature branch: `git checkout -b test-protection`
2. Make a small change (e.g., update README)
3. Commit and push: `git push -u origin test-protection`
4. Try to push directly to `main` (should fail):
   ```bash
   git checkout main
   git merge test-protection
   git push  # ❌ Should be rejected
   ```
5. Create a pull request instead
6. Verify that CI checks run automatically
7. Verify that merge is blocked until checks pass

---

## Protection Rules Reference

### Available Status Checks

After setting up branch protection, these CI checks will be required:

#### Test Matrix Checks
- `test (3.9, ubuntu-latest)` - Tests on Python 3.9
- `test (3.10, ubuntu-latest)` - Tests on Python 3.10
- `test (3.11, ubuntu-latest)` - Tests on Python 3.11

#### Lint Checks
- `lint` - Code quality (flake8, black, isort)

### How to Add Status Checks

1. Go to branch protection rule settings
2. Under "Require status checks to pass before merging"
3. Click in the search box
4. Select checks from the list (they appear after first CI run)
5. Click "Save changes"

---

## Workflow Examples

### Standard Development Workflow

```bash
# 1. Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# 2. Make changes and commit
git add .
git commit -m "feat: add new feature"

# 3. Push feature branch
git push -u origin feature/new-feature

# 4. Create pull request on GitHub
# - Base: develop
# - Compare: feature/new-feature
# - Wait for CI checks to pass
# - Request review from team member
# - Address review comments
# - Merge when approved and checks pass

# 5. Delete feature branch after merge
git checkout develop
git pull origin develop
git branch -d feature/new-feature
```

### Hotfix Workflow (Urgent Production Fixes)

```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/urgent-fix

# 2. Make minimal changes to fix issue
git add .
git commit -m "fix: urgent production issue"

# 3. Push and create PR
git push -u origin hotfix/urgent-fix

# 4. Get expedited review
# - Fast-track approval process
# - Ensure CI passes
# - Merge to main immediately

# 5. Merge hotfix back to develop
git checkout develop
git merge hotfix/urgent-fix
git push origin develop
```

---

## Troubleshooting

### Issue: Cannot Merge PR - Status Checks Not Found

**Problem:** GitHub says required status checks are not found.

**Solution:**
1. Run CI workflow at least once on the base branch
2. Go to branch protection settings
3. Refresh the page
4. Status checks should now appear in the dropdown
5. Add them to required checks

### Issue: CI Checks Failing on Old Commits

**Problem:** Branch is behind main, CI checks failing.

**Solution:**
```bash
# Update your branch with latest main
git checkout your-branch
git fetch origin main
git rebase origin/main
# Or use merge:
git merge origin/main

# Push updated branch
git push --force-with-lease origin your-branch
```

### Issue: Need to Bypass Protection for Emergency

**Problem:** Critical fix needed, but can't wait for reviews/CI.

**Solution:**
1. **Not recommended** - Only for true emergencies
2. Temporarily disable branch protection:
   - Go to Settings → Branches
   - Edit the protection rule
   - Uncheck "Do not allow bypassing"
   - Make your emergency commit
   - **Immediately re-enable protection**
3. **Better approach:**
   - Keep "Allow specified actors to bypass" enabled
   - Add only 1-2 emergency contacts
   - Create audit trail of emergency merges

### Issue: Pre-commit Hooks Failing

**Problem:** Cannot commit code, pre-commit hooks fail.

**Solution:**
```bash
# Run pre-commit manually to see issues
pre-commit run --all-files

# Fix issues automatically where possible
black .
isort .

# If you must bypass (not recommended):
git commit --no-verify -m "message"

# Better: Fix the issues pre-commit found
```

---

## Additional Security Considerations

### Enable Dependabot Alerts

1. Go to Settings → Security & analysis
2. Enable **Dependabot alerts**
3. Enable **Dependabot security updates**
4. Review alerts regularly in the Security tab

### Enable Code Scanning

1. Go to Settings → Security & analysis
2. Enable **Code scanning alerts**
3. Set up CodeQL analysis
4. Review findings in the Security tab

### Enable Secret Scanning

1. Go to Settings → Security & analysis
2. Enable **Secret scanning**
3. GitHub will alert you if secrets are pushed

---

## Best Practices

### DO ✅

- ✅ Protect `main` and `develop` branches
- ✅ Require CI checks to pass
- ✅ Require at least 1 approval
- ✅ Keep branches up to date before merging
- ✅ Use descriptive commit messages
- ✅ Link PRs to issues
- ✅ Test locally before pushing
- ✅ Review your own PR before requesting reviews

### DON'T ❌

- ❌ Force push to protected branches
- ❌ Bypass protection rules without good reason
- ❌ Approve your own pull requests
- ❌ Merge without CI checks passing
- ❌ Ignore review comments
- ❌ Create PRs with 1000+ line changes
- ❌ Use `--no-verify` to skip hooks
- ❌ Leave stale branches after merging

---

## Summary

Branch protection is a critical part of maintaining code quality. By requiring:

1. **Pull Requests** - All changes go through review
2. **CI Checks** - Automated testing catches bugs
3. **Code Review** - Human oversight ensures quality
4. **Up-to-date Branches** - Prevent merge conflicts

You ensure that:
- 🎯 Code quality remains high
- 🐛 Bugs are caught before production
- 📚 Knowledge is shared across team
- 🔒 Production code is stable and tested

---

## Questions?

If you encounter issues with branch protection:

1. Check GitHub's [documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
2. Review CI workflow logs in the Actions tab
3. Ask for help in the team chat
4. Open an issue in the repository

---

**Last Updated:** 2026-01-15
**Version:** 1.0
**Maintained By:** DevOps Team
