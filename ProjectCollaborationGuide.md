# 🚀 Team Git Guide: How to Work Together Without Breaking Things

Collaborating on a team is different than working solo. On a team, the `main` branch is sacred. Following these rules ensures that our app stays stable and your teammates stay happy.

---

## 🛠 The Golden Workflow
We use a **Feature Branch Workflow**. This means no one writes code directly on `main`.

### 1. Start of the Day: Sync Up
Before you write a single line of code, make sure your local machine knows what happened while you were away.
* **Switch to main:** `git checkout main`
* **Pull latest changes:** `git pull origin main`

### 2. Creating a Feature Branch
Always create your new branch from the latest `main`.
* **Create and switch:** `git checkout -b feature/your-feature-name`
    * *Tip: Use descriptive names like `feature/login-validation` or `bugfix/header-typo`.*

### 3. The Development Loop
As you work, commit often. Small commits are easier to review.
* **Check status:** `git status` (See what files you changed)
* **Stage changes:** `git add .`
* **Commit:** `git commit -m "Brief description of what you did"`
* **Push to server:** `git push origin feature/your-feature-name`
    * *Note: If you don't push, I can't see your changes to review them!*

### 4. Keeping Your Feature Fresh
If I merge someone else's code into `main` while you are still working, your branch is now "out of date." Merge `main` into your branch daily:
1. **Switch to main:** `git checkout main`
2. **Pull the latest:** `git pull origin main` (Crucial! This gets the new stuff from the server)
3. **Go back to your branch:** `git checkout feature/your-feature-name`
4. **Merge the update:** `git merge main`



[Image of git feature branch workflow diagram]


---

## 📂 What to Git (and what NOT to Git)

### ✅ What to Include
* **Source code:** All your logic files like `.js`, `.py`, `.html`, `.css`.
* **Configuration templates:** Files like `config.example.json`.
* **Documentation:** `README.md` or other setup guides.
* **Assets:** Small icons, SVGs, or essential UI images.

### ❌ What to Exclude
* **Dependencies:** Never commit `node_modules/` or `venv/`.
* **Secrets & Credentials:** Never commit `.env` files or API keys.
* **Local IDE settings:** Folders like `.vscode/` or `.idea/`.
* **Build folders:** Folders like `/dist` or `/build`.

---

## 🔍 Inspecting History
Before pushing, it’s good to see what you (and others) have done.
* **Visual Overview:** Run `gitk` to open a graphical window showing the branch tree and commits.
* **Text List:** Run `git log --name-only` to see a list of commits and exactly which files were changed in each one.

---

## 🏁 The Merge Request (MR) Process
Once your feature is done and pushed:
1. Go to the repository online and create a **Merge Request** to `main`.
2. **The Review:** I will review each MR. If I leave comments, fix them and push again to the same branch.
3. **The Merge:** Once approved, I will merge it into `main`.

---

## 🛠 Troubleshooting & "Undo" Guide

### "I committed a file I shouldn't have!"
If you accidentally added a file (like a secret or a huge log file) and committed it:
* **Remove it but keep the local copy:** `git rm --cached <filename>`
* **Remove it and delete the local file:** `git rm <filename>`
* Then, `git commit --amend` to fix the mistake.

### "There is a Merge Conflict!"
Don't try to edit the `<<<<<<< HEAD` markers manually if you aren't comfortable. Use a tool:
1. **Use a Merge Tool:** Run `git mergetool`. This will open a visual side-by-side editor (like VS Code, Meld, or KDiff3).
2. **Select the version you want:** Use the UI to pick the "Left" or "Right" side.
3. **Save and Close:** Once you save and exit the tool, Git will automatically stage the fix.



### "I started working on the wrong branch!"
If you haven't committed yet:
1. `git stash` (Hides your changes temporarily)
2. `git checkout correct-branch-name`
3. `git stash pop` (Brings your changes back)

### "I want to throw away everything and start over"
**Warning: This deletes all uncommitted work!**
```bash
git reset --hard HEAD
```

---
**Remember:** If you are ever unsure, **stop and ask**. It is much easier to fix a question than it is to fix a broken commit history!