"""
BALE Startup Validation
Ensures all required dependencies and configurations are available.
"""
import os
import sys
from typing import List, Tuple
from src.logger import setup_logger
logger = setup_logger("bale_startup")
def check_environment() -> Tuple[bool, List[str]]:
"""
Validate environment configuration at startup.
Returns:
(is_valid, list_of_warnings)
"""
warnings = []
critical = False
# Check required environment variables
required = [] # Nothing strictly required anymore - we have defaults
recommended = [
("LOCAL_LLM_ENDPOINT", "Local LLM for inference"),
("DATABASE_URL", "PostgreSQL for persistence"),
("BALE_SECRET_KEY", "JWT signing key"),
]
for var, desc in required:
if not os.getenv(var):
warnings.append(f" CRITICAL: {var} not set ({desc})")
critical = True
for var, desc in recommended:
if not os.getenv(var):
warnings.append(f" {var} not set ({desc})")
# Check at least one LLM is available
has_llm = os.getenv("LOCAL_LLM_ENDPOINT") or os.getenv("MISTRAL_API_KEY")
if not has_llm:
warnings.append(" No LLM configured - analysis will fail (set LOCAL_LLM_ENDPOINT or MISTRAL_API_KEY)")
return not critical, warnings
def check_dependencies() -> Tuple[bool, List[str]]:
"""
Verify required Python packages are installed.
Returns:
(all_ok, list_of_missing)
"""
missing = []
required_packages = [
("fastapi", "FastAPI"),
("pydantic", "Pydantic"),
("langchain_core", "LangChain"),
("langgraph", "LangGraph"),
]
for package, name in required_packages:
try:
__import__(package)
except ImportError:
missing.append(f" {name} ({package}) not installed")
optional_packages = [
("redis", "Redis caching"),
("neo4j", "Knowledge graph"),
("jose", "JWT authentication"),
("passlib", "Password hashing"),
]
for package, name in optional_packages:
try:
__import__(package)
except ImportError:
missing.append(f" {name} ({package}) not installed (optional)")
return all("" not in m for m in missing), missing
def check_llm_connectivity() -> Tuple[bool, str]:
"""
Test LLM connectivity.
Returns:
(is_connected, status_message)
"""
import requests
local_endpoint = os.getenv("LOCAL_LLM_ENDPOINT")
if local_endpoint:
try:
# Try health endpoint
health_url = local_endpoint.replace("/chat/completions", "/health")
health_url = health_url.replace("/v1/", "/")
resp = requests.get(health_url, timeout=5)
if resp.status_code < 400:
return True, f" Local LLM available at {local_endpoint}"
except Exception as e:
pass
try:
# Try models endpoint for Ollama
models_url = local_endpoint.replace("/v1/chat/completions", "/api/tags")
resp = requests.get(models_url, timeout=5)
if resp.status_code < 400:
return True, f" Ollama available at {local_endpoint}"
except Exception as e:
return False, f" Local LLM unreachable: {e}"
if os.getenv("MISTRAL_API_KEY"):
return True, " Mistral API key configured"
return False, " No LLM configured"
def check_database() -> Tuple[bool, str]:
"""
Test database connectivity.
Returns:
(is_connected, status_message)
"""
db_url = os.getenv("DATABASE_URL")
if not db_url:
return False, " DATABASE_URL not set"
try:
from database.config import check_connection
if check_connection():
return True, " PostgreSQL connected"
else:
return False, " PostgreSQL connection failed"
except ImportError:
return False, " Database module not available"
except Exception as e:
return False, f" Database error: {e}"
def run_startup_checks(exit_on_critical: bool = False) -> bool:
"""
Run all startup checks and log results.
Args:
exit_on_critical: If True, exit process on critical failures.
Returns:
True if all critical checks pass.
"""
print("\n" + "="*60)
print(" BALE Startup Checks")
print("="*60 + "\n")
all_ok = True
# Environment
env_ok, env_warnings = check_environment()
print(" Environment:")
if not env_warnings:
print(" All variables configured")
else:
for w in env_warnings:
print(f" {w}")
if not env_ok:
all_ok = False
print()
# Dependencies
dep_ok, dep_missing = check_dependencies()
print(" Dependencies:")
if not dep_missing:
print(" All packages installed")
else:
for m in dep_missing:
print(f" {m}")
if not dep_ok:
all_ok = False
print()
# LLM
llm_ok, llm_status = check_llm_connectivity()
print(" LLM:")
print(f" {llm_status}")
print()
# Database
db_ok, db_status = check_database()
print(" Database:")
print(f" {db_status}")
print()
# Summary
print("="*60)
if all_ok:
print(" All critical checks passed - BALE ready to start!")
else:
print(" Some checks failed - BALE may have limited functionality")
print("="*60 + "\n")
if not all_ok and exit_on_critical:
print("Exiting due to critical failures...")
sys.exit(1)
return all_ok
if __name__ == "__main__":
from dotenv import load_dotenv
load_dotenv()
run_startup_checks()
