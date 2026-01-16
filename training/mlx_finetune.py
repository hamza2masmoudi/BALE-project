"""
BALE MLX Finetuning Pipeline
Finetune a 7B model on Apple Silicon using MLX.

This creates a domain-specific legal model that is BALE's core IP.
"""
import json
import os
from pathlib import Path
from typing import List, Dict
import argparse


def prepare_training_data(
    input_path: str = "data/training/legal_finetune.jsonl",
    output_dir: str = "data/mlx_training",
    train_ratio: float = 0.9
) -> Dict[str, str]:
    """
    Convert training data to MLX chat format.
    
    MLX expects:
    - train.jsonl
    - valid.jsonl
    
    Each line: {"messages": [{"role": "system", "content": ...}, {"role": "user", "content": ...}, {"role": "assistant", "content": ...}]}
    """
    os.makedirs(output_dir, exist_ok=True)
    
    examples = []
    with open(input_path) as f:
        for line in f:
            ex = json.loads(line)
            # Convert to chat format
            messages = [
                {"role": "system", "content": "You are BALE, an expert legal contract analyst. Provide precise, actionable analysis of contract clauses."},
                {"role": "user", "content": f"{ex['instruction']}\n\n{ex['input']}"},
                {"role": "assistant", "content": ex['output']}
            ]
            examples.append({"messages": messages})
    
    # Split train/valid
    n_train = int(len(examples) * train_ratio)
    train_data = examples[:n_train]
    valid_data = examples[n_train:]
    
    # Write files
    train_path = os.path.join(output_dir, "train.jsonl")
    valid_path = os.path.join(output_dir, "valid.jsonl")
    
    with open(train_path, "w") as f:
        for ex in train_data:
            f.write(json.dumps(ex) + "\n")
    
    with open(valid_path, "w") as f:
        for ex in valid_data:
            f.write(json.dumps(ex) + "\n")
    
    print(f"✅ Training data prepared:")
    print(f"   Train: {len(train_data)} examples → {train_path}")
    print(f"   Valid: {len(valid_data)} examples → {valid_path}")
    
    return {"train": train_path, "valid": valid_path}


def create_lora_config(output_path: str = "training/lora_config.yaml"):
    """Create LoRA configuration for legal domain finetuning."""
    config = """# BALE Legal Model LoRA Configuration
# Optimized for Apple Silicon M-series

# Model to finetune
model: "mlx-community/Mistral-7B-Instruct-v0.3-4bit"

# Training parameters
train:
  iters: 1000
  batch_size: 2
  learning_rate: 1e-5
  grad_checkpoint: true

# LoRA parameters  
lora:
  rank: 16
  alpha: 32
  dropout: 0.05
  target_modules:
    - q_proj
    - v_proj
    - k_proj
    - o_proj
    - gate_proj
    - up_proj
    - down_proj

# Data
data:
  train: "data/mlx_training/train.jsonl"
  valid: "data/mlx_training/valid.jsonl"

# Output
output:
  adapter_path: "models/bale-legal-lora"
  checkpoint_every: 100
"""
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(config)
    
    print(f"✅ LoRA config saved to: {output_path}")
    return output_path


def run_finetuning():
    """
    Run MLX LoRA finetuning.
    
    This uses the mlx-lm library for efficient Apple Silicon training.
    """
    try:
        from mlx_lm import load, generate
        from mlx_lm.tuner import train
        import mlx.core as mx
    except ImportError:
        print("❌ MLX not installed. Run: pip install mlx mlx-lm")
        return False
    
    # Paths
    model_name = "mlx-community/Mistral-7B-Instruct-v0.3-4bit"
    train_data = "data/mlx_training/train.jsonl"
    valid_data = "data/mlx_training/valid.jsonl"
    adapter_path = "models/bale-legal-lora"
    
    # Check if data exists
    if not os.path.exists(train_data):
        print(f"❌ Training data not found: {train_data}")
        print("   Run: python -m training.mlx_finetune --prepare")
        return False
    
    print(f"🚀 Starting MLX LoRA finetuning")
    print(f"   Model: {model_name}")
    print(f"   Train data: {train_data}")
    print(f"   Output: {adapter_path}")
    print()
    
    # Load model
    print("Loading model (this may take a few minutes)...")
    model, tokenizer = load(model_name)
    
    # Count training examples
    with open(train_data) as f:
        n_train = sum(1 for _ in f)
    
    print(f"   Training examples: {n_train}")
    
    # Train with LoRA
    os.makedirs(adapter_path, exist_ok=True)
    
    train(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_data,
        val_dataset=valid_data,
        adapter_path=adapter_path,
        iters=min(n_train // 2, 500),  # Cap at 500 iterations
        batch_size=2,
        num_layers=16,  # Number of layers to apply LoRA
        learning_rate=1e-5,
    )
    
    print(f"\n✅ Finetuning complete!")
    print(f"   Adapter saved to: {adapter_path}")
    
    return True


def test_finetuned_model(prompt: str = None):
    """Test the finetuned model."""
    try:
        from mlx_lm import load, generate
    except ImportError:
        print("❌ MLX not installed")
        return
    
    adapter_path = "models/bale-legal-lora"
    
    if not os.path.exists(adapter_path):
        print(f"❌ No adapter found at {adapter_path}")
        print("   Run finetuning first")
        return
    
    # Load base model with adapter
    model_name = "mlx-community/Mistral-7B-Instruct-v0.3-4bit"
    print(f"Loading model with adapter...")
    model, tokenizer = load(model_name, adapter_path=adapter_path)
    
    if not prompt:
        prompt = """Analyze this contract clause for legal risks:

"The Vendor shall defend, indemnify, and hold harmless the Customer from any and all claims, losses, damages, and expenses without any limitation whatsoever."

Identify the risk level and key issues."""
    
    print(f"\n📝 Prompt:\n{prompt}\n")
    
    # Generate
    response = generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=500,
        temp=0.1,
    )
    
    print(f"📤 Response:\n{response}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BALE MLX Finetuning Pipeline")
    parser.add_argument("--prepare", action="store_true", help="Prepare training data")
    parser.add_argument("--config", action="store_true", help="Create LoRA config")
    parser.add_argument("--train", action="store_true", help="Run finetuning")
    parser.add_argument("--test", action="store_true", help="Test finetuned model")
    parser.add_argument("--all", action="store_true", help="Run all steps")
    
    args = parser.parse_args()
    
    if args.prepare or args.all:
        prepare_training_data()
    
    if args.config or args.all:
        create_lora_config()
    
    if args.train or args.all:
        run_finetuning()
    
    if args.test:
        test_finetuned_model()
    
    if not any([args.prepare, args.config, args.train, args.test, args.all]):
        parser.print_help()
