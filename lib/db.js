/**
 * Camada de persistência com SQLite nativo (node:sqlite).
 * Portado de backend/models.py + backend/repositories/*.
 *
 * Mantém a mesma estrutura de tabelas do SQLAlchemy original:
 *   users, chat_sessions, chat_messages.
 *
 * A conexão é cacheada em globalThis para reutilizar entre hot-reloads do
 * Next.js em desenvolvimento.
 */

import { DatabaseSync } from 'node:sqlite'
import crypto from 'node:crypto'
import fs from 'node:fs'
import path from 'node:path'

const DB_PATH =
  process.env.SQLITE_PATH || path.join(process.cwd(), 'data', 'chatcine.db')

function openDb() {
  fs.mkdirSync(path.dirname(DB_PATH), { recursive: true })
  const db = new DatabaseSync(DB_PATH)
  db.exec('PRAGMA journal_mode = WAL;')
  db.exec('PRAGMA foreign_keys = ON;')
  migrate(db)
  return db
}

function getDb() {
  if (!globalThis.__chatcineDb) {
    globalThis.__chatcineDb = openDb()
  }
  return globalThis.__chatcineDb
}

function migrate(db) {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT NOT NULL UNIQUE,
      password_hash TEXT,
      profile_pic_url TEXT,
      plan_status TEXT NOT NULL DEFAULT 'free',
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS chat_sessions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER,
      session_key TEXT UNIQUE,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now')),
      FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS chat_messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      session_id INTEGER NOT NULL,
      role TEXT NOT NULL,
      content TEXT NOT NULL,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
    CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions (user_id);
    CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_key ON chat_sessions (session_key);
    CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages (session_id);
    CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages (created_at);
  `)
}

function defaultAvatar(email) {
  const username = String(email).split('@')[0]
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(username)}&background=random`
}

// ---------------------------------------------------------------------------
// Usuários (UserRepository)
// ---------------------------------------------------------------------------
export const users = {
  findByEmail(email) {
    return getDb()
      .prepare('SELECT * FROM users WHERE email = ?')
      .get(String(email).toLowerCase().trim())
  },

  findById(id) {
    return getDb().prepare('SELECT * FROM users WHERE id = ?').get(Number(id))
  },

  create({ email, passwordHash, profilePicUrl, planStatus = 'free' }) {
    const normalized = String(email).toLowerCase().trim()
    const avatar = profilePicUrl || defaultAvatar(normalized)
    const result = getDb()
      .prepare(
        `INSERT INTO users (email, password_hash, profile_pic_url, plan_status)
         VALUES (?, ?, ?, ?)`
      )
      .run(normalized, passwordHash || null, avatar, planStatus)
    return this.findById(result.lastInsertRowid)
  },
}

// ---------------------------------------------------------------------------
// Sessões de chat (ChatSessionRepository)
// ---------------------------------------------------------------------------
export const chatSessions = {
  findById(id) {
    return getDb().prepare('SELECT * FROM chat_sessions WHERE id = ?').get(Number(id))
  },

  findByUserId(userId) {
    return getDb()
      .prepare(
        'SELECT * FROM chat_sessions WHERE user_id = ? ORDER BY created_at DESC LIMIT 1'
      )
      .get(Number(userId))
  },

  findByKey(sessionKey) {
    return getDb()
      .prepare('SELECT * FROM chat_sessions WHERE session_key = ?')
      .get(String(sessionKey))
  },

  create({ userId = null, sessionKey = null } = {}) {
    const result = getDb()
      .prepare('INSERT INTO chat_sessions (user_id, session_key) VALUES (?, ?)')
      .run(userId, sessionKey)
    return this.findById(result.lastInsertRowid)
  },

  /** Obtém ou cria a sessão para um usuário/chave (port de get_or_create_for_user). */
  getOrCreate({ userId = null, sessionKey = null } = {}) {
    if (userId) {
      const existing = this.findByUserId(userId)
      return existing || this.create({ userId })
    }
    if (sessionKey) {
      const existing = this.findByKey(sessionKey)
      return existing || this.create({ sessionKey })
    }
    // Nova sessão anônima
    return this.create({ sessionKey: crypto.randomUUID() })
  },
}

// ---------------------------------------------------------------------------
// Mensagens de chat (ChatMessageRepository)
// ---------------------------------------------------------------------------
export const chatMessages = {
  create({ sessionId, role, content }) {
    getDb()
      .prepare(
        'INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)'
      )
      .run(Number(sessionId), role, content)
  },

  /** Últimas N mensagens de uma sessão em ordem cronológica (port de get_session_history). */
  getSessionHistory(sessionId, limit = 6) {
    const rows = getDb()
      .prepare(
        `SELECT * FROM chat_messages
         WHERE session_id = ?
         ORDER BY created_at DESC, id DESC
         LIMIT ?`
      )
      .all(Number(sessionId), Number(limit))
    return rows.reverse()
  },
}

export { getDb }
