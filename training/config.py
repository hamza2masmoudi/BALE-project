"""
BALE Fine-Tuning Configuration
Settings and utilities for model fine-tuning.
"""
import os
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from pathlib import Path
@dataclass
class FineTuningConfig:
"""Configuration for fine-tuning BALE models."""
# Model Selection
base_model: str = "Qwen/Qwen2.5-32B-Instruct" # or meta-llama/Meta-Llama-3-8B-Instruct
# LoRA Configuration
lora_r: int = 16 # Rank
lora_alpha: int = 32
lora_dropout: float = 0.05
target_modules: List[str] = field(default_factory=lambda: [
"q_proj", "k_proj", "v_proj", "o_proj",
"gate_proj", "up_proj", "down_proj"
])
# Training Parameters
learning_rate: float = 2e-4
batch_size: int = 4
gradient_accumulation_steps: int = 4
num_epochs: int = 3
max_seq_length: int = 4096
warmup_ratio: float = 0.03
weight_decay: float = 0.01
# Optimization
fp16: bool = True
bf16: bool = False
gradient_checkpointing: bool = True
# Dataset
train_file: str = "training/data/bale_training_alpaca.jsonl"
eval_file: Optional[str] = None
eval_split: float = 0.1
# Output
output_dir: str = "training/output"
save_steps: int = 500
logging_steps: int = 10
# Hardware
per_device_train_batch_size: int = 1
per_device_eval_batch_size: int = 1
def to_trainer_args(self) -> Dict[str, Any]:
"""Convert to HuggingFace TrainingArguments format."""
return {
"output_dir": self.output_dir,
"num_train_epochs": self.num_epochs,
"per_device_train_batch_size": self.per_device_train_batch_size,
"per_device_eval_batch_size": self.per_device_eval_batch_size,
"gradient_accumulation_steps": self.gradient_accumulation_steps,
"learning_rate": self.learning_rate,
"weight_decay": self.weight_decay,
"warmup_ratio": self.warmup_ratio,
"fp16": self.fp16,
"bf16": self.bf16,
"gradient_checkpointing": self.gradient_checkpointing,
"logging_steps": self.logging_steps,
"save_steps": self.save_steps,
"evaluation_strategy": "steps" if self.eval_file else "no",
"save_total_limit": 3,
"load_best_model_at_end": True if self.eval_file else False,
"report_to": "wandb" # or "tensorboard"
}
def to_lora_config(self) -> Dict[str, Any]:
"""Convert to PEFT LoRA config format."""
return {
"r": self.lora_r,
"lora_alpha": self.lora_alpha,
"lora_dropout": self.lora_dropout,
"target_modules": self.target_modules,
"bias": "none",
"task_type": "CAUSAL_LM"
}
# Pre-configured profiles
CONFIGS = {
"qwen_32b_lora": FineTuningConfig(
base_model="Qwen/Qwen2.5-32B-Instruct",
lora_r=16,
per_device_train_batch_size=1,
gradient_accumulation_steps=8
),
"llama_8b_lora": FineTuningConfig(
base_model="meta-llama/Meta-Llama-3-8B-Instruct",
lora_r=32,
per_device_train_batch_size=2,
gradient_accumulation_steps=4
),
"mistral_7b_lora": FineTuningConfig(
base_model="mistralai/Mistral-7B-Instruct-v0.2",
lora_r=32,
per_device_train_batch_size=2,
gradient_accumulation_steps=4
)
}
FINETUNING_SCRIPT_TEMPLATE = '''#!/bin/bash
# BALE Fine-Tuning Script
# Generated configuration for legal LLM fine-tuning
# Prerequisites:
# pip install transformers peft datasets accelerate bitsandbytes wandb
export WANDB_PROJECT="bale-legal-finetune"
export CUDA_VISIBLE_DEVICES=0
python -m training.finetune \\
--base_model "{base_model}" \\
--data_path "{train_file}" \\
--output_dir "{output_dir}" \\
--lora_r {lora_r} \\
--lora_alpha {lora_alpha} \\
--num_epochs {num_epochs} \\
--batch_size {batch_size} \\
--learning_rate {learning_rate} \\
--max_seq_length {max_seq_length} \\
--gradient_checkpointing \\
--fp16
'''
def generate_training_script(config: FineTuningConfig, output_path: str = None) -> str:
"""Generate a shell script for fine-tuning."""
script = FINETUNING_SCRIPT_TEMPLATE.format(
base_model=config.base_model,
train_file=config.train_file,
output_dir=config.output_dir,
lora_r=config.lora_r,
lora_alpha=config.lora_alpha,
num_epochs=config.num_epochs,
batch_size=config.batch_size,
learning_rate=config.learning_rate,
max_seq_length=config.max_seq_length
)
if output_path:
Path(output_path).write_text(script)
return script
