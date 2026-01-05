# BALE ~ Binary Adjudication & Litigation Engine

> **Status**: BALE 2.1 (Open Neural Validation Phase)  
> **Architecture**: Neuro-Symbolic (Hybrid)  
> **Key Feature**: Deterministic Adjudication via "Conditional Determinism"

## Overview
BALE is a research-grade legal reasoning engine designed to audit international commercial contracts. It identifies distinct conflicts between **Civil Law** (Napoleonic Code) and **Common Law** (English Law) interpretations using a multi-agent dialectic application.

## Key Capabilities
*   **Ontology-First**: Weights authorities (Constitution > Contract) to prevent hallucination.
*   **Dialectic Synthesis**: Uses two opposing agents (Civilist vs. Commonist) to find the "Interpretive Gap."
*   **Deterministic Judge**: Adjudication is performed by symbolic Python logic, not by an LLM.

## Architecture
See [TECHNICAL_MANUAL.md](TECHNICAL_MANUAL.md) for a deep dive into the engineering principles.

## Quick Start
```bash
# 1. Clone
git clone git@github.com:hamza2masmoudi/BALE-project.git

# 2. Setup
./run.sh
```

## Documentation
*   [ARCHITECTURE.md](ARCHITECTURE.md) - System Design
*   [TECHNICAL_MANUAL.md](TECHNICAL_MANUAL.md) - Deep Dive for Engineers
*   [DEPLOYMENT.md](DEPLOYMENT.md) - production guide
