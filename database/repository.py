"""
BALE Database Repository
Data access layer with repository pattern for clean separation.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

from database.models import (
    User, Contract, Clause, Analysis, AuditLog, APIKey, TrainingExample
)


# ==================== USER REPOSITORY ====================

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def create(self, email: str, full_name: str = None, organization: str = None) -> User:
        user = User(
            email=email,
            full_name=full_name,
            organization=organization
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_last_login(self, user_id: str) -> None:
        self.db.query(User).filter(User.id == user_id).update({
            "last_login_at": datetime.utcnow()
        })
        self.db.commit()


# ==================== CONTRACT REPOSITORY ====================

class ContractRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, contract_id: str) -> Optional[Contract]:
        return self.db.query(Contract).filter(Contract.id == contract_id).first()
    
    def get_by_owner(
        self, 
        owner_id: str, 
        status: str = None,
        jurisdiction: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Contract]:
        query = self.db.query(Contract).filter(Contract.owner_id == owner_id)
        
        if status:
            query = query.filter(Contract.status == status)
        if jurisdiction:
            query = query.filter(Contract.jurisdiction == jurisdiction)
        
        return query.order_by(desc(Contract.created_at)).limit(limit).offset(offset).all()
    
    def count_by_owner(self, owner_id: str, status: str = None) -> int:
        query = self.db.query(Contract).filter(Contract.owner_id == owner_id)
        if status:
            query = query.filter(Contract.status == status)
        return query.count()
    
    def create(
        self,
        owner_id: str,
        name: str,
        content_text: str = None,
        jurisdiction: str = "INTERNATIONAL",
        **kwargs
    ) -> Contract:
        contract = Contract(
            owner_id=owner_id,
            name=name,
            content_text=content_text,
            jurisdiction=jurisdiction,
            **kwargs
        )
        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)
        return contract
    
    def update(self, contract_id: str, **updates) -> Optional[Contract]:
        contract = self.get_by_id(contract_id)
        if not contract:
            return None
        
        for key, value in updates.items():
            if hasattr(contract, key):
                setattr(contract, key, value)
        
        contract.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(contract)
        return contract
    
    def update_risk(self, contract_id: str, risk_score: int) -> None:
        contract = self.get_by_id(contract_id)
        if contract:
            old_risk = contract.latest_risk_score
            contract.latest_risk_score = risk_score
            
            # Calculate trend
            if old_risk is not None:
                if risk_score > old_risk + 5:
                    contract.risk_trend = "increasing"
                elif risk_score < old_risk - 5:
                    contract.risk_trend = "decreasing"
                else:
                    contract.risk_trend = "stable"
            
            self.db.commit()
    
    def delete(self, contract_id: str) -> bool:
        contract = self.get_by_id(contract_id)
        if contract:
            self.db.delete(contract)
            self.db.commit()
            return True
        return False
    
    def archive(self, contract_id: str) -> Optional[Contract]:
        return self.update(contract_id, status="archived")


# ==================== ANALYSIS REPOSITORY ====================

class AnalysisRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, analysis_id: str) -> Optional[Analysis]:
        return self.db.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    def get_by_user(
        self, 
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Analysis]:
        return (
            self.db.query(Analysis)
            .filter(Analysis.user_id == user_id)
            .order_by(desc(Analysis.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    def get_by_contract(self, contract_id: str) -> List[Analysis]:
        return (
            self.db.query(Analysis)
            .filter(Analysis.contract_id == contract_id)
            .order_by(desc(Analysis.created_at))
            .all()
        )
    
    def create(
        self,
        user_id: str,
        input_text: str,
        risk_score: int,
        verdict: str,
        contract_id: str = None,
        **kwargs
    ) -> Analysis:
        analysis = Analysis(
            user_id=user_id,
            contract_id=contract_id,
            input_text=input_text,
            risk_score=risk_score,
            verdict=verdict,
            **kwargs
        )
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis
    
    def get_stats(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get analysis statistics for a user."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        analyses = (
            self.db.query(Analysis)
            .filter(Analysis.user_id == user_id)
            .filter(Analysis.created_at >= cutoff)
            .all()
        )
        
        if not analyses:
            return {"count": 0, "avg_risk": 0, "avg_processing_ms": 0}
        
        risks = [a.risk_score for a in analyses if a.risk_score is not None]
        times = [a.processing_time_ms for a in analyses if a.processing_time_ms is not None]
        
        return {
            "count": len(analyses),
            "avg_risk": sum(risks) / len(risks) if risks else 0,
            "avg_processing_ms": sum(times) / len(times) if times else 0,
            "plaintiff_favor_count": sum(1 for a in analyses if a.verdict == "PLAINTIFF_FAVOR"),
            "defense_favor_count": sum(1 for a in analyses if a.verdict == "DEFENSE_FAVOR")
        }


# ==================== AUDIT REPOSITORY ====================

class AuditRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def log(
        self,
        action: str,
        user_id: str = None,
        api_key_id: str = None,
        resource_type: str = None,
        resource_id: str = None,
        request_data: Dict = None,
        response_status: int = None,
        ip_address: str = None,
        user_agent: str = None,
        error_message: str = None
    ) -> AuditLog:
        log = AuditLog(
            user_id=user_id,
            api_key_id=api_key_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            request_data=request_data,
            response_status=response_status,
            ip_address=ip_address,
            user_agent=user_agent,
            error_message=error_message
        )
        self.db.add(log)
        self.db.commit()
        return log
    
    def get_by_user(
        self, 
        user_id: str, 
        action: str = None,
        limit: int = 100
    ) -> List[AuditLog]:
        query = self.db.query(AuditLog).filter(AuditLog.user_id == user_id)
        if action:
            query = query.filter(AuditLog.action == action)
        return query.order_by(desc(AuditLog.created_at)).limit(limit).all()


# ==================== TRAINING DATA REPOSITORY ====================

class TrainingDataRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(
        self,
        input_text: str,
        expected_output: str,
        source_type: str = "synthetic",
        task_type: str = "interpretation",
        domain: str = "commercial",
        difficulty: str = "medium"
    ) -> TrainingExample:
        example = TrainingExample(
            input_text=input_text,
            expected_output=expected_output,
            source_type=source_type,
            task_type=task_type,
            domain=domain,
            difficulty=difficulty
        )
        self.db.add(example)
        self.db.commit()
        self.db.refresh(example)
        return example
    
    def get_for_training(
        self, 
        task_type: str = None,
        validated_only: bool = True,
        limit: int = 10000
    ) -> List[TrainingExample]:
        query = self.db.query(TrainingExample)
        
        if validated_only:
            query = query.filter(TrainingExample.is_validated == True)
        if task_type:
            query = query.filter(TrainingExample.task_type == task_type)
        
        return query.filter(TrainingExample.is_used_in_training == False).limit(limit).all()
    
    def mark_used(self, example_ids: List[str], training_run_id: str) -> None:
        self.db.query(TrainingExample).filter(
            TrainingExample.id.in_(example_ids)
        ).update({
            "is_used_in_training": True,
            "training_run_id": training_run_id
        }, synchronize_session=False)
        self.db.commit()
    
    def validate(self, example_id: str, validator_id: str, quality_score: float) -> None:
        self.db.query(TrainingExample).filter(
            TrainingExample.id == example_id
        ).update({
            "is_validated": True,
            "validator_id": validator_id,
            "quality_score": quality_score,
            "validated_at": datetime.utcnow()
        })
        self.db.commit()
    
    def get_stats(self) -> Dict[str, Any]:
        total = self.db.query(TrainingExample).count()
        validated = self.db.query(TrainingExample).filter(
            TrainingExample.is_validated == True
        ).count()
        used = self.db.query(TrainingExample).filter(
            TrainingExample.is_used_in_training == True
        ).count()
        
        return {
            "total": total,
            "validated": validated,
            "used_in_training": used,
            "pending_validation": total - validated
        }
