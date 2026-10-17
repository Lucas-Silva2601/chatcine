#!/usr/bin/env node
'use strict'

/**
 * Reinicia o ChatCine: primeiro para os processos em execução e depois
 * sobe tudo de novo, abrindo o navegador no final.
 *
 * Uso: npm run restart
 */

const { stopApp } = require('./stop')
const { startApp } = require('./start')

async function restartApp() {
  console.log('🔄 Reiniciando o ChatCine...')
  console.log('')

  await stopApp()

  console.log('')
  const result = await startApp({ open: true })
  return result
}

if (require.main === module) {
  restartApp().then((result) => {
    process.exit(result.ok ? 0 : 1)
  })
}

module.exports = { restartApp }
