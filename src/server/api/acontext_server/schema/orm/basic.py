from datetime import datetime
from typing import List, Optional
from sqlalchemy import DateTime, String, Integer, ForeignKey, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
)
from sqlalchemy.sql import func
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.alias_generators import to_camel


class Base(DeclarativeBase):
    """Base class for all ORM models with Pydantic integration"""

    # Pydantic configuration for all models
    __pydantic_config__ = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
        validate_default=True,
    )


class TimestampMixin:
    """Mixin class for common timestamp fields"""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Project(Base, TimestampMixin):
    """Project model - top level entity with Pydantic validation"""

    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Relationships
    spaces: Mapped[List["Space"]] = relationship(
        "Space", back_populates="project", cascade="all, delete-orphan", lazy="select"
    )

    # Pydantic model for runtime validation
    class __pydantic_model__(BaseModel):
        model_config = ConfigDict(
            from_attributes=True,
            validate_assignment=True,
            str_strip_whitespace=True,
        )

        id: Optional[int] = Field(None, ge=1, description="Unique project identifier")
        name: str = Field(..., min_length=1, max_length=255, description="Project name")
        description: Optional[str] = Field(
            None, max_length=1000, description="Project description"
        )
        created_at: Optional[datetime] = Field(None, description="Creation timestamp")
        last_updated_at: Optional[datetime] = Field(
            None, description="Last update timestamp"
        )

        @field_validator("name")
        @classmethod
        def validate_name(cls, v: str) -> str:
            if not v or not v.strip():
                raise ValueError("Project name cannot be empty or whitespace only")
            return v.strip()

        @field_validator("description")
        @classmethod
        def validate_description(cls, v: Optional[str]) -> Optional[str]:
            if v is not None and len(v.strip()) == 0:
                return None  # Convert empty string to None
            return v.strip() if v else None

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}')>"

    def validate(self) -> "Project.__pydantic_model__":
        """Validate current instance using Pydantic model"""
        return self.__pydantic_model__.model_validate(self)


class Space(Base, TimestampMixin):
    """Space model - belongs to a project with Pydantic validation"""

    __tablename__ = "spaces"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="spaces")
    sessions: Mapped[List["Session"]] = relationship(
        "Session", back_populates="space", cascade="all, delete-orphan", lazy="select"
    )

    # Pydantic model for runtime validation
    class __pydantic_model__(BaseModel):
        model_config = ConfigDict(
            from_attributes=True,
            validate_assignment=True,
            str_strip_whitespace=True,
        )

        id: Optional[int] = Field(None, ge=1, description="Unique space identifier")
        name: str = Field(..., min_length=1, max_length=255, description="Space name")
        description: Optional[str] = Field(
            None, max_length=1000, description="Space description"
        )
        project_id: int = Field(..., ge=1, description="Parent project ID")
        created_at: Optional[datetime] = Field(None, description="Creation timestamp")
        last_updated_at: Optional[datetime] = Field(
            None, description="Last update timestamp"
        )

        @field_validator("name")
        @classmethod
        def validate_name(cls, v: str) -> str:
            if not v or not v.strip():
                raise ValueError("Space name cannot be empty or whitespace only")
            return v.strip()

        @field_validator("description")
        @classmethod
        def validate_description(cls, v: Optional[str]) -> Optional[str]:
            if v is not None and len(v.strip()) == 0:
                return None
            return v.strip() if v else None

    def __repr__(self) -> str:
        return (
            f"<Space(id={self.id}, name='{self.name}', project_id={self.project_id})>"
        )

    def validate(self) -> "Space.__pydantic_model__":
        """Validate current instance using Pydantic model"""
        return self.__pydantic_model__.model_validate(self)


class Session(Base, TimestampMixin):
    """Session model - belongs to a space with Pydantic validation"""

    __tablename__ = "sessions"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    space_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("spaces.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    space: Mapped["Space"] = relationship("Space", back_populates="sessions")

    # Pydantic model for runtime validation
    class __pydantic_model__(BaseModel):
        model_config = ConfigDict(
            from_attributes=True,
            validate_assignment=True,
            str_strip_whitespace=True,
        )

        id: Optional[int] = Field(None, ge=1, description="Unique session identifier")
        name: str = Field(..., min_length=1, max_length=255, description="Session name")
        description: Optional[str] = Field(
            None, max_length=1000, description="Session description"
        )
        space_id: int = Field(..., ge=1, description="Parent space ID")
        created_at: Optional[datetime] = Field(None, description="Creation timestamp")
        last_updated_at: Optional[datetime] = Field(
            None, description="Last update timestamp"
        )

        @field_validator("name")
        @classmethod
        def validate_name(cls, v: str) -> str:
            if not v or not v.strip():
                raise ValueError("Session name cannot be empty or whitespace only")
            return v.strip()

        @field_validator("description")
        @classmethod
        def validate_description(cls, v: Optional[str]) -> Optional[str]:
            if v is not None and len(v.strip()) == 0:
                return None
            return v.strip() if v else None

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, name='{self.name}', space_id={self.space_id})>"

    def validate(self) -> "Session.__pydantic_model__":
        """Validate current instance using Pydantic model"""
        return self.__pydantic_model__.model_validate(self)


# Database utility functions
def create_database_engine(database_url: str):
    """Create SQLAlchemy engine with recommended settings"""
    return create_engine(
        database_url,
        echo=False,  # Set to True for SQL debugging
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=3600,  # Recycle connections after 1 hour
    )


def create_session_factory(engine):
    """Create session factory for database operations"""
    return sessionmaker(
        bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
    )


def create_tables(engine):
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)


def drop_tables(engine):
    """Drop all tables from the database"""
    Base.metadata.drop_all(bind=engine)


# Runtime validation utilities
def validate_model_data(model_instance, raise_on_error: bool = True):
    """
    Validate SQLAlchemy model instance using its embedded Pydantic model

    Args:
        model_instance: SQLAlchemy model instance
        raise_on_error: Whether to raise exception on validation error

    Returns:
        Tuple of (is_valid: bool, validation_result_or_error)
    """
    try:
        pydantic_instance = model_instance.validate()
        return True, pydantic_instance
    except Exception as e:
        if raise_on_error:
            raise
        return False, e


# Example usage and testing
if __name__ == "__main__":
    # Test runtime validation
    try:
        # Create a project instance
        project = Project()
        project.name = "Test Project"
        project.description = "A test project"
        project.id = 1

        # Validate at runtime
        print("Validating project...")
        is_valid, result = validate_model_data(project, raise_on_error=False)
        if is_valid:
            print(f"✅ Project validation passed: {result}")
        else:
            print(f"❌ Project validation failed: {result}")

        # Test invalid data
        print("\nTesting invalid project...")
        invalid_project = Project()
        invalid_project.name = ""  # Invalid: empty name
        invalid_project.id = 1

        is_valid, result = validate_model_data(invalid_project, raise_on_error=False)
        if not is_valid:
            print(f"❌ Expected validation failure: {result}")

        # Test space validation
        print("\nValidating space...")
        space = Space()
        space.name = "Test Space"
        space.project_id = 1
        space.id = 1

        is_valid, result = validate_model_data(space, raise_on_error=False)
        if is_valid:
            print(f"✅ Space validation passed: {result}")

    except Exception as e:
        print(f"Error during validation: {e}")
