from sqlalchemy import Column, Integer, String, Float, DateTime
import datetime
from database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    username = Column(String, index=True)
    dataset_name = Column(String)
    target_variable = Column(String)
    protected_attribute = Column(String)
    disparate_impact = Column(Float)
    demographic_parity_diff = Column(Float)
    audit_narrative = Column(String)
