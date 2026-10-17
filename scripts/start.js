#!/usr/bin/env node
'use strict'

/**
 * Sobe o ChatCine (aplicação Next.js única — páginas + API) em segundo plano,
 * aguarda o servidor ficar pronto e abre o navegador automaticamente.
 *
 * Uso: npm start
 * Pare: npm run stop
 * Reinicie: npm run restart
 */

const { spawn } = require('node:child_process')
const fs = require('node:fs')
const path = require('node:path')

const {
  ROOT,
  APP_DIR,
  LOGS_DIR,
  APP_PORT,
  APP_URL,
  sleep,
  ensureLogsDir,
  isPortListening,
  openBrowser,
  savePids,
  tailFile,
} = require('./lib')

async function startApp({ open = true, timeout = 180000, production = false } = {}) {
  // ---------------------------------------------------------------------
  // Verificações iniciais
  // ---------------------------------------------------------------------
  if (await isPortListening(APP_PORT)) {
    console.log(`⚠️  O ChatCine já parece estar rodando em ${APP_URL}.`)
    console.log('   Para reiniciar, use: npm run restart')
    if (open) openBrowser(APP_URL)
    return { ok: true, alreadyRunning: true }
  }

  if (!fs.existsSync(path.join(APP_DIR, 'node_modules', 'next'))) {
    console.error('❌ Dependências não encontradas.')
    console.error('   Execute: npm run install:all  (ou npm install)')
    return { ok: false }
  }

  // ---------------------------------------------------------------------
  // Sobe o servidor em segundo plano, com log em logs/app.log
  // ---------------------------------------------------------------------
  ensureLogsDir()

  const appLog = path.join(LOGS_DIR, 'app.log')
  const stamp = `# ChatCine — ${new Date().toLocaleString()}\n`
  fs.writeFileSync(appLog, stamp)

  const fd = fs.openSync(appLog, 'a')
  // Sobe o Next.js direto pelo binário local (evita recursão com `npm start`
  // e respeita a porta configurada sem depender de um script intermediário).
  const nextBin = path.join(APP_DIR, 'node_modules', 'next', 'dist', 'bin', 'next')
  const nextArgs = [nextBin, production ? 'start' : 'dev', '-p', String(APP_PORT)]
  const proc = spawn(process.execPath, nextArgs, {
    cwd: APP_DIR,
    detached: true,
    stdio: ['ignore', fd, fd],
    windowsHide: true,
  })
  fs.closeSync(fd)

  let exited = false
  let spawnError = null
  proc.on('error', (error) => (spawnError = error))
  proc.on('exit', () => (exited = true))

  savePids({ app: proc.pid, startedAt: new Date().toISOString(), log: appLog })

  console.log('🚀 Iniciando ChatCine...')
  console.log(`   • Aplicação (Next.js) → ${APP_URL}`)
  console.log(`   • Log                  → ${path.relative(ROOT, appLog)}`)
  console.log('')

  // ---------------------------------------------------------------------
  // Aguarda o Next.js ficar disponível
  // ---------------------------------------------------------------------
  const deadline = Date.now() + timeout
  let ready = false

  while (Date.now() < deadline) {
    if (spawnError) break
    if (exited) break
    if (await isPortListening(APP_PORT)) {
      ready = true
      break
    }
    await sleep(1000)
  }

  if (!ready) {
    console.error('❌ O servidor não ficou pronto a tempo.')
    if (spawnError) console.error(`   Erro: ${spawnError.message}`)
    console.error('')
    console.error(`📄 Últimas linhas de ${path.relative(ROOT, appLog)}:`)
    console.error(tailFile(appLog, 40))
    return { ok: false }
  }

  console.log('✅ ChatCine no ar!')
  console.log(`   🌐 Aplicação: ${APP_URL}`)
  console.log('')
  console.log('   Comandos úteis:')
  console.log('     npm run stop      → para a aplicação')
  console.log('     npm run restart   → reinicia a aplicação')
  console.log('     npm run logs      → mostra os logs')

  if (open) {
    // Pequena pausa para o Next terminar a primeira compilação
    await sleep(1000)
    openBrowser(APP_URL)
  }

  return { ok: true }
}

if (require.main === module) {
  startApp({ open: true }).then((result) => {
    process.exit(result.ok ? 0 : 1)
  })
}

module.exports = { startApp }
