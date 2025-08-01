import uuid
from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlmodel import Session, SQLModel, select

from app.models.base import InDBBase

ModelType = TypeVar("ModelType", bound=InDBBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(
        self,
        model: type[ModelType],
    ):
        """
        CRUD object with default methods to Create, Read, Update, Delete
        (CRUD).

        **Parameters**

        * `model`: A SQLModel model class
        """
        self.model = model

    def get(
        self,
        session: Session,
        *,
        id: uuid.UUID,
    ) -> ModelType | None:
        """Get a single record by id"""
        statement = select(self.model).where(self.model.id == id)
        result = session.exec(statement)
        return result.one_or_none()

    def get_multi(
        self,
        session: Session,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ModelType]:
        """Get multiple records with pagination"""
        statement = select(self.model).offset(skip).limit(limit)
        result = session.exec(statement)
        return result.all()

    def create(
        self,
        session: Session,
        *,
        obj_in: CreateSchemaType,
        owner_id: uuid.UUID | None = None,
    ) -> ModelType:
        """Create new record with optional owner_id"""
        obj_data = obj_in.model_dump()
        if owner_id is not None:
            obj_data["owner_id"] = owner_id
        db_obj = self.model(**obj_data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update(
        self,
        session: Session,
        *,
        id: uuid.UUID,
        obj_in: UpdateSchemaType,
    ) -> ModelType | None:
        """Update existing record"""
        db_obj = self.get(session, id=id)
        if db_obj:
            update_data = obj_in.model_dump(exclude_unset=True)
            db_obj.sqlmodel_update(update_data)

            session.add(db_obj)
            session.commit()
            session.refresh(db_obj)
        return db_obj

    def remove(
        self,
        session: Session,
        *,
        id: uuid.UUID,
    ) -> ModelType | None:
        """Remove a record"""
        obj = self.get(session, id=id)
        if obj:
            session.delete(obj)
            session.commit()
        return obj
