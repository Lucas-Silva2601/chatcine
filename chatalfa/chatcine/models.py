"""
Modelos de dados usando SQLAlchemy.
Define a estrutura do banco de dados.
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db


class User(UserMixin, db.Model):
    """Modelo de usuário."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)
    profile_pic_url = db.Column(db.String(500), nullable=True)
    plan_status = db.Column(db.String(50), default='free', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    chat_sessions = db.relationship('ChatSession', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, email: str, password: str = None, profile_pic_url: str = None, plan_status: str = 'free'):
        """Inicializa um novo usuário."""
        self.email = email
        if password:
            self.password_hash = generate_password_hash(password)
        self.profile_pic_url = profile_pic_url or self._generate_default_avatar()
        self.plan_status = plan_status
    
    def _generate_default_avatar(self) -> str:
        """Gera URL de avatar padrão baseado no email."""
        username = self.email.split('@')[0]
        return f"https://ui-avatars.com/api/?name={username}&background=random"
    
    def set_password(self, password: str) -> None:
        """Define a senha do usuário."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Verifica se a senha está correta."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def get_id(self) -> str:
        """Retorna o ID do usuário como string (requerido pelo Flask-Login)."""
        return str(self.id)
    
    def __repr__(self) -> str:
        return f'<User {self.email}>'


class ChatSession(db.Model):
    """Modelo de sessão de chat."""
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)  # Nullable para sessões anônimas
    session_key = db.Column(db.String(255), nullable=True, unique=True, index=True)  # Chave única para sessões anônimas
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade='all, delete-orphan', order_by='ChatMessage.created_at')
    
    def __repr__(self) -> str:
        return f'<ChatSession {self.id} - User {self.user_id or "Anonymous"}>'


class ChatMessage(db.Model):
    """Modelo de mensagem do chat."""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False)  # 'user' ou 'assistant'
    content = db.Column(db.Text, nullable=False)  # JSON string para mensagens da IA
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f'<ChatMessage {self.id} - {self.role}>'
