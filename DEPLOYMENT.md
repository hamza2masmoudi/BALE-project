# BALE 2.1 Deployment Guide

> **Architecture**: Open-Weight Neuro-Symbolic
> **Infrastructure**: Docker + Ollama (LocalHost)

## 1. Prerequisites
*   **Host Machine**: Mac (M1/M2/M3), Linux, or Windows (WSL2) with 16GB+ RAM.
*   **Docker**: Installed and running.
*   **Ollama**: Installed on the **HOST** machine.

---

## 2. Infrastructure Setup (The "Brain")

BALE 2.1 runs inside a container (Body) but thinking happens on the host (Brain).

### Step 1: Prepare the Host
1.  **Install Ollama**: [ollama.com](https://ollama.com)
2.  **Pull the Model**:
    ```bash
    ollama pull qwen2.5:14b
    ```
3.  **Start Server**:
    Ensure Ollama is running (`ollama serve`). By default it listens on port `11434`.

---

## 3. Application Deployment (The "Body")

### Option A: Docker (Recommended)
This method isolates the Python environment but networks with the host for intelligence.

1.  **Configure `.env`**:
    Ensure your `.env` file points to the Docker host gateway:
    ```bash
    LOCAL_LLM_ENDPOINT=http://host.docker.internal:11434/v1/chat/completions
    LOCAL_LLM_MODEL=qwen2.5:14b
    ```
    *(Note: `docker-compose.yml` sets this automatically, but good to keep in sync).*

2.  **Build & Run**:
    ```bash
    docker-compose up --build -d
    ```

3.  **Access**:
    Open `http://localhost:8501`.

### Option B: Bare Metal (Local Python)
Use this for development or if you don't use Docker.

1.  **Install**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Run**:
    ```bash
    ./run.sh
    ```

---

## 4. Troubleshooting Network

If the container cannot see Ollama:
1.  **Mac/Windows**: `host.docker.internal` works out of the box.
2.  **Linux**: You may need to add `--network="host"` or verify `host-gateway` support in your Docker version.

## 5. Verification
Run the Smoke Test inside the container to verify the brain link:
```bash
docker exec -it bale_engine python3 tests/benchmark_smoke.py
```
Target: **✅ PASS**
