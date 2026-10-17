<div align="center">

# 🎬 ChatCine

### Chat interativo sobre filmes, movido a IA

*Converse, peça recomendações e descubra filmes com a ajuda de um assistente de cinema inteligente.*

<br/>

![Next.js](https://img.shields.io/badge/Next.js-16-black?style=for-the-badge&logo=next.js&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4-38B2AC?style=for-the-badge&logo=tailwindcss&logoColor=white)
![Ollama](https://img.shields.io/badge/IA-Ollama_Cloud-fff?style=for-the-badge&logo=ollama&logoColor=black)
![TMDB](https://img.shields.io/badge/Dados-TMDB-01b4e4?style=for-the-badge&logo=themoviedb&logoColor=white)
![SQLite](https://img.shields.io/badge/Storage-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

<br/>

**Frontend + API em um único servidor Next.js** — sem backend separado, sem Python.

[![Deploy](https://img.shields.io/badge/Deploy-npm_start-2ea44f?style=for-the-badge)](#-início-rápido)
[![License](https://img.shields.io/badge/Licença-MIT-blue?style=for-the-badge)](#-licença)

</div>

---

## 📖 Sobre o Projeto

O **ChatCine** é uma aplicação web full-stack que une uma interface de chat moderna a um assistente de IA especializado em cinema. Pergunte sobre qualquer filme, peça sugestões para a noite de cinema ou envie uma imagem para tentar identificar o filme — o ChatCine responde com **JSON estruturado** que a interface transforma em cards ricos com poster, nota, gênero e link do IMDb.

O que começou como um projeto Flask + React foi **migrado para uma arquitetura 100% Next.js/React**, com a API implementada como *Route Handlers* no mesmo servidor que serve a interface.

---

## ✨ Funcionalidades

- 💬 **Chat com IA** — Assistente de cinema que responde sempre em JSON estruturado (`movie` · `recommendations` · `text`).
- 🎞️ **Cards de filme dinâmicos** — Quando a IA identifica um filme, a interface renderiza um card com poster, ano, nota, gêneros, sinopse e link direto para o IMDb.
- 🔍 **Recomendações inteligentes** — Peça sugestões e receba uma lista de filmes com poster e ano.
- 🖼️ **Upload de arquivos** — Envio de imagens e vídeos para análise pela IA.
- 🔐 **Autenticação JWT** — Login e registro com tokens assinados (HS256) e estado persistido.
- 🎨 **Tema escuro cinematográfico** — Visual inspirado em catálogos de streaming.
- ⚡ **Servidor único** — Interface e API no mesmo Next.js, sem CORS e sem processo extra.

---

## 🧠 Arquitetura de IA

O assistente usa o **Ollama Cloud** (endpoint compatível com OpenAI) e segue um contrato de resposta rigoroso:

| Tipo | Quando a IA usa | Formato do `content` |
| ---- | --------------- | -------------------- |
| `movie` | Identificou um filme com alta confiança | `{ title, year }` |
| `recommendations` | Usuário pediu sugestões | `[{ title, year }, …]` |
| `text` | Saudação, dúvida ou conversa geral | `string` |

A IA é orientada por um **system prompt** que a faz responder *exclusivamente* em JSON, respeitar numeração de filmes ("Rambo 1" ≠ "Rambo 2"), corrigir erros de ortografia silenciosamente e adotar a persona de um cinéfilo descontraído.

Quando o tipo é `movie`, o servidor busca os **detalhes reais na TMDB** e substitui o conteúdo antes de enviar ao cliente — o que garante posters, notas e sinopses corretos.

---

## 🏗️ Arquitetura Técnica

```
chatcine/
├── app/                       # Rotas de páginas e de API (App Router)
│   ├── page.jsx               # "/" → ChatPage
│   ├── login/page.jsx         # "/login" → LoginPage
│   └── api/                   # API (Route Handlers)
│       ├── chat/                    # POST /api/chat
│       ├── movie/[id]/              # GET  /api/movie/:id
│       ├── recommendations/[id]/    # GET  /api/recommendations/:id
│       └── auth/                    # login · register · refresh · me · logout
├── lib/                       # Lógica de servidor
│   ├── ai.js                  # Ollama Cloud (fetch nativo)
│   ├── movie.js               # TMDB (fetch nativo)
│   ├── chat.js                # Orquestração do chat
│   ├── db.js                  # SQLite nativo (node:sqlite)
│   ├── jwt.js                 # JWT HS256 (node:crypto)
│   ├── password.js            # Hash de senha (scrypt)
│   ├── validate.js            # Validação das respostas da IA
│   └── ratelimit.js           # Rate limiting e cache em memória
├── components/                # Componentes React ("use client")
├── services/                  # Camada de acesso à API (axios)
├── store/                     # Estado global (Zustand)
├── styles/                    # CSS legado + Tailwind
└── scripts/                   # start · stop · restart · logs
```

### Decisões de Design

- **Sem dependências externas para o núcleo** — A IA (Ollama), a TMDB, o banco (SQLite nativo do Node), o JWT e o hash de senha usam recursos nativos do runtime (`fetch`, `node:sqlite`, `node:crypto`), mantendo o `package.json` enxuto.
- **Contrato de resposta preservado** — A API devolve `{ type, content }` em tudo, permitindo que a interface decida entre renderizar texto ou um card de filme.
- **Cache e rate limiting** — Detalhes de filmes cacheados por 1h; limite de 10 mensagens de chat por minuto por IP.

---

## 🚀 Início Rápido

```bash
# 1. Instalar dependências
npm run install:all

# 2. Configurar variáveis de ambiente
cp .env.example .env.local

# 3. Subir a aplicação (abre o navegador automaticamente)
npm start
```

Acesse **http://localhost:3000** 🍿

### Variáveis de Ambiente

Crie `.env.local`:

```env
# Obrigatórias
OLLAMA_API_KEY=      # https://ollama.com/settings/keys
TMDB_API_KEY=        # https://www.themoviedb.org/settings/api

# Opcionais
OLLAMA_MODEL=        # padrão: gemma4:31b-cloud
JWT_SECRET_KEY=      # segredo dos tokens (troque em produção)
```

> O banco SQLite é criado automaticamente em `data/chatcine.db` na primeira execução.

---

## 🛠️ Scripts Disponíveis

| Comando            | Descrição                                                    |
| ------------------ | ------------------------------------------------------------ |
| `npm start`        | Sobe a aplicação e **abre o navegador automaticamente**.     |
| `npm run stop`     | Para o servidor.                                             |
| `npm run restart`  | Para e sobe de novo (recompila e reabre o navegador).        |
| `npm run logs`     | Mostra as últimas linhas do log.                             |
| `npm run dev`      | Modo desenvolvimento com hot reload + abre o navegador.      |
| `npm run build`    | Build de produção.                                           |

---

## 🔌 Endpoints da API

| Método | Rota                          | Descrição                                  |
| ------ | ----------------------------- | ------------------------------------------ |
| POST   | `/api/chat`                   | Processa mensagem (texto + arquivo) e retorna a resposta da IA. |
| GET    | `/api/movie/:id`              | Detalhes de um filme (cache de 1h).        |
| GET    | `/api/recommendations/:id`    | Recomendações de filmes (cache de 1h).     |
| POST   | `/api/auth/login`             | Autentica e retorna um JWT.                |
| POST   | `/api/auth/register`          | Cria conta e retorna um JWT.               |
| POST   | `/api/auth/refresh`           | Renova o access token.                     |
| GET    | `/api/auth/me`                | Retorna o usuário autenticado.             |
| POST   | `/api/auth/logout`            | Confirma o logout.                         |

---

## 🧰 Stack Tecnológica

| Camada           | Tecnologias                                        |
| ---------------- | -------------------------------------------------- |
| Frontend         | Next.js 16 · React 19 · Tailwind CSS 4 · Zustand   |
| API              | Next.js Route Handlers (mesmo servidor)            |
| IA               | Ollama Cloud (`gemma4:31b-cloud`)                  |
| Dados de filmes  | TMDB API                                           |
| Persistência     | SQLite (`node:sqlite`)                             |
| Autenticação     | JWT HS256 (`node:crypto`) · scrypt                 |

---

## 🧯 Solução de Problemas

**Porta 3000 em uso?**
```bash
npm run stop
```

**IA ou filmes não respondem?**
Verifique se `OLLAMA_API_KEY` e `TMDB_API_KEY` estão preenchidas em `.env.local` e reinicie.

**Ver o que está acontecendo em tempo real?**
```bash
npm run logs -- --lines 100
```

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<div align="center">

Feito com 🎬 e ☕ por **[Lucas Silva](https://github.com/Lucas-Silva2601)**

⭐ Se este projeto te ajudou, considere dar uma estrela!

</div>
