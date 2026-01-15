# 🎬 ChatCine - Full Stack (React + Flask)

ChatCine é uma aplicação web full stack que combina **React.js** no frontend e **Flask** no backend para criar um chat interativo sobre filmes com inteligência artificial.

## 🏗️ Arquitetura

```
chatcine/
├── frontend/                 # Aplicação React.js
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   ├── pages/            # Páginas
│   │   ├── services/         # Serviços API
│   │   ├── store/            # Estado global (Zustand)
│   │   └── styles/           # CSS
│   ├── package.json
│   └── vite.config.js
│
├── backend/                  # API Flask REST
│   ├── controllers/          # Endpoints API
│   ├── services/             # Lógica de negócio
│   ├── repositories/         # Acesso a dados
│   ├── models.py             # Modelos do banco
│   ├── app.py                # Factory Flask
│   └── requirements.txt
│
└── package.json              # Scripts principais
```

## ✨ Funcionalidades

- 💬 **Chat em Tempo Real**: Interface moderna com React
- 🎥 **Busca de Filmes**: Integração com TMDB
- 🎯 **Recomendações**: IA sugere filmes similares
- 🎤 **Transcrição de Áudio**: Envie mensagens de voz
- 🖼️ **Análise de Imagens**: Envie imagens para análise
- 🔐 **Autenticação JWT**: Sistema seguro de autenticação
- 📱 **Responsivo**: Funciona em desktop e mobile

## 🚀 Tecnologias

### Frontend
- **React 18** - Biblioteca UI
- **Vite** - Build tool ultrarrápido
- **Zustand** - Gerenciamento de estado
- **Axios** - Cliente HTTP
- **React Router** - Roteamento

### Backend
- **Flask 3.0** - Framework web Python
- **Flask-JWT-Extended** - Autenticação JWT
- **Flask-CORS** - Suporte CORS
- **SQLAlchemy** - ORM
- **Groq API** - IA para chat
- **TMDB API** - Dados de filmes

## 📋 Pré-requisitos

