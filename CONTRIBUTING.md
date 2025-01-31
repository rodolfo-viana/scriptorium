# 🚀 Contributing to Scriptorium

Thank you for your interest in contributing to **Scriptorium**! To ensure a structured development process, please follow these guidelines.

---

## Branching & Pull Request Workflow

We use a **branch-based workflow** to maintain code quality.

### **1. Feature Development**

- Always create a new branch for your feature or bugfix.
- Name your branch descriptively:
```
feature/add-json-logging
bugfix/fix-log-rotation
```

### **2️. Submit PRs to `staging`**
- All feature branches **must be merged into `staging`**.
- Open a pull request (PR) from your feature branch to `staging`.
- At least **one approval is required** before merging.

### **3️. Merging `staging` into `main`**
- The `main` branch only receives PRs from `staging`.
- PRs from feature branches directly to `main` are **not allowed**.

---

## Setup Instructions

1. **Fork the repository** and clone your fork:

```sh
git clone https://github.com/rodolfo-viana/scriptorium.git
cd scriptorium
```

2. **Set up the upstream repo** (only needed once):

```sh
git remote add upstream https://github.com/rodolfo-viana/scriptorium.git
```

3. **Create a feature branch from staging**:

```sh
git checkout staging
git pull origin staging
git checkout -b feature/my-awesome-feature
```

4. **Make changes, commit, and push**:

```sh
git add .
git commit -m "Add awesome feature"
git push origin feature/my-awesome-feature
```

__PS__: Write meaningful commit message like `feat: Add structured logging in JSON format` or `fix: Resolve issue with async log rotation`.

5. **Open a PR to `staging`** and request a review.

---

## Testing

Before submitting a PR:

 - Ensure all tests pass:

```sh
pytest -v --tb=short
```

If adding a new feature, **write corresponding tests**.

---

## Heed Help?

If you have questions, feel free to open an issue.

Happy coding!


