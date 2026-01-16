"""
BALE LLM Fine-Tuning Pipeline
Training scripts for legal domain adaptation using LoRA.
"""
import os
import json
import torch
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from src.logger import setup_logger

logger = setup_logger("bale_finetune")


# ==================== CONFIGURATION ====================

@dataclass
class FineTuneConfig:
    """Fine-tuning configuration."""
    # Model
    base_model: str = "unsloth/Qwen2.5-32B-Instruct"
    output_dir: str = "./models/bale-legal"
    
    # LoRA
    lora_r: int = 64
    lora_alpha: int = 128
    lora_dropout: float = 0.05
    target_modules: List[str] = None
    
    # Training
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    warmup_ratio: float = 0.1
    max_seq_length: int = 4096
    
    # Hardware
    use_4bit: bool = True
    use_flash_attention: bool = True
    
    def __post_init__(self):
        if self.target_modules is None:
            self.target_modules = [
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj"
            ]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FineTuneConfig":
        return cls(**d)


# Preset configurations
PRESET_CONFIGS = {
    "qwen-32b": FineTuneConfig(
        base_model="unsloth/Qwen2.5-32B-Instruct",
        lora_r=64,
        lora_alpha=128,
        batch_size=2,
    ),
    "llama-8b": FineTuneConfig(
        base_model="unsloth/Llama-3.1-8B-Instruct",
        lora_r=32,
        lora_alpha=64,
        batch_size=8,
    ),
    "mistral-7b": FineTuneConfig(
        base_model="unsloth/Mistral-7B-Instruct-v0.3",
        lora_r=32,
        lora_alpha=64,
        batch_size=8,
    ),
}


# ==================== DATASET PREPARATION ====================

