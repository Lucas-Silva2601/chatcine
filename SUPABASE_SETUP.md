# 🗄️ Configuração do Supabase

Este guia mostra como configurar o ChatCine para usar o Supabase como banco de dados.

## 📋 Pré-requisitos

- Conta no [Supabase](https://supabase.com/) (gratuita)
- Projeto ChatCine instalado

## 🚀 Passo a Passo

### 1. Criar Projeto no Supabase

1. Acesse [https://supabase.com/](https://supabase.com/)
2. Faça login ou crie uma conta
3. Clique em "New Project"
4. Preencha:
   - **Name**: ChatCine
   - **Database Password**: Crie uma senha forte (anote!)
   - **Region**: Escolha a mais próxima
5. Clique em "Create new project"
6. Aguarde ~2 minutos para o projeto ser criado

### 2. Obter Credenciais

No painel do seu projeto Supabase:

1. Vá em **Settings** → **API**
2. Copie as seguintes informações:
   - **Project URL** (ex: `https://xxxxx.supabase.co`)
   - **anon public key** (chave pública)
   - **service_role key** (chave privada - use com cuidado!)

3. Vá em **Settings** → **Database**
4. Role até **Connection string** → **URI**
5. Copie a **Connection string** (ex: `postgresql://postgres:[YOUR-PASSWORD]@...`)
6. Substitua `[YOUR-PASSWORD]` pela senha que você criou

### 3. Criar Tabelas no Banco de Dados

1. No painel do Supabase, vá em **SQL Editor**
2. Clique em "New query"
3. Copie todo o conteúdo do arquivo `backend/migrations/supabase_schema.sql`
4. Cole no editor SQL
5. Clique em "Run" (▶️)
6. Verifique se apareceu "Success. No rows returned"

### 4. Configurar Backend

Crie ou edite o arquivo `backend/.env`:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=sua-chave-secreta-aqui
JWT_SECRET_KEY=sua-chave-jwt-aqui
PORT=5001

# Supabase Database
DATABASE_URL=postgresql://postgres:[SUA-SENHA]@db.xxxxx.supabase.co:5432/postgres

# External APIs
GROQ_API_KEY=sua-chave-groq
TMDB_API_KEY=sua-chave-tmdb

# Rate Limiting
RATELIMIT_ENABLED=true
```

**⚠️ IMPORTANTE**: Substitua:
- `[SUA-SENHA]` pela senha do banco
- `xxxxx` pelo ID do seu projeto
- A URL completa você copiou no passo 2

### 5. Configurar Frontend (Opcional)

Se quiser usar recursos do Supabase diretamente no frontend, crie `frontend/.env`:

```env
# Supabase Configuration (opcional)
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=sua-chave-publica-anon

# API Backend
VITE_API_URL=http://localhost:5001/api
```

### 6. Instalar Dependências

```bash
# Instalar psycopg2 (driver PostgreSQL)
cd backend
.\venv\Scripts\pip.exe install psycopg2-binary

# Instalar cliente Supabase no frontend (opcional)
cd ../frontend
npm install @supabase/supabase-js

cd ..
```

### 7. Testar Conexão

```bash
# Testar se o backend conecta ao Supabase
cd backend
.\venv\Scripts\python.exe -c "from app import create_app; app = create_app(); print('✅ Conectado ao Supabase!')"
```

### 8. Executar o Projeto

```bash
npm run dev
```

Acesse: **http://localhost:3000**

## 🔍 Verificar se Está Funcionando

1. Crie uma conta no ChatCine
2. No Supabase, vá em **Table Editor** → **users**
3. Você deve ver o usuário criado!

## 🛠️ Comandos Úteis

### Ver Dados no Supabase

```sql
-- Ver todos os usuários
SELECT * FROM users;

-- Ver sessões de chat
SELECT * FROM chat_sessions;

-- Ver mensagens
SELECT * FROM chat_messages;

-- Ver estatísticas
SELECT 
    (SELECT COUNT(*) FROM users) as total_users,
    (SELECT COUNT(*) FROM chat_sessions) as total_sessions,
    (SELECT COUNT(*) FROM chat_messages) as total_messages;
```

### Limpar Dados (Cuidado!)

```sql
-- Deletar todas as mensagens
TRUNCATE chat_messages CASCADE;

-- Deletar todas as sessões
TRUNCATE chat_sessions CASCADE;

-- Deletar todos os usuários (cuidado!)
TRUNCATE users CASCADE;
```

## 🔐 Segurança

### Row Level Security (RLS)

O schema já inclui políticas RLS que garantem:
- ✅ Usuários só veem seus próprios dados
- ✅ Usuários só podem modificar seus próprios dados
- ✅ Proteção automática contra acesso não autorizado

### Boas Práticas

1. **Nunca compartilhe** a `service_role key`
2. **Use variáveis de ambiente** para credenciais
3. **Não commite** o arquivo `.env` no Git
4. **Mude as senhas** em produção
5. **Habilite 2FA** na sua conta Supabase

## 🌍 Deploy em Produção

### Variáveis de Ambiente

Configure no seu serviço de hosting (Vercel, Railway, etc):

```env
FLASK_ENV=production
DATABASE_URL=postgresql://postgres:...@db.xxxxx.supabase.co:5432/postgres
SECRET_KEY=chave-super-secreta-producao
JWT_SECRET_KEY=chave-jwt-super-secreta-producao
GROQ_API_KEY=sua-chave-groq
TMDB_API_KEY=sua-chave-tmdb
```

## 📊 Monitoramento

No Supabase, você pode monitorar:

1. **Database** → **Reports**: Uso do banco
2. **Database** → **Backups**: Backups automáticos
3. **Logs**: Logs de queries e erros

## 🆘 Problemas Comuns

### Erro: "Connection refused"

**Solução**: Verifique se a URL do banco está correta e se sua senha está correta.

### Erro: "SSL required"

**Solução**: Adicione `?sslmode=require` no final da DATABASE_URL:
```
postgresql://...?sslmode=require
```

### Erro: "Too many connections"

**Solução**: O plano gratuito do Supabase tem limite de conexões. Configure connection pooling:

```python
# backend/config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 5,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
```

### Tabelas não aparecem

**Solução**: Execute o script SQL novamente no SQL Editor do Supabase.

## 💡 Dicas

1. **Backups**: Supabase faz backups automáticos diários
2. **Logs**: Monitore os logs no painel do Supabase
3. **Performance**: Use índices nas colunas mais consultadas
4. **Escalabilidade**: Upgrade o plano conforme necessário

## 📚 Recursos

- [Documentação Supabase](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

## 🎉 Pronto!

Agora seu ChatCine está usando o Supabase como banco de dados! 🚀

---

**Dúvidas?** Consulte a [documentação oficial do Supabase](https://supabase.com/docs).

