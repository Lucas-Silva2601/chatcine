#!/usr/bin/env node
'use strict'

/**
 * Para o ChatCine: encerra o processo Next.js que está escutando na porta da
 * aplicação e limpa os arquivos de PID.
 *
 * Uso: npm run stop
 */

const {
  APP_PORT,
  sleep,
  getPortPids,
  killPidTree,
  readPids,
  clearPids,
} = require('./lib')

async function waitPortFree(port, timeoutMs = 10000) {
  const deadline = Date.now() + timeoutMs
  while (Date.now() < deadline) {
    if (getPortPids(port).length === 0) return true
    await sleep(500)
  }
  return false
}

async function stopApp() {
  const pids = new Set(getPortPids(APP_PORT))

  // Inclui o PID registrado no arquivo, caso a porta já tenha sido liberada
  const saved = readPids()
  if (saved?.app) pids.add(saved.app)

  if (pids.size === 0) {
    console.log('ℹ️  Nenhum processo do ChatCine em execução.')
    clearPids()
    return { ok: true, stopped: [] }
  }

  console.log('🛑 Parando o ChatCine...')
  const stopped = []
  for (const pid of pids) {
    const ok = killPidTree(pid)
    if (ok) stopped.push(pid)
  }

  await waitPortFree(APP_PORT)
  clearPids()

  if (stopped.length > 0) {
    console.log(`✅ ChatCine parado (PIDs encerrados: ${stopped.join(', ')}).`)
  } else {
    console.log('⚠️  Nenhum processo pôde ser encerrado. Verifique a porta manualmente.')
  }

  return { ok: true, stopped }
}

if (require.main === module) {
  stopApp().then(() => process.exit(0))
}

module.exports = { stopApp }