- **Node.js** 14+ e npm
- **Python** 3.9+
- **pip** (gerenciador de pacotes Python)
- **Banco de Dados**:
  - [Supabase](https://supabase.com/) (Recomendado - PostgreSQL gratuito) OU
  - SQLite (local, para desenvolvimento)
- Chaves de API:
  - [Groq API](https://groq.com/)
  - [TMDB API](https://www.themoviedb.org/)

## ⚙️ Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/chatcine.git
cd chatcine
```

### 2. Instale o concurrently (para rodar frontend e backend juntos)

```bash
npm install
```

### 3. Configure o Backend

```bash
cd backend

# Crie ambiente virtual
python -m venv venv

# Ative o ambiente virtual
# Windows:
.\\venv\\Scripts\\activate
# Linux/Mac:
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
# Crie um arquivo .env na pasta backend:
```

**backend/.env:**
```env
FLASK_ENV=development
SECRET_KEY=sua-chave-secreta-aqui
JWT_SECRET_KEY=sua-chave-jwt-aqui
PORT=5001

# Banco de Dados
# Opção 1: Supabase (Recomendado)
DATABASE_URL=postgresql://postgres:[SUA-SENHA]@db.xxxxx.supabase.co:5432/postgres

# Opção 2: SQLite Local (para desenvolvimento)
# DATABASE_URL=sqlite:///chatcine_dev.db

# APIs Externas
GROQ_API_KEY=sua-chave-groq-aqui
TMDB_API_KEY=sua-chave-tmdb-aqui

# Google Cloud (Opcional)
GOOGLE_APPLICATION_CREDENTIALS=google-credentials.json

# Rate Limiting
RATELIMIT_ENABLED=true
```

**📝 Nota**: Para configurar o Supabase, veja o guia completo em [SUPABASE_SETUP.md](SUPABASE_SETUP.md)

```bash
# Inicialize o banco de dados
python init_db.py

cd ..
```

### 4. Configure o Frontend

```bash
cd frontend

# Instale dependências
npm install

# Configure variáveis de ambiente (opcional)
# Crie um arquivo .env na pasta frontend:
```

**frontend/.env:**
```env
VITE_API_URL=http://localhost:5001/api
```

```bash
cd ..
```

## 🎮 Executando o Projeto

### Opção 1: Executar tudo com um comando (Recomendado)

```bash
npm run dev
```

Este comando inicia automaticamente:
- ✅ Backend Flask na porta 5001
- ✅ Frontend React na porta 3000

Acesse: **http://localhost:3000**

### Opção 2: Executar separadamente

**Terminal 1 - Backend:**
```bash
npm run dev:backend
# ou
cd backend && python run.py
```

**Terminal 2 - Frontend:**
```bash
npm run dev:frontend
# ou
cd frontend && npm run dev
```

## 📝 Scripts Disponíveis

### Scripts Principais (raiz do projeto)

```bash
npm run dev              # Inicia frontend + backend
npm run dev:backend      # Inicia apenas backend
npm run dev:frontend     # Inicia apenas frontend
npm run build            # Build de produção do frontend
npm run install:all      # Instala todas as dependências
npm run install:backend  # Instala dependências do backend
npm run install:frontend # Instala dependências do frontend
npm run init-db          # Inicializa banco de dados
npm run test:backend     # Testes do backend
npm run test:frontend    # Testes do frontend
```

### Scripts do Frontend (pasta frontend)

```bash
npm run dev      # Servidor de desenvolvimento
npm run build    # Build de produção
npm run preview  # Preview do build
npm run lint     # Verifica código
```

### Scripts do Backend (pasta backend)

```bash
python run.py           # Inicia servidor
python init_db.py       # Inicializa banco
pytest                  # Executa testes
flake8 .               # Linting
black .                # Formatação
```

## 🔑 Autenticação

O sistema usa **JWT (JSON Web Tokens)** para autenticação:

1. **Login/Registro**: Usuário recebe um token JWT
2. **Token Storage**: Token é salvo no localStorage
3. **Requisições**: Token é enviado no header `Authorization: Bearer <token>`
4. **Expiração**: Token expira em 1 hora (renovável)

## 🌐 Endpoints da API

### Autenticação

- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Registro
- `POST /api/auth/refresh` - Renovar token
- `GET /api/auth/me` - Dados do usuário
- `POST /api/auth/logout` - Logout

### Chat

- `POST /api/chat` - Enviar mensagem
- `GET /api/movie/:id` - Buscar filme
- `GET /api/recommendations/:id` - Recomendações

## 🎨 Estrutura do Frontend

```
frontend/src/
├── components/
│   ├── ChatMessage.jsx       # Componente de mensagem
│   └── MovieCard.jsx          # Card de filme
├── pages/
│   ├── LoginPage.jsx          # Página de login
│   └── ChatPage.jsx           # Página principal
├── services/
│   ├── api.js                 # Configuração Axios
│   ├── authService.js         # Serviços de auth
│   └── chatService.js         # Serviços de chat
├── store/
│   └── authStore.js           # Estado de autenticação
├── styles/
│   ├── index.css              # Estilos globais
│   ├── LoginPage.css
│   ├── ChatPage.css
│   ├── ChatMessage.css
│   └── MovieCard.css
├── App.jsx                    # Componente raiz
└── main.jsx                   # Entry point
```

## 🔧 Estrutura do Backend

```
backend/
├── controllers/               # Endpoints API
│   ├── auth_controller.py
│   └── chat_controller.py
├── services/                  # Lógica de negócio
│   ├── ai_service.py
│   ├── chat_service.py
│   ├── movie_service.py
│   └── speech_service.py
├── repositories/              # Acesso a dados
│   ├── user_repository.py
│   └── chat_repository.py
├── dto/                       # Data Transfer Objects
├── core/                      # Exceções e constantes
├── utils/                     # Utilitários
├── models.py                  # Modelos do banco
├── config.py                  # Configurações
├── extensions.py              # Extensões Flask
└── app.py                     # Factory Flask
```

## 🐳 Docker (Opcional)

```bash
docker-compose up -d
```

## 🧪 Testes

### Backend
```bash
cd backend
pytest
pytest --cov=. --cov-report=html
```

### Frontend
```bash
cd frontend
npm run test
```

## 📦 Build de Produção

```bash
# Build do frontend
npm run build

# Os arquivos estarão em frontend/dist
# Configure seu servidor para servir esses arquivos
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 🙏 Agradecimentos

- [TMDB](https://www.themoviedb.org/) - API de filmes
- [Groq](https://groq.com/) - API de IA
- [React](https://react.dev/) - Biblioteca UI
- [Flask](https://flask.palletsprojects.com/) - Framework web

## 📞 Suporte

Para suporte, abra uma issue no GitHub.

---

⭐ Se este projeto foi útil para você, considere dar uma estrela!

**Desenvolvido com ❤️ usando React + Flask**
