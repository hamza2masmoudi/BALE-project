#!/usr/bin/env python3
"""
BALE V9 Risk-Focused Training Script
Fine-tunes the V8 model on risk-focused data to improve risk detection accuracy.
Target: 45% → 85%+ risk accuracy
"""
import subprocess
import sys
from pathlib import Path
def main():
"""Run risk-focused fine-tuning."""
# Configuration
base_model = "mlx-community/Mistral-7B-Instruct-v0.3-4bit"
base_adapter = "models/bale-legal-lora-v8-ultimate" # Continue from V8
output_adapter = "models/bale-legal-lora-v9-risk"
train_data = "data/risk_training_v9/train.jsonl"
valid_data = "data/risk_training_v9/valid.jsonl"
# Training parameters (lower LR for fine-tuning)
iters = 2000
learning_rate = 5e-6 # Lower than initial training
batch_size = 1
lora_rank = 16
lora_layers = 8
# Check if files exist
if not Path(train_data).exists():
print(f" Training data not found: {train_data}")
print("Run: python src/data/generate_risk_training.py first")
sys.exit(1)
# Build command
cmd = [
"python3", "-m", "mlx_lm.lora",
"--model", base_model,
"--train",
"--data", str(Path(train_data).parent),
"--iters", str(iters),
"--learning-rate", str(learning_rate),
"--batch-size", str(batch_size),
"--lora-layers", str(lora_layers),
"--lora-rank", str(lora_rank),
"--adapter-path", output_adapter,
"--val-batches", "25",
"--steps-per-report", "50",
"--steps-per-eval", "200",
"--save-every", "500"
]
# Add resume from V8 adapter if it exists
if Path(base_adapter).exists():
print(f" Continuing from V8 adapter: {base_adapter}")
cmd.extend(["--resume-adapter-file", base_adapter])
else:
print(f" V8 adapter not found, training from base model")
print("\n" + "="*60)
print("BALE V9 RISK-FOCUSED TRAINING")
print("="*60)
print(f"Base model: {base_model}")
print(f"Training data: {train_data}") print(f"Output adapter: {output_adapter}")
print(f"Iterations: {iters}")
print(f"Learning rate: {learning_rate}")
print("="*60 + "\n")
# Run training
print("Starting training...")
print(f"Command: {' '.join(cmd)}\n")
result = subprocess.run(cmd, cwd=Path(__file__).parent.parent.parent)
if result.returncode == 0:
print("\n Training complete!")
print(f"Adapter saved to: {output_adapter}")
print("\nNext step: Run golden evaluation to verify improvement")
print(" python evaluation/run_golden_eval.py --adapter-path models/bale-legal-lora-v9-risk")
else:
print(f"\n Training failed with code {result.returncode}")
sys.exit(1)
if __name__ == "__main__":
main()
