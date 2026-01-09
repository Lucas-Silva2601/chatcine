"""
Formulários usando Flask-WTF.
Define os formulários de autenticação e validação de dados.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from .models import User


class LoginForm(FlaskForm):
    """Formulário de login."""
    email = StringField(
        'Email',
        validators=[
            DataRequired(message='O email é obrigatório.'),
            Email(message='Por favor, insira um email válido.')
        ],
        render_kw={'placeholder': 'seu@email.com', 'autocomplete': 'email'}
    )
    password = PasswordField(
        'Senha',
        validators=[
            DataRequired(message='A senha é obrigatória.'),
            Length(min=6, message='A senha deve ter pelo menos 6 caracteres.')
        ],
        render_kw={'placeholder': '••••••', 'autocomplete': 'current-password'}
    )
    submit = SubmitField('Entrar')


class RegisterForm(FlaskForm):
    """Formulário de registro."""
    email = StringField(
        'Email',
        validators=[
            DataRequired(message='O email é obrigatório.'),
            Email(message='Por favor, insira um email válido.')
        ],
        render_kw={'placeholder': 'seu@email.com', 'autocomplete': 'email'}
    )
    password = PasswordField(
        'Senha',
        validators=[
            DataRequired(message='A senha é obrigatória.'),
            Length(min=6, message='A senha deve ter pelo menos 6 caracteres.')
        ],
        render_kw={'placeholder': 'Mínimo 6 caracteres', 'autocomplete': 'new-password'}
    )
    submit = SubmitField('Registrar')
    
    def validate_email(self, field):
        """Valida se o email já está em uso."""
        if User.query.filter_by(email=field.data.lower().strip()).first():
            raise ValidationError('Este email já está registrado. Tente fazer login.')



