"""
Rotas de autenticação.
Gerencia login, registro, logout e OAuth do Google.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy.exc import IntegrityError

from ..models import User
from ..extensions import db
from ..forms import LoginForm, RegisterForm
import chatcine.extensions as ext

# Cria um Blueprint chamado 'auth'
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rota para a página de login e para processar o formulário de login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data
        
        # Busca usuário no banco de dados
        user = User.query.filter_by(email=email).first()
        
        # Verifica se o usuário existe e se a senha está correta
        if user and user.check_password(password):
            login_user(user, remember=True)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Email ou senha inválidos.', 'error')
    
    return render_template('login.html', form=form)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Rota para processar o formulário de registro."""
    form = RegisterForm()
    
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data
        
        try:
            # Cria novo usuário
            user = User(email=email, password=password)
            db.session.add(user)
            db.session.commit()
            
            # Faz login automaticamente
            login_user(user, remember=True)
            flash('Conta criada com sucesso! Bem-vindo(a)!', 'success')
            return redirect(url_for('main.index'))
        
        except IntegrityError:
            db.session.rollback()
            flash('Erro ao criar conta. Tente novamente.', 'error')
        except Exception as e:
            db.session.rollback()
            flash('Ocorreu um erro inesperado. Tente novamente.', 'error')
    
    # Se houver erros de validação, redireciona para login
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'error')
    
    return redirect(url_for('auth.login'))


@auth_bp.route('/login/google')
def login_google():
    """Rota que inicia o fluxo de login com o Google."""
    if not ext.google_oauth:
        flash('Login com Google não está configurado.', 'error')
        return redirect(url_for('auth.login'))
    
    redirect_uri = url_for('auth.authorize', _external=True)
    return ext.google_oauth.authorize_redirect(redirect_uri)


@auth_bp.route('/authorize')
def authorize():
    """Rota de callback que o Google chama após o usuário autorizar."""
    if not ext.google_oauth:
        flash('Login com Google não está configurado.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        # Pega o token de acesso do Google
        token = ext.google_oauth.authorize_access_token()
        # Usa o token para obter as informações do usuário
        user_info = ext.google_oauth.parse_id_token(token, nonce=session.get('nonce'))
    except Exception as e:
        flash(f"Erro na autenticação com o Google: {str(e)}", "error")
        return redirect(url_for('auth.login'))
    
    email = user_info.get('email', '').lower()
    profile_pic = user_info.get('picture')
    
    if not email:
        flash('Não foi possível obter o email do Google.', 'error')
        return redirect(url_for('auth.login'))
    
    # Busca ou cria usuário
    user = User.query.filter_by(email=email).first()
    
    if not user:
        # Cria novo usuário do Google
        try:
            user = User(email=email, profile_pic_url=profile_pic)
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            user = User.query.filter_by(email=email).first()
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar conta com Google.', 'error')
            return redirect(url_for('auth.login'))
    else:
        # Atualiza foto de perfil se necessário
        if profile_pic and user.profile_pic_url != profile_pic:
            user.profile_pic_url = profile_pic
            db.session.commit()
    
    login_user(user, remember=True)
    flash('Login com Google realizado com sucesso!', 'success')
    return redirect(url_for('main.index'))


@auth_bp.route('/logout')
@login_required
def logout():
    """Rota para deslogar o usuário."""
    logout_user()
    session.clear()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('auth.login'))
