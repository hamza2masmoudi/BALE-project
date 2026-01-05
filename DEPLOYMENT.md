# BALE 2.0 Deployment Guide

## 1. Prerequisites
*   **Python 3.10+** installed.
*   **Docker** (Optional, for containerized deployment).
*   **API Keys**:
    *   Mistral AI (`MISTRAL_API_KEY`)
    *   DeepSeek (`DEEPSEEK_API_KEY`) - *Optional (System falls back to Mistral)*

## 2. Installation

### Local Deployment
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-repo/bale-project.git
    cd bale-project
    ```

2.  **Create Virtual Environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration**:
    *   Copy `.env.example` to `.env`.
    *   Add your API keys.

5.  **Run the Application**:
    ```bash
    streamlit run app.py
    ```

### Docker Deployment
1.  **Build Image**:
    ```bash
    docker-compose build
    ```

2.  **Run Container**:
    ```bash
    docker-compose up
    ```
    Access the app at `http://localhost:8501`.

## 3. Production Notes
*   **Concurrency**: Streamlit is single-threaded by default. For high traffic, consider deploying on **Google Cloud Run** or **AWS Fargate** with multiple instances.
*   **Vector Database**: The current implementation uses local ChromaDB. For production, switch to a managed Vector DB (Pinecone/Weaviate) by updating `src/vector_store.py`.
*   **Logging**: Logs are currently output to stdout. Configure a centralized logging driver (e.g., CloudWatch) in `docker-compose.yml`.

## 4. Verification
To verify the deployment is scientifically sound before serving traffic:
```bash
python3 tests/benchmark_soundness.py
```
Target: **>80% Pass Rate** on the Gold Set.