class LegalDatasetBuilder:
    """Build fine-tuning datasets from BALE training examples."""
    
    SYSTEM_PROMPT = """You are BALE, a specialized legal AI assistant trained to analyze international commercial contracts. You provide precise, jurisdiction-aware analysis with explicit citations to legal authorities. You identify ambiguities, assess litigation risk, and suggest contract improvements."""
    
    def __init__(self, output_dir: str = "./training/output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def build_instruction(self, task_type: str, input_data: Dict) -> str:
        """Build instruction based on task type."""
        templates = {
            "interpretation": "Analyze the following contract clause for ambiguities, applicable legal principles, and potential risks:\n\n{clause}",
            "risk_assessment": "Assess the litigation risk for this clause, identifying specific vulnerabilities:\n\n{clause}\n\nJurisdiction: {jurisdiction}",
            "harmonization": "Suggest improvements to this clause to reduce legal risk while preserving commercial intent:\n\n{clause}",
            "simulation": "Simulate how opposing counsel might attack this clause in litigation:\n\n{clause}",
            "citation": "Identify the relevant legal authorities and precedents that apply to:\n\n{clause}\n\nJurisdiction: {jurisdiction}",
        }
        template = templates.get(task_type, templates["interpretation"])
        return template.format(**input_data)
    
    def format_alpaca(self, examples: List[Dict]) -> List[Dict]:
        """Format examples in Alpaca format."""
        formatted = []
        for ex in examples:
            formatted.append({
                "instruction": self.build_instruction(
                    ex.get("task_type", "interpretation"),
                    ex
                ),
                "input": "",
                "output": ex.get("response", ex.get("output", "")),
                "system": self.SYSTEM_PROMPT
            })
        return formatted
    
    def format_chatml(self, examples: List[Dict]) -> List[Dict]:
        """Format examples in ChatML format."""
        formatted = []
        for ex in examples:
            instruction = self.build_instruction(
                ex.get("task_type", "interpretation"),
                ex
            )
            formatted.append({
                "messages": [
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": instruction},
                    {"role": "assistant", "content": ex.get("response", ex.get("output", ""))}
                ]
            })
        return formatted
    
    def save_dataset(
        self, 
        examples: List[Dict], 
        name: str,
        format: str = "chatml"
    ) -> Path:
        """Save dataset to file."""
        if format == "alpaca":
            data = self.format_alpaca(examples)
        else:
            data = self.format_chatml(examples)
        
        output_path = self.output_dir / f"{name}_{format}.jsonl"
        
        with open(output_path, "w") as f:
            for item in data:
                f.write(json.dumps(item) + "\n")
        
        logger.info(f"Saved {len(data)} examples to {output_path}")
        return output_path


# ==================== TRAINING SCRIPT ====================

class FineTuner:
    """
    Fine-tuning orchestrator using Unsloth for efficient training.
    """
    
    def __init__(self, config: FineTuneConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
    
    def setup_model(self):
        """Load and prepare model with LoRA."""
        try:
            from unsloth import FastLanguageModel
            
            self.model, self.tokenizer = FastLanguageModel.from_pretrained(
                model_name=self.config.base_model,
                max_seq_length=self.config.max_seq_length,
                load_in_4bit=self.config.use_4bit,
                dtype=None,  # Auto-detect
            )
            
            self.model = FastLanguageModel.get_peft_model(
                self.model,
                r=self.config.lora_r,
                lora_alpha=self.config.lora_alpha,
                lora_dropout=self.config.lora_dropout,
                target_modules=self.config.target_modules,
                use_gradient_checkpointing="unsloth",
            )
            
            logger.info(f"Model loaded: {self.config.base_model}")
            return True
            
        except ImportError:
            logger.error("unsloth not installed. Install with: pip install unsloth")
            return False
    
    def train(self, dataset_path: str, resume_from: str = None):
        """Run fine-tuning."""
        if self.model is None:
            if not self.setup_model():
                return None
        
        try:
            from trl import SFTTrainer
            from transformers import TrainingArguments
            from datasets import load_dataset
            
            # Load dataset
            dataset = load_dataset("json", data_files=dataset_path, split="train")
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir=self.config.output_dir,
                num_train_epochs=self.config.num_epochs,
                per_device_train_batch_size=self.config.batch_size,
                gradient_accumulation_steps=self.config.gradient_accumulation_steps,
                learning_rate=self.config.learning_rate,
                warmup_ratio=self.config.warmup_ratio,
                logging_steps=10,
                save_strategy="epoch",
                fp16=not torch.cuda.is_bf16_supported(),
                bf16=torch.cuda.is_bf16_supported(),
                optim="adamw_8bit",
                seed=42,
            )
            
            # Trainer
            trainer = SFTTrainer(
                model=self.model,
                tokenizer=self.tokenizer,
                train_dataset=dataset,
                args=training_args,
                max_seq_length=self.config.max_seq_length,
            )
            
            # Train
            logger.info("Starting fine-tuning...")
            trainer.train(resume_from_checkpoint=resume_from)
            
            # Save
            self.model.save_pretrained(self.config.output_dir)
            self.tokenizer.save_pretrained(self.config.output_dir)
            
            logger.info(f"Model saved to {self.config.output_dir}")
            return self.config.output_dir
            
        except ImportError as e:
            logger.error(f"Missing dependency: {e}")
            return None
    
    def save_lora_adapter(self, path: str = None):
        """Save only the LoRA adapter weights."""
        if self.model is None:
            logger.error("No model loaded")
            return
        
        adapter_path = path or f"{self.config.output_dir}/adapter"
        self.model.save_pretrained(adapter_path)
        logger.info(f"LoRA adapter saved to {adapter_path}")
        return adapter_path


# ==================== MODEL VERSIONING ====================

@dataclass
class ModelVersion:
    """Track model versions."""
    version: str
    base_model: str
    adapter_path: str
    created_at: str
    
    # Training info
    dataset_name: str = ""
    num_examples: int = 0
    training_hours: float = 0.0
    
    # Performance
    eval_accuracy: float = 0.0
    eval_risk_mae: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ModelRegistry:
    """Manage model versions."""
    
    def __init__(self, registry_path: str = "./models/registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.versions: Dict[str, ModelVersion] = {}
        self._load()
    
    def _load(self):
        if self.registry_path.exists():
            with open(self.registry_path) as f:
                data = json.load(f)
                for v_id, v_data in data.items():
                    self.versions[v_id] = ModelVersion(**v_data)
    
    def _save(self):
        with open(self.registry_path, "w") as f:
            json.dump(
                {k: v.to_dict() for k, v in self.versions.items()},
                f,
                indent=2
            )
    
    def register(self, version: ModelVersion) -> str:
        """Register a new model version."""
        self.versions[version.version] = version
        self._save()
        logger.info(f"Registered model version: {version.version}")
        return version.version
    
    def get(self, version: str) -> Optional[ModelVersion]:
        return self.versions.get(version)
    
    def get_latest(self) -> Optional[ModelVersion]:
        if not self.versions:
            return None
        return max(self.versions.values(), key=lambda v: v.created_at)
    
    def list_versions(self) -> List[str]:
        return list(self.versions.keys())


# ==================== CLI INTERFACE ====================

def main():
    """CLI for fine-tuning."""
    import argparse
    
    parser = argparse.ArgumentParser(description="BALE Fine-Tuning Pipeline")
    parser.add_argument("--preset", choices=list(PRESET_CONFIGS.keys()), default="llama-8b")
    parser.add_argument("--dataset", required=True, help="Path to training dataset")
    parser.add_argument("--output", default="./models/bale-legal", help="Output directory")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--resume", help="Resume from checkpoint")
    
    args = parser.parse_args()
    
    config = PRESET_CONFIGS[args.preset]
    config.output_dir = args.output
    config.num_epochs = args.epochs
    
    trainer = FineTuner(config)
    result = trainer.train(args.dataset, resume_from=args.resume)
    
    if result:
        # Register version
        registry = ModelRegistry()
        version = ModelVersion(
            version=f"v{datetime.now().strftime('%Y%m%d_%H%M')}",
            base_model=config.base_model,
            adapter_path=result,
            created_at=datetime.utcnow().isoformat(),
            dataset_name=args.dataset,
        )
        registry.register(version)
        print(f"\n✅ Training complete! Model: {version.version}")


if __name__ == "__main__":
    main()
