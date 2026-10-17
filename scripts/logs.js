#!/usr/bin/env node
'use strict'

/**
 * Mostra as últimas linhas do log do ChatCine.
 *
 * Uso: npm run logs
 *      npm run logs -- --lines 120
 */

const path = require('node:path')
const { LOGS_DIR, tailFile } = require('./lib')

function parseLines(args) {
  const index = args.indexOf('--lines')
  if (index !== -1 && args[index + 1]) {
    const value = Number(args[index + 1])
    if (Number.isInteger(value) && value > 0) return value
  }
  return 60
}

const lines = parseLines(process.argv.slice(2))

// Logs da aplicação Next.js (páginas + API)
const files = [
  { label: 'saída', file: path.join(LOGS_DIR, 'app.log') },
  { label: 'erros', file: path.join(LOGS_DIR, 'app.err.log') },
]

console.log(`━━━ ChatCine — logs (últimas ${lines} linhas) ━━━`)

for (const { label, file } of files) {
  console.log('')
  console.log(`── ${label}: ${path.relative(process.cwd(), file)} ──`)
  console.log(tailFile(file, lines))
}
