"""
Controller para operações de autenticação.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user, login_required

from ..repositories.user_repository import UserRepository
from ..forms import LoginForm, RegisterForm
from ..core.exceptions import ValidationError, AuthenticationError
import chatcine.extensions as ext


class AuthController:
    """Controller para gerenciar autenticação."""
    
    def __init__(self):
        """Inicializa o controller."""
        self.user_repo = UserRepository()
        self.blueprint = Blueprint('auth', __name__)
        self._register_routes()
    
    def _register_routes(self):
        """Registra as rotas do controller."""
        self.blueprint.route('/login', methods=['GET', 'POST'])(self.login)
        self.blueprint.route('/register', methods=['POST'])(self.register)
        self.blueprint.route('/login/google', methods=['GET'])(self.login_google)
        self.blueprint.route('/authorize', methods=['GET'])(self.authorize)
        self.blueprint.route('/logout', methods=['GET'])(self.logout)
    
    def login(self):
        """Rota de login."""
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        
        form = LoginForm()
        
        if form.validate_on_submit():
            email = form.email.data.strip().lower()
            password = form.password.data
            
            user = self.user_repo.get_by_email(email)
            
            if user and user.check_password(password):
                login_user(user, remember=True)
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('main.index'))
            else:
                flash('Email ou senha inválidos.', 'error')
        
        return render_template('login.html', form=form)
    
    def register(self):
        """Rota de registro."""
        form = RegisterForm()
        
        if form.validate_on_submit():
            email = form.email.data.strip().lower()
            password = form.password.data
            
            try:
                user = self.user_repo.create_user(email=email, password=password)
                login_user(user, remember=True)
                flash('Conta criada com sucesso! Bem-vindo(a)!', 'success')
                return redirect(url_for('main.index'))
            except Exception as e:
                flash('Erro ao criar conta. Tente novamente.', 'error')
        
        if form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(error, 'error')
        
        return redirect(url_for('auth.login'))
    
    def login_google(self):
        """Inicia login com Google."""
        if not ext.google_oauth:
            flash('Login com Google não está configurado.', 'error')
            return redirect(url_for('auth.login'))
        
        redirect_uri = url_for('auth.authorize', _external=True)
        return ext.google_oauth.authorize_redirect(redirect_uri)
    
    def authorize(self):
        """Callback do Google OAuth."""
        if not ext.google_oauth:
            flash('Login com Google não está configurado.', 'error')
            return redirect(url_for('auth.login'))
        
        try:
            token = ext.google_oauth.authorize_access_token()
            user_info = ext.google_oauth.parse_id_token(token, nonce=session.get('nonce'))
        except Exception as e:
            flash(f"Erro na autenticação com o Google: {str(e)}", "error")
            return redirect(url_for('auth.login'))
        
        email = user_info.get('email', '').lower()
        profile_pic = user_info.get('picture')
        
        if not email:
            flash('Não foi possível obter o email do Google.', 'error')
            return redirect(url_for('auth.login'))
        
        user = self.user_repo.get_by_email(email)
        
        if not user:
            try:
                user = self.user_repo.create_user(email=email, profile_pic_url=profile_pic)
            except Exception as e:
                flash('Erro ao criar conta com Google.', 'error')
                return redirect(url_for('auth.login'))
        else:
            if profile_pic and user.profile_pic_url != profile_pic:
                self.user_repo.update(user, profile_pic_url=profile_pic)
        
        login_user(user, remember=True)
        flash('Login com Google realizado com sucesso!', 'success')
        return redirect(url_for('main.index'))
    
    @login_required
    def logout(self):
        """Rota de logout."""
        logout_user()
        session.clear()
        flash('Você saiu da sua conta.', 'info')
        return redirect(url_for('auth.login'))


# Cria instância do controller
auth_controller = AuthController()
auth_bp = auth_controller.blueprint

