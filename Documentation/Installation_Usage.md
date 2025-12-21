# 📥 Installation and Usage Guide

Welcome to **IneX̂ō**! This guide covers everything from installation to running the app using various methods (Manual, Docker, Podman).

## 📋 Prerequisites

- **Python 3.9+** (For manual run)
- **Git** (To clone the repository)
- **Docker Desktop** (Optional, for containerized run)
- **Podman Desktop** (Optional, alternative to Docker)

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "inexo"
```

### 2. Manual Setup (Python)

It is recommended to use a virtual environment.

#### 🪟 Windows Users
```powershell
# Create venv
python -m venv venv

# Activate venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 🍎 Mac / 🐧 Linux Users
```bash
# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Usage

### Method 1: One-Click Launcher (Windows Recommended)

**First Time Setup:**
If this is your first time or if you face issues, run **`localrun\inexo_initial_setup.bat`**. This will:
- Clean up any old virtual environments.
- Create a fresh `venv`.
- Install all dependencies from `requirements.txt`.

**Daily Run:**
Simply double-click **`localrun\inexo_start.bat`**. 
- It automatically activates the virtual environment.
- Starts the background backup job.
- Launches the application in your default browser.

### Method 2: Command Line (All OS)

**Windows:**
```bash
venv\Scripts\activate
streamlit run app.py
```

**Mac/Linux:**
```bash
source venv/bin/activate
streamlit run app.py
```

---

## 🐳 Docker Guide

This ensures the app runs exactly the same on any machine.

### Prerequisites
- **Docker Desktop**: Must be installed and running.

### Quick Start
1. **Start**: Run `docker-compose up` in the project folder.
2. **Access**: Open [http://localhost:8501](http://localhost:8501).
3. **Stop**: Press `Ctrl+C` or run `docker-compose down`.

### Rebuild
If you add new dependencies:
```bash
docker-compose up --build
```

### Data Persistence
Your `finance.db` is synced via volumes. Data entered in Docker is saved to your local drive.

---

## 🦭 Podman Guide (Docker Alternative)

### Prerequisites
- **Podman Desktop**: Installed.
- **podman-compose**: `pip install podman-compose`

### Quick Start
1. **Start**: Run `podman-compose up`.
2. **Access**: Open [http://localhost:8501](http://localhost:8501).
3. **Stop**: `podman-compose down`.

### Generating Kubernetes Yaml
Podman can generate K8s config from running containers:
```bash
podman generate kube inexo > finance-app-k8s.yaml
```

---

## 🔧 Troubleshooting

### Docker Issues
**Error:** `error during connect: ... pipe ... The system cannot find the file specified.`
- **Cause:** Docker Desktop is not running.
- **Fix:** Start Docker Desktop from the Windows Start menu.

**Error:** `Port 8501 is already in use`
- **Cause:** You might have the app running locally (via `bat` file) or another container running.
- **Fix:** Close the other terminal or run `docker-compose down`.

### Windows Batch File Issues
- **App fails to start**: Ensure you have Python installed and added to PATH. Try running `localrun\inexo_initial_setup.bat` to completely reset the virtual environment.

---

## ☁️ Cloud Deployment (Basic Info)

To deploy this to the cloud (AWS, Azure, DigitalOcean, etc.), the process is generally:

1.  **Build image:** Build your Docker image.
2.  **Push to Registry:** Upload to a "Container Registry" (like Docker Hub or AWS ECR).
    ```bash
    docker login
    docker tag inexo myuser/inexo
    docker push myuser/inexo
    ```
3.  **Run on Server:** On the cloud server, pull and run:
    ```bash
    docker run -p 80:8501 myuser/inexo
    ```

> **Note:** For cloud deployment, switch from local SQLite (`finance.db`) to a cloud database (PostgreSQL/MySQL) for persistence.
