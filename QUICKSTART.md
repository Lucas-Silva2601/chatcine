# 🚀 Guia Rápido - ChatCine

## Instalação Rápida (5 minutos)

### 1. Instale as dependências

```bash
# Na raiz do projeto
npm install

# Instale dependências do backend
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cd ..

# Instale dependências do frontend
cd frontend
npm install
cd ..
```

### 2. Configure as variáveis de ambiente

Crie o arquivo `backend/.env`:

```env
FLASK_ENV=development
SECRET_KEY=minha-chave-secreta-123
JWT_SECRET_KEY=minha-chave-jwt-456
PORT=5001

# Banco de Dados
# Opção 1: Supabase (veja SUPABASE_SETUP.md)
DATABASE_URL=postgresql://postgres:[SUA-SENHA]@db.xxxxx.supabase.co:5432/postgres

# Opção 2: SQLite Local
# DATABASE_URL=sqlite:///chatcine_dev.db

GROQ_API_KEY=sua-chave-groq
TMDB_API_KEY=sua-chave-tmdb

RATELIMIT_ENABLED=true
```

**💡 Dica**: Para usar Supabase (recomendado), siga o guia [SUPABASE_SETUP.md](SUPABASE_SETUP.md)

### 3. Inicialize o banco de dados

```bash
cd backend
python init_db.py
cd ..
```

### 4. Execute o projeto

```bash
npm run dev
```

Pronto! Acesse: **http://localhost:3000**

## 📝 Comandos Úteis

```bash
# Iniciar tudo
npm run dev

# Apenas backend
npm run dev:backend

# Apenas frontend
npm run dev:frontend

# Build de produção
npm run build

# Testes
npm run test:backend
npm run test:frontend
```

## 🔑 Obtendo as API Keys

### Groq API (IA)
1. Acesse: https://console.groq.com/
2. Crie uma conta
3. Vá em "API Keys"
4. Crie uma nova chave
5. Copie e cole no `.env`

### TMDB API (Filmes)
1. Acesse: https://www.themoviedb.org/
2. Crie uma conta
3. Vá em Settings → API
4. Solicite uma API Key
5. Copie e cole no `.env`

## 🐛 Problemas Comuns

### Erro: "Module not found"
```bash
# Reinstale as dependências
npm run install:all
```

### Erro: "Port 3000 already in use"
```bash
# Mate o processo na porta 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:3000 | xargs kill -9
```

### Erro: "Database locked"
```bash
# Reinicialize o banco
cd backend
python init_db.py
```

## 📱 Testando

1. Abra http://localhost:3000
2. Clique em "Registrar"
3. Crie uma conta
4. Comece a conversar sobre filmes!

## 🎯 Próximos Passos

- Configure Google Cloud Speech para áudio
- Personalize os estilos CSS
- Adicione mais funcionalidades
- Deploy em produção

---

**Dúvidas?** Consulte o [README.md](README.md) completo!

