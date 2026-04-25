from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint, CheckConstraint
from DB.ConfigDB import Base


class ContextDB(Base):

    __tablename__ = "TBL_CONTEXTS"

    ID_C = Column(Integer, primary_key=True, index=True)
    NAME_C = Column(String, unique=True, nullable=False)

    PARENT_ID_C = Column(Integer, ForeignKey("TBL_CONTEXTS.ID_C"), nullable=True)

    # relazione self-reference (albero)
    parent = relationship("ContextDB", remote_side=[ID_C])
    children = relationship("ContextDB", overlaps="parent")

    @property
    def id(self): return self.ID_C
    @property
    def name(self): return self.NAME_C
    @property
    def parent_id(self): return self.PARENT_ID_C

    def __repr__(self):
        return f"ContextDB(id={self.ID_C}, name='{self.NAME_C}', parent_id={self.PARENT_ID_C})"


class ObjectTypeDB(Base):  # Tabella dei tipi di oggetto

    __tablename__ = "TBL_OBJECT_TYPES"  # Nome tabella
    __table_args__ = (
        UniqueConstraint('NAME_OT', 'CONTEXT_ID_OT', name='unique_objecttype_per_context'),
        )
    
    ID_OT = Column(Integer, primary_key=True, index=True)
    NAME_OT = Column(String, index=True, nullable=False)

    CONTEXT_ID_OT = Column(Integer, ForeignKey("TBL_CONTEXTS.ID_C"), nullable=False)
    CONTEXT_NAME_OT = Column(String, nullable=False)

    DESCRIPTION_OT = Column(String, nullable=True)

    context = relationship("ContextDB")

    @property
    def id(self): return self.ID_OT
    @property
    def name(self): return self.NAME_OT
    @property
    def description(self): return self.DESCRIPTION_OT
    @property
    def context_id(self): return self.CONTEXT_ID_OT
    @property
    def context_name(self): return self.CONTEXT_NAME_OT

    def __repr__(self):  # Debug leggibile
        return f"ObjectTypeDB(id={self.ID_OT}, name='{self.NAME_OT}')"


class AlgorithmDB(Base):

    __tablename__ = "TBL_ALGORITHMS"
    __table_args__ = (
        UniqueConstraint('NAME_A', 'CONTEXT_ID_A', name='unique_algorithm_per_context'),
        CheckConstraint('COST_A >= 0', name='check_cost_non_negative'),
    )

    ID_A = Column(Integer, primary_key=True, index=True)
    NAME_A = Column(String, index=True, nullable=False)

    CONTEXT_ID_A = Column(Integer, ForeignKey("TBL_CONTEXTS.ID_C"), nullable=False)
    CONTEXT_NAME_A = Column(String, nullable=False)

    INPUT_TYPE_A = Column(String, nullable=False, index=True)
    OUTPUT_TYPE_A = Column(String, nullable=False, index=True)
    COST_A = Column(Float, nullable=False)

    context = relationship("ContextDB")

    @property
    def id(self):return self.ID_A
    @property
    def name(self):return self.NAME_A
    @property
    def input_type(self):return self.INPUT_TYPE_A
    @property
    def output_type(self):return self.OUTPUT_TYPE_A
    @property
    def cost(self):return self.COST_A
    @property
    def context_id(self): return self.CONTEXT_ID_A
    @property
    def context_name(self): return self.CONTEXT_NAME_A

    def __repr__(self):
        return (
            f"AlgorithmDB(id={self.id}, name='{self.NAME_A}', "
            f"input='{self.INPUT_TYPE_A}', "
            f"output='{self.OUTPUT_TYPE_A}', "
            f"cost={self.COST_A})"
        )


class PipelineDB(Base):  # Tabella pipeline

    __tablename__ = "TBL_PIPELINES"  # Nome tabella

    ID_P = Column(Integer, primary_key=True, index=True)
    PIPELINE_NAME = Column(String, nullable=True)

    CONTEXT_ID_P = Column(Integer, ForeignKey("TBL_CONTEXTS.ID_C"), nullable=False)
    CONTEXT_NAME_P = Column(String, nullable=False)

    START_TYPE_ID_P = Column(Integer, ForeignKey("TBL_OBJECT_TYPES.ID_OT"), nullable=False)
    END_TYPE_ID_P = Column(Integer, ForeignKey("TBL_OBJECT_TYPES.ID_OT"), nullable=False)

    TOTAL_COST_P = Column(Float, nullable=False, default=0.0)

    context = relationship("ContextDB")

    @property
    def id(self): return self.ID_P
    @property
    def name(self): return self.PIPELINE_NAME
    @property
    def start_type(self): return self.START_TYPE_ID_P
    @property
    def end_type(self): return self.END_TYPE_ID_P
    @property
    def total_cost(self): return self.TOTAL_COST_P
    @property
    def context_id(self): return self.CONTEXT_ID_P
    @property
    def context_name(self): return self.CONTEXT_NAME_P

    start_type = relationship("ObjectTypeDB", foreign_keys=[START_TYPE_ID_P])  # Relazione start
    end_type = relationship("ObjectTypeDB", foreign_keys=[END_TYPE_ID_P])  # Relazione end

    steps = relationship(  # Relazione step pipeline
        "PipelineStepDB",
        back_populates="pipeline",
        cascade="all, delete-orphan",
        order_by="PipelineStepDB.ID_STEP"  # Mantiene ordine corretto
    )

    def __repr__(self):  # Debug leggibile
        return f"PipelineDB(id={self.ID_P}, start={self.START_TYPE_ID_P}, end={self.END_TYPE_ID_P}, cost={self.TOTAL_COST_P})"


class PipelineStepDB(Base):

    __tablename__ = "TBL_STEPS_PIPELINE"

    __table_args__ = (
        UniqueConstraint('PIPELINE_ID', 'ID_STEP', name='unique_step_order_per_pipeline'),
    )

    ID_SP = Column(Integer, primary_key=True, index=True)
    PIPELINE_ID = Column(Integer, ForeignKey("TBL_PIPELINES.ID_P"), nullable=False, index=True)
    PIPELINE_NAME = Column(String, nullable=False)
    ID_STEP = Column(Integer, nullable=False)
    ALGORITHM_ID = Column(Integer, ForeignKey("TBL_ALGORITHMS.ID_A"), nullable=False)

    pipeline = relationship("PipelineDB", back_populates="steps")
    algorithm = relationship("AlgorithmDB")