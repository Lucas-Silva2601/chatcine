# 🤝 Guia de Contribuição

Obrigado por considerar contribuir com o ChatCine! Este documento fornece diretrizes para contribuir com o projeto.

## 📋 Código de Conduta

- Seja respeitoso e inclusivo
- Aceite críticas construtivas
- Foque no que é melhor para a comunidade
- Mostre empatia com outros membros da comunidade

## 🚀 Como Contribuir

### 1. Reportar Bugs

Antes de reportar um bug:
- Verifique se já não existe uma issue sobre o problema
- Certifique-se de estar usando a versão mais recente
- Colete informações sobre o ambiente (SO, versão do Python, etc.)

Ao reportar um bug, inclua:
- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs. comportamento atual
- Screenshots (se aplicável)
- Informações do ambiente

### 2. Sugerir Melhorias

Para sugerir uma melhoria:
- Abra uma issue com o prefixo `[FEATURE]`
- Descreva claramente a funcionalidade desejada
- Explique por que seria útil
- Forneça exemplos de uso, se possível

### 3. Contribuir com Código

#### Setup do Ambiente de Desenvolvimento

```bash
# 1. Fork o repositório no GitHub

# 2. Clone seu fork
git clone https://github.com/seu-usuario/chatcine.git
cd chatcine

# 3. Adicione o repositório original como upstream
git remote add upstream https://github.com/original-usuario/chatcine.git

# 4. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows

# 5. Instale as dependências
pip install -r requirements.txt

# 6. Configure o .env
cp .env.example .env
# Edite o .env com suas credenciais

# 7. Inicialize o banco de dados
python init_db.py
```

#### Fluxo de Trabalho

1. **Crie uma branch para sua feature**
```bash
git checkout -b feature/nome-da-feature
# ou
git checkout -b fix/nome-do-bug
```

2. **Faça suas alterações**
- Escreva código limpo e bem documentado
- Siga as convenções de código do projeto
- Adicione testes para novas funcionalidades
- Atualize a documentação se necessário

3. **Execute os testes**
```bash
# Testes
pytest

# Cobertura
pytest --cov=chatcine --cov-report=html

# Linting
flake8 chatcine

# Formatação
black chatcine

# Type checking
mypy chatcine
```

4. **Commit suas alterações**
```bash
git add .
git commit -m "feat: adiciona nova funcionalidade X"
```

**Convenção de Commits:**
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Mudanças na documentação
- `style:` Formatação, ponto e vírgula, etc.
- `refactor:` Refatoração de código
- `test:` Adição ou correção de testes
- `chore:` Tarefas de manutenção

5. **Push para seu fork**
```bash
git push origin feature/nome-da-feature
```

6. **Abra um Pull Request**
- Vá para o repositório original no GitHub
- Clique em "New Pull Request"
- Selecione sua branch
- Preencha o template do PR

## 📝 Padrões de Código

### Python

- **PEP 8**: Siga as diretrizes do PEP 8
- **Type Hints**: Use type hints sempre que possível
- **Docstrings**: Documente funções e classes
- **Linha máxima**: 100 caracteres
- **Imports**: Organize imports (stdlib, third-party, local)

Exemplo:
```python
from typing import Optional, List
from flask import Blueprint, request, jsonify
from ..models import User
from ..services import UserService


def create_user(email: str, password: str) -> Optional[User]:
    """
    Cria um novo usuário no sistema.
    
    Args:
        email: Email do usuário
        password: Senha do usuário
        
    Returns:
        Objeto User se criado com sucesso, None caso contrário
        
    Raises:
        ValueError: Se o email já estiver em uso
    """
    # Implementação...
    pass
```

### Estrutura de Arquivos

```
chatcine/
├── controllers/      # Rotas e lógica HTTP
├── services/         # Lógica de negócio
├── repositories/     # Acesso a dados
├── dto/              # Data Transfer Objects
├── core/             # Funcionalidades centrais
├── utils/            # Utilitários
├── models.py         # Modelos do banco
├── schemas.py        # Schemas de validação
└── config.py         # Configurações
```

### Testes

- Escreva testes para novas funcionalidades
- Mantenha cobertura acima de 80%
- Use fixtures do pytest
- Nomeie testes descritivamente

Exemplo:
```python
def test_create_user_with_valid_data(client, db):
    """Testa criação de usuário com dados válidos."""
    response = client.post('/auth/register', data={
        'email': 'test@example.com',
        'password': 'SecurePass123'
    })
    assert response.status_code == 201
    assert User.query.filter_by(email='test@example.com').first() is not None
```

## 🔍 Revisão de Código

Todos os PRs passarão por revisão. Esteja preparado para:
- Responder a comentários
- Fazer ajustes solicitados
- Explicar suas decisões de design

## 📚 Recursos Úteis

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [PEP 8 Style Guide](https://pep8.org/)

## ❓ Dúvidas?

Se tiver dúvidas:
- Abra uma issue com a tag `question`
- Entre em contato com os mantenedores
- Consulte a documentação existente

## 🎉 Reconhecimento

Todos os contribuidores serão reconhecidos no README do projeto!

---

Obrigado por contribuir com o ChatCine! 🎬

