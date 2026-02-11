"""
BALE Database Models
SQLAlchemy models for PostgreSQL persistence.
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import (
Column, String, Integer, Float, Boolean, DateTime, Text, JSON,
ForeignKey, Enum as SQLEnum, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
Base = declarative_base()
# ==================== UTILITY ====================
def generate_uuid():
return str(uuid.uuid4())
# ==================== USER & AUTH ====================
class User(Base):
"""User account for multi-tenant support."""
__tablename__ = "users"
id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
email = Column(String(256), unique=True, nullable=False, index=True)
hashed_password = Column(String(256), nullable=True) # Null for SSO users
# Profile
full_name = Column(String(256))
organization = Column(String(256))
role = Column(String(64), default="analyst") # admin, analyst, viewer
# SSO
sso_provider = Column(String(64)) # okta, azure_ad, google, etc.
sso_id = Column(String(256))
# Status
is_active = Column(Boolean, default=True)
is_verified = Column(Boolean, default=False)
# Timestamps
created_at = Column(DateTime(timezone=True), server_default=func.now())
updated_at = Column(DateTime(timezone=True), onupdate=func.now())
last_login_at = Column(DateTime(timezone=True))
# Relationships
contracts = relationship("Contract", back_populates="owner")
analyses = relationship("Analysis", back_populates="user")
api_keys = relationship("APIKey", back_populates="user")
__table_args__ = (
Index("ix_users_organization", "organization"),
)
class APIKey(Base):
"""API keys for programmatic access."""
__tablename__ = "api_keys"
id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
name = Column(String(128), nullable=False) # "Production Key", "Test Key"
key_hash = Column(String(256), nullable=False) # Hashed API key
key_prefix = Column(String(12), nullable=False) # First 8 chars for identification
# Permissions
scopes = Column(JSONB, default=list) # ["analyze", "contracts:read", "contracts:write"]
# Limits
rate_limit_per_minute = Column(Integer, default=60)
monthly_quota = Column(Integer, default=1000)
current_month_usage = Column(Integer, default=0)
# Status
is_active = Column(Boolean, default=True)
expires_at = Column(DateTime(timezone=True))
# Timestamps
created_at = Column(DateTime(timezone=True), server_default=func.now())
last_used_at = Column(DateTime(timezone=True))
# Relationships
user = relationship("User", back_populates="api_keys")
# ==================== CONTRACTS ====================
class Contract(Base):
"""Stored contract for tracking and analysis."""
__tablename__ = "contracts"
id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
owner_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
# Core Fields
name = Column(String(256), nullable=False)
description = Column(Text)
# Content
content_text = Column(Text) # Extracted text
content_hash = Column(String(64)) # SHA-256 of original file
original_filename = Column(String(256))
file_type = Column(String(32)) # pdf, docx, txt
# Legal Classification
jurisdiction = Column(String(64), default="INTERNATIONAL")
contract_type = Column(String(64)) # NDA, SaaS, Employment, etc.
governing_law = Column(String(128))
# Parties
parties = Column(JSONB, default=list) # [{"name": "...", "role": "buyer/seller"}]
# Dates
effective_date = Column(DateTime(timezone=True))
expiration_date = Column(DateTime(timezone=True))
# Metadata
tags = Column(JSONB, default=list)
custom_metadata = Column(JSONB, default=dict)
# Risk Tracking
latest_risk_score = Column(Integer)
risk_trend = Column(String(16)) # increasing, decreasing, stable
# Status
status = Column(String(32), default="active") # active, archived, expired
# Timestamps
created_at = Column(DateTime(timezone=True), server_default=func.now())
updated_at = Column(DateTime(timezone=True), onupdate=func.now())
# Relationships
owner = relationship("User", back_populates="contracts")
analyses = relationship("Analysis", back_populates="contract")
clauses = relationship("Clause", back_populates="contract")
__table_args__ = (
Index("ix_contracts_owner_status", "owner_id", "status"),
Index("ix_contracts_jurisdiction", "jurisdiction"),
)
class Clause(Base):
"""Individual clause extracted from a contract."""
__tablename__ = "clauses"
id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
contract_id = Column(UUID(as_uuid=False), ForeignKey("contracts.id"), nullable=False)
# Content
clause_number = Column(String(32)) # "5.2", "Article 12"
title = Column(String(256))
text = Column(Text, nullable=False)
# Classification
clause_type = Column(String(64)) # liability, termination, ip, force_majeure, etc.
# Analysis Cache
last_risk_score = Column(Integer)
last_analyzed_at = Column(DateTime(timezone=True))
# Timestamps
created_at = Column(DateTime(timezone=True), server_default=func.now())
# Relationships
contract = relationship("Contract", back_populates="clauses")
# ==================== ANALYSIS ====================
class Analysis(Base):
"""Record of a BALE analysis run."""
__tablename__ = "analyses"
id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
contract_id = Column(UUID(as_uuid=False), ForeignKey("contracts.id"), nullable=True)
# Input
input_text = Column(Text, nullable=False)
input_hash = Column(String(64))
jurisdiction = Column(String(64))
analysis_depth = Column(String(32)) # quick, standard, deep
# Configuration
inference_mode = Column(String(32)) # local, mistral
model_version = Column(String(64))
# Results
risk_score = Column(Integer)
verdict = Column(String(32)) # PLAINTIFF_FAVOR, DEFENSE_FAVOR, NEUTRAL
confidence = Column(Float)
interpretive_gap = Column(Integer)
# Explainability
decision_factors = Column(JSONB, default=list)
citations = Column(JSONB, default=list)
counterfactuals = Column(JSONB, default=list)
# Agent Outputs
civilist_output = Column(Text)
commonist_output = Column(Text)
synthesis_output = Column(Text)
harmonized_clause = Column(Text)
trial_transcript = Column(Text)
# Full Report (for debugging)
full_report = Column(JSONB)
# Performance
processing_time_ms = Column(Integer)
token_count = Column(Integer)
# Timestamps
created_at = Column(DateTime(timezone=True), server_default=func.now())
# Relationships
user = relationship("User", back_populates="analyses")
contract = relationship("Contract", back_populates="analyses")
__table_args__ = (
Index("ix_analyses_user_created", "user_id", "created_at"),
Index("ix_analyses_contract", "contract_id"),
)
# ==================== AUDIT LOG ====================
class AuditLog(Base):
"""Audit trail for compliance."""
__tablename__ = "audit_logs"
id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
# Actor
user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
api_key_id = Column(UUID(as_uuid=False), ForeignKey("api_keys.id"), nullable=True)
ip_address = Column(String(64))
user_agent = Column(String(256))
# Action
action = Column(String(64), nullable=False) # analyze, create_contract, delete, etc.
resource_type = Column(String(64)) # contract, analysis, user
resource_id = Column(UUID(as_uuid=False))
# Details
request_data = Column(JSONB) # Sanitized request body
response_status = Column(Integer)
error_message = Column(Text)
# Timestamp
created_at = Column(DateTime(timezone=True), server_default=func.now())
__table_args__ = (
Index("ix_audit_user_action", "user_id", "action"),
Index("ix_audit_created", "created_at"),
)
# ==================== TRAINING DATA ====================
class TrainingExample(Base):
"""Curated training examples for fine-tuning."""
__tablename__ = "training_examples"
id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
# Source
source_type = Column(String(64)) # user_feedback, expert_annotation, synthetic
source_id = Column(UUID(as_uuid=False)) # Link to analysis or contract
# Training Pair
input_text = Column(Text, nullable=False)
expected_output = Column(Text, nullable=False)
# Classification
task_type = Column(String(64)) # interpretation, risk_assessment, harmonization
domain = Column(String(64)) # commercial, ip, employment
difficulty = Column(String(32)) # easy, medium, hard
# Quality
is_validated = Column(Boolean, default=False)
validator_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
quality_score = Column(Float) # 0-1
# Usage
is_used_in_training = Column(Boolean, default=False)
training_run_id = Column(String(64))
# Timestamps
created_at = Column(DateTime(timezone=True), server_default=func.now())
validated_at = Column(DateTime(timezone=True))
__table_args__ = (
Index("ix_training_task_validated", "task_type", "is_validated"),
)
