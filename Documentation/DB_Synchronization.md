# 🔄 Database Synchronization & Persistence

This document explains how **IneX̂ō** saves your financial data and how you can switch between Local and Docker versions without losing progress.

## 💾 The Core Concept: `finance.db`

The application uses a **local SQLite database** file named `finance.db` located in the project root folder.
*   This file contains **ALL** your data (Users, Transactions, Settings).
*   There is no external cloud database by default.
*   **Back this file up!** (Our auto-backup script does this for you by pushing to Git).

---

## 🔌 How Synchronization Works

### 1. Local Run (Python/Bat)
When you run the app locally (e.g., via `inexo_start.bat`), the Python script reads/writes directly to the `finance.db` file in the folder.

### 2. Docker / Podman Run
We use **Volume Mapping** to ensure data persistence.

*   **Configuration**: In `docker-compose.yml`, you will see:
    ```yaml
    volumes:
      - ../:/app
    ```
*   **What this means**: The container does NOT keep data inside itself. It "borrows" the folder from your host machine.
*   **Result**: If you add a transaction inside Docker, it writes to `finance.db` **on your actual hard drive**. If you verify the file timestamp on Windows, you will see it updated instantly.

---

## ⚠️ CRITICAL WARNINGS

### 🚫 1. SINGLE ACCESS RULE
**NEVER run the Local App and Docker Container at the same time.**

*   **Why?** SQLite is a file-based database. If two processes (Local Python + Docker Python) try to write to the file simultaneously, the database will **LOCK**.
*   **Error Message**: `OperationalError: database is locked`.
*   **Fix**: Always **STOP** one environment before STARTING the other.
    *   Stop Docker: `docker-compose down`
    *   Stop Local: Close terminal / `inexo_stop.bat`

### 🆕 2. First Run
If `finance.db` does not exist:
*   **Local Run**: The app creates it automatically on first launch.
*   **Docker Run**: The app inside the container creates it, and thanks to volume mapping, it appears on your Windows folder too.

---

## 🔄 Switching Environments

You can seamlessly switch between environments:

1.  **Day 1**: Run via `inexo_start.bat`. Add some expenses. **Close App**.
2.  **Day 2**: Open Terminal. Run `docker-start.bat`.
3.  **Result**: You will see all yesterday's expenses. The data is shared.

---

## 🛡️ Backup Logic

The `inexo_auto_backup_db.ps1` script (triggered by the launcher) watches `finance.db` for changes.
*   When the file changes (timestamp update), it commits the change to **Git**.
*   This ensures you have a version history of your finances in your private repository.
