'use strict'

/**
 * Utilitários compartilhados pelos scripts do ChatCine.
 *
 * O ChatCine é uma aplicação Next.js única (frontend + API), então os scripts
 * cuidam apenas do servidor na porta 3000. A experiência de "subir / parar /
 * reiniciar" é a mesma em Windows, macOS e Linux, sem dependências externas.
 */

const { spawn, spawnSync } = require('node:child_process')
const fs = require('node:fs')
const net = require('node:net')
const path = require('node:path')

const ROOT = path.resolve(__dirname, '..')
const APP_DIR = ROOT
const LOGS_DIR = path.join(ROOT, 'logs')
const PID_FILE = path.join(LOGS_DIR, 'pids.json')

const APP_PORT = Number(process.env.PORT || process.env.FRONTEND_PORT || 3000)
const APP_URL = `http://localhost:${APP_PORT}`

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

function ensureLogsDir() {
  fs.mkdirSync(LOGS_DIR, { recursive: true })
}

/** Verifica se algo está escutando na porta (TCP). */
function isPortListening(port, host = '127.0.0.1', timeout = 1000) {
  return new Promise((resolve) => {
    const socket = net.connect({ port, host })
    let settled = false

    const finish = (value) => {
      if (settled) return
      settled = true
      socket.destroy()
      resolve(value)
    }

    socket.setTimeout(timeout)
    socket.once('connect', () => finish(true))
    socket.once('timeout', () => finish(false))
    socket.once('error', () => finish(false))
  })
}

/** Aguarda uma porta começar a aceitar conexões. */
async function waitForPort(port, timeoutMs = 120000, intervalMs = 1000) {
  const deadline = Date.now() + timeoutMs
  while (Date.now() < deadline) {
    if (await isPortListening(port)) return true
    await sleep(intervalMs)
  }
  return false
}

/** Abre uma URL no navegador padrão do sistema. */
function openBrowser(url) {
  let cmd
  let args

  if (process.platform === 'win32') {
    cmd = 'cmd'
    args = ['/c', 'start', url]
  } else if (process.platform === 'darwin') {
    cmd = 'open'
    args = [url]
  } else {
    cmd = 'xdg-open'
    args = [url]
  }

  try {
    const child = spawn(cmd, args, { detached: true, stdio: 'ignore', windowsHide: false })
    child.on('error', () => {
      console.warn(`⚠️  Não foi possível abrir o navegador automaticamente. Acesse ${url}`)
    })
    child.unref()
    return true
  } catch {
    console.warn(`⚠️  Não foi possível abrir o navegador automaticamente. Acesse ${url}`)
    return false
  }
}

/** Retorna os PIDs com processos escutando na porta. */
function getPortPids(port) {
  if (process.platform === 'win32') {
    const result = spawnSync('netstat', ['-ano'], { encoding: 'utf8', windowsHide: true })
    if (result.status !== 0 || !result.stdout) return []

    const pids = new Set()
    const regex = new RegExp(`^\\s*TCP\\s+[^\\s]+:${port}\\s+[^\\s]+\\s+LISTENING\\s+(\\d+)\\s*$`, 'i')

    for (const line of result.stdout.split(/\r?\n/)) {
      const match = line.match(regex)
      if (match) pids.add(Number(match[1]))
    }
    return [...pids]
  }

  const result = spawnSync('lsof', ['-nP', `-iTCP:${port}`, '-sTCP:LISTEN', '-t'], { encoding: 'utf8' })
  if (result.status !== 0 || !result.stdout) return []

  return result.stdout
    .split(/\r?\n/)
    .map((value) => Number(value.trim()))
    .filter((value) => Number.isInteger(value) && value > 0)
}

/** Mata um processo (com toda a sua árvore de processos filhos). */
function killPidTree(pid) {
  if (process.platform === 'win32') {
    const result = spawnSync('taskkill', ['/PID', String(pid), '/T', '/F'], {
      encoding: 'utf8',
      windowsHide: true,
    })
    return result.status === 0
  }

  try {
    process.kill(pid, 'SIGTERM')
    return true
  } catch {
    return false
  }
}

/** Últimas linhas de um arquivo de texto. */
function tailFile(file, lines = 40) {
  try {
    const content = fs.readFileSync(file, 'utf8')
    return content.split(/\r?\n/).slice(-lines).join('\n')
  } catch {
    return '(sem dados)'
  }
}

function savePids(data) {
  ensureLogsDir()
  fs.writeFileSync(PID_FILE, JSON.stringify(data, null, 2))
}

function readPids() {
  try {
    return JSON.parse(fs.readFileSync(PID_FILE, 'utf8'))
  } catch {
    return null
  }
}

function clearPids() {
  try {
    fs.unlinkSync(PID_FILE)
  } catch {
    /* arquivo já não existe */
  }
}

module.exports = {
  ROOT,
  APP_DIR,
  LOGS_DIR,
  PID_FILE,
  APP_PORT,
  APP_URL,
  sleep,
  ensureLogsDir,
  isPortListening,
  waitForPort,
  openBrowser,
  getPortPids,
  killPidTree,
  tailFile,
  savePids,
  readPids,
  clearPids,
}
