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

/** Escapa um valor para uso em string literal do PowerShell. */
function quotePowerShell(value) {
  return `'${String(value).replace(/'/g, "''")}'`
}

/** Escapa um argumento seguindo as regras da linha de comando do Windows. */
function quoteWindowsArgument(value) {
  const text = String(value)
  if (!/[\s"]/.test(text)) return text

  let result = '"'
  let backslashes = 0

  for (const char of text) {
    if (char === '\\') {
      backslashes += 1
      continue
    }
    if (char === '"') {
      result += '\\'.repeat(backslashes * 2 + 1) + '"'
      backslashes = 0
      continue
    }
    result += '\\'.repeat(backslashes) + char
    backslashes = 0
  }

  return result + '\\'.repeat(backslashes * 2) + '"'
}

/**
 * Inicia um processo em segundo plano sem abrir janela no Windows.
 *
 * `detached: true` sempre cria um novo console no Windows (mesmo com
 * `windowsHide: true`). Por isso usamos o `Start-Process -WindowStyle Hidden`
 * do PowerShell, que inicia o processo com a janela oculta e o mantém vivo
 * depois que este script termina.
 */
function startHiddenWindowsProcess(execPath, args, { cwd, stdoutLog, stderrLog }) {
  const pidFile = path.join(LOGS_DIR, 'app.pid.tmp')
  const launcherLog = path.join(LOGS_DIR, 'launcher.log')
  const argumentList = args.map(quoteWindowsArgument).join(' ')
  const command = [
    '$ErrorActionPreference = "Stop";',
    `$p = Start-Process -FilePath ${quotePowerShell(execPath)}`,
    `-ArgumentList ${quotePowerShell(argumentList)}`,
    `-WorkingDirectory ${quotePowerShell(cwd)}`,
    '-WindowStyle Hidden',
    `-RedirectStandardOutput ${quotePowerShell(stdoutLog)}`,
    `-RedirectStandardError ${quotePowerShell(stderrLog)}`,
    '-PassThru;',
    `Set-Content -LiteralPath ${quotePowerShell(pidFile)} -Value $p.Id -NoNewline -Encoding ascii`,
  ].join(' ')

  fs.rmSync(pidFile, { force: true })
  const launcherFd = fs.openSync(launcherLog, 'w')

  let result
  try {
    // Sem pipes: o processo filho herda os handles do arquivo de log. Se
    // usássemos pipes, o `spawnSync` ficaria esperando o servidor terminar.
    result = spawnSync(
      'powershell.exe',
      ['-NoProfile', '-NonInteractive', '-Command', command],
      {
        windowsHide: true,
        timeout: 30000,
        stdio: ['ignore', launcherFd, launcherFd],
      }
    )
  } finally {
    fs.closeSync(launcherFd)
  }

  if (result.error) throw result.error
  if (result.status !== 0) {
    const detail = tailFile(launcherLog, 20).trim()
    throw new Error(detail || 'Falha ao iniciar o processo em segundo plano.')
  }

  let pidText
  try {
    pidText = fs.readFileSync(pidFile, 'utf8').trim()
  } finally {
    fs.rmSync(pidFile, { force: true })
  }

  const pid = Number(pidText)
  if (!Number.isInteger(pid) || pid <= 0) {
    throw new Error('Não foi possível obter o PID do processo iniciado.')
  }
  return pid
}

/**
 * Sobe um processo desacoplado do script atual.
 * @returns {{ pid: number, proc: import('node:child_process').ChildProcess|null }}
 */
function startBackgroundProcess(execPath, args, { cwd, stdoutLog, stderrLog }) {
  if (process.platform === 'win32') {
    return {
      pid: startHiddenWindowsProcess(execPath, args, { cwd, stdoutLog, stderrLog }),
      proc: null,
    }
  }

  const stdout = fs.openSync(stdoutLog, 'a')
  const stderr = fs.openSync(stderrLog, 'a')
  const proc = spawn(execPath, args, {
    cwd,
    detached: true,
    stdio: ['ignore', stdout, stderr],
    windowsHide: true,
  })
  fs.closeSync(stdout)
  fs.closeSync(stderr)
  proc.unref()

  return { pid: proc.pid, proc }
}

/** Verifica se um processo ainda está vivo. */
function isProcessAlive(pid) {
  try {
    process.kill(pid, 0)
    return true
  } catch {
    return false
  }
}

/** Abre uma URL no navegador padrão do sistema. */
function openBrowser(url) {
  let cmd
  let args

  if (process.platform === 'win32') {
    // O `rundll32` é um executável de subsistema GUI: abre a URL pelo
    // ShellExecute no navegador padrão sem criar nenhum console. O antigo
    // `cmd /c start` não funcionava de forma confiável com `windowsHide`.
    cmd = 'rundll32.exe'
    args = ['url.dll,FileProtocolHandler', url]
  } else if (process.platform === 'darwin') {
    cmd = 'open'
    args = [url]
  } else {
    cmd = 'xdg-open'
    args = [url]
  }

  try {
    // `detached` mantém o processo vivo depois que este script termina. No
    // Windows o `rundll32` é GUI, então não há console para aparecer.
    const child = spawn(cmd, args, {
      detached: true,
      stdio: 'ignore',
      windowsHide: true,
    })
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
  isProcessAlive,
  startBackgroundProcess,
  openBrowser,
  getPortPids,
  killPidTree,
  tailFile,
  savePids,
  readPids,
  clearPids,
}
