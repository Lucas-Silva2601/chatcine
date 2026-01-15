"""
Repository base com operações comuns.
"""
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from extensions import db
from core.exceptions import DatabaseError

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Repository base com operações CRUD comuns."""
    
    def __init__(self, model: Type[T], session: Session = None):
        """
        Inicializa o repository.
        
        Args:
            model: Classe do modelo SQLAlchemy
            session: Sessão do banco (usa db.session se None)
        """
        self.model = model
        self.session = session or db.session
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Busca um registro por ID."""
        try:
            return self.session.query(self.model).get(id)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Erro ao buscar {self.model.__name__} por ID: {str(e)}")
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """Busca todos os registros."""
        try:
            query = self.session.query(self.model)
            if limit:
                query = query.limit(limit).offset(offset)
            return query.all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Erro ao buscar {self.model.__name__}: {str(e)}")
    
    def create(self, **kwargs) -> T:
        """Cria um novo registro."""
        try:
            instance = self.model(**kwargs)
            self.session.add(instance)
            self.session.commit()
            return instance
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError(f"Erro ao criar {self.model.__name__}: {str(e)}")
    
    def update(self, instance: T, **kwargs) -> T:
        """Atualiza um registro existente."""
        try:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            self.session.commit()
            return instance
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError(f"Erro ao atualizar {self.model.__name__}: {str(e)}")
    
    def delete(self, instance: T) -> None:
        """Deleta um registro."""
        try:
            self.session.delete(instance)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise DatabaseError(f"Erro ao deletar {self.model.__name__}: {str(e)}")
    
    def filter_by(self, **kwargs) -> List[T]:
        """Filtra registros por critérios."""
        try:
            return self.session.query(self.model).filter_by(**kwargs).all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Erro ao filtrar {self.model.__name__}: {str(e)}")
    
    def first(self, **kwargs) -> Optional[T]:
        """Retorna o primeiro registro que corresponde aos critérios."""
        try:
            return self.session.query(self.model).filter_by(**kwargs).first()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Erro ao buscar {self.model.__name__}: {str(e)}")

