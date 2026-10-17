#!/usr/bin/env node
'use strict'

/**
 * Usado pelo "npm run dev": aguarda o Next.js subir e abre o navegador.
 * Os processos em si são gerenciados pelo concurrently.
 */

const { APP_PORT, APP_URL, sleep, waitForPort, openBrowser } = require('./lib')

async function main() {
  console.log(`⏳ Aguardando o Next.js em ${APP_URL}...`)

  const ready = await waitForPort(APP_PORT, 180000)

  if (!ready) {
    console.warn(`❌ O Next.js não subiu na porta ${APP_PORT} em 2 minutos.`)
    console.warn('   Verifique a saída acima ou execute: npm run stop')
    process.exit(1)
  }

  // Dá um instante para o servidor terminar de subir antes de abrir a aba
  await sleep(1000)
  openBrowser(APP_URL)
  console.log(`🌐 ChatCine aberto em ${APP_URL}`)
}

main()
