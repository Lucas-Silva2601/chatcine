# 🔧 Solução de Problemas - ChatCine

Guia para resolver problemas comuns ao executar o ChatCine.

## 🚨 Erro: "Can't load plugin: sqlalchemy.dialects:https"

**Causa**: A variável `DATABASE_URL` está vazia ou com valor inválido.

**Solução**:

1. Execute o script de setup:
```bash
npm run setup
# ou
python setup.py
```

2. Verifique se `backend/.env` foi criado

3. Certifique-se que `DATABASE_URL` está vazia ou comentada:
```env
# Para SQLite local (padrão)
DATABASE_URL=

# OU comente a linha:
# DATABASE_URL=
```

4. Para usar Supabase, configure corretamente:
```env
DATABASE_URL=postgresql://postgres:[SENHA]@db.xxxxx.supabase.co:5432/postgres
```

## 🚨 Erro: "ModuleNotFoundError: No module named 'flask'"

**Causa**: Dependências do Python não instaladas.

**Solução**:
```bash
# Ative o venv
.\venv\Scripts\activate

# Instale dependências
cd backend
pip install -r requirements.txt
```

## 🚨 Erro: "Port 3000 already in use"

**Causa**: Outra aplicação está usando a porta 3000.

**Solução Windows**:
```bash
# Encontre o processo
netstat -ano | findstr :3000

# Mate o processo (substitua PID)
taskkill /PID <PID> /F
```

**Solução Linux/Mac**:
```bash
# Mate o processo na porta 3000
lsof -ti:3000 | xargs kill -9
```

## 🚨 Erro: "Connection refused" (Supabase)

**Causa**: URL do Supabase incorreta ou senha errada.

**Solução**:

1. Verifique a URL no painel do Supabase:
   - Settings → Database → Connection string

2. Certifique-se de substituir `[YOUR-PASSWORD]`

3. Teste a conexão:
```bash
cd backend
python -c "from app import create_app; create_app()"
```

## 🚨 Erro: "psycopg2 not installed"

**Causa**: Driver PostgreSQL não instalado.

**Solução**:
```bash
cd backend
pip install psycopg2-binary
```

## 🚨 Frontend não carrega / tela branca

**Causa**: Dependências do frontend não instaladas.

**Solução**:
```bash
cd frontend
npm install
npm run dev
```

## 🚨 Erro: "API request failed"

**Causa**: Backend não está rodando ou URL incorreta.

**Solução**:

1. Verifique se o backend está rodando na porta 5001:
```bash
# Em um terminal separado
npm run dev:backend
```

2. Verifique `frontend/.env`:
```env
VITE_API_URL=http://localhost:5001/api
```

3. Teste o backend:
```bash
curl http://localhost:5001/api/auth/me
```

## 🚨 Erro: "JWT token invalid"

**Causa**: Token expirado ou inválido.

**Solução**:

1. Faça logout e login novamente

2. Limpe o localStorage:
```javascript
// No console do navegador (F12)
localStorage.clear()
location.reload()
```

## 🚨 Erro: "GROQ_API_KEY not configured"

**Causa**: API key do Groq não configurada.

**Solução**:

1. Obtenha uma chave em: https://console.groq.com/

2. Configure em `backend/.env`:
```env
GROQ_API_KEY=sua-chave-aqui
```

3. Reinicie o backend

## 🚨 Erro: "TMDB API error"

**Causa**: API key do TMDB não configurada ou inválida.

**Solução**:

1. Obtenha uma chave em: https://www.themoviedb.org/settings/api

2. Configure em `backend/.env`:
```env
TMDB_API_KEY=sua-chave-aqui
```

3. Reinicie o backend

## 🚨 Banco de dados vazio após reiniciar

**Causa**: Usando SQLite em memória ou banco foi deletado.

**Solução**:

1. Verifique `backend/.env`:
```env
# Deve ter um caminho de arquivo, não :memory:
DATABASE_URL=
```

2. Reinicialize o banco:
```bash
npm run init-db
```

## 🚨 Erro: "CORS policy"

**Causa**: Frontend e backend em portas diferentes sem CORS configurado.

**Solução**: O CORS já está configurado no backend. Certifique-se de:

1. Backend rodando em: `http://localhost:5001`
2. Frontend rodando em: `http://localhost:3000`

## 🚨 Erro: "npm: command not found"

**Causa**: Node.js não instalado.

**Solução**:

1. Instale Node.js: https://nodejs.org/
2. Verifique a instalação:
```bash
node --version
npm --version
```

## 🚨 Erro: "python: command not found"

**Causa**: Python não instalado ou não está no PATH.

**Solução Windows**:

1. Instale Python: https://python.org/
2. Marque "Add Python to PATH" durante instalação
3. Reinicie o terminal

**Solução Linux/Mac**:
```bash
# Use python3
python3 --version
```

## 🚨 Build do frontend falha

**Causa**: Erros de sintaxe ou dependências faltando.

**Solução**:

1. Limpe cache e reinstale:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

2. Verifique erros no console

## 🚨 Migrations não funcionam (Supabase)

**Causa**: Tabelas não criadas ou RLS bloqueando.

**Solução**:

1. Execute o schema SQL manualmente no Supabase:
   - Abra SQL Editor
   - Cole o conteúdo de `backend/migrations/supabase_schema.sql`
   - Execute

2. Verifique as tabelas:
```sql
SELECT * FROM users LIMIT 1;
```

## 🚨 Erro: "Rate limit exceeded"

**Causa**: Muitas requisições em pouco tempo.

**Solução**:

1. Aguarde 1 minuto

2. Para desenvolvimento, desabilite em `backend/.env`:
```env
RATELIMIT_ENABLED=false
```

## 🚨 Logs não aparecem

**Causa**: Nível de log muito alto.

**Solução**:

Configure em `backend/.env`:
```env
LOG_LEVEL=DEBUG
```

## 🚨 Venv não ativa (Windows)

**Causa**: Política de execução do PowerShell.

**Solução**:
```powershell
# Execute como Administrador
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Depois ative o venv
.\venv\Scripts\Activate.ps1
```

## 📞 Ainda com problemas?

1. **Verifique os logs**:
   - Backend: Terminal onde rodou `npm run dev:backend`
   - Frontend: Console do navegador (F12)

2. **Reinicie tudo**:
```bash
# Pare tudo (Ctrl+C)
# Limpe e reinicie
npm run dev
```

3. **Reinstale tudo**:
```bash
# Backend
cd backend
pip install -r requirements.txt --force-reinstall

# Frontend
cd ../frontend
rm -rf node_modules
npm install

# Raiz
cd ..
npm install
```

4. **Abra uma issue**: https://github.com/seu-usuario/chatcine/issues

---

**Dica**: Sempre verifique os logs primeiro! Eles geralmente indicam o problema exato.

