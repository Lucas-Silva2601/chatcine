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

// Log único da aplicação Next.js (páginas + API)
const file = path.join(LOGS_DIR, 'app.log')

console.log(`━━━ ChatCine — ${path.relative(process.cwd(), file)} (últimas ${lines} linhas) ━━━`)
console.log(tailFile(file, lines))
