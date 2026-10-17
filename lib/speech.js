/**
 * Serviço de transcrição de áudio (Google Cloud Speech-to-Text).
 * Portado de backend/services/speech_service.py.
 *
 * Opcional: só é usado se houver credenciais do Google configuradas.
 * A SDK oficial `@google-cloud/speech` é importada dinamicamente para que a
 * aplicação funcione sem ela instalada (transcrição fica indisponível).
 */

import { ExternalAPIError } from './errors'

/**
 * O serviço é considerado configurado se houver credenciais via variável de
 * ambiente (caminho do arquivo ou JSON direto). A validação do arquivo em si
 * acontece na SDK do Google, evitando acesso dinâmico ao filesystem que
 * dispararia o tracing completo do projeto no Turbopack.
 */
export function isSpeechConfigured() {
  return Boolean(
    process.env.GOOGLE_APPLICATION_CREDENTIALS || process.env.GOOGLE_CREDENTIALS_JSON
  )
}

/**
 * Transcreve um arquivo de áudio enviado.
 * @param {{ buffer: Buffer, mimetype: string }} audio
 * @returns {Promise<string|null>} Texto transcrito ou null
 */
export async function transcribeAudio(audio) {
  if (!isSpeechConfigured()) {
    throw new ExternalAPIError('Credenciais do Google Cloud Speech não configuradas.')
  }

  let speech
  try {
    // Nome do módulo em variável: impede o bundler de resolver o pacote no
    // build (é uma dependência opcional). Em runtime, se estiver instalado,
    // o import resolve normalmente.
    const pkg = ['@google-cloud', 'speech'].join('/')
    ;({ default: speech } = await import(/* @vite-ignore */ pkg))
  } catch {
    throw new ExternalAPIError(
      'Serviço de transcrição de áudio não está configurado (instale @google-cloud/speech).'
    )
  }

  try {
    const client = new speech.SpeechClient()
    const [response] = await client.recognize({
      audio: { content: audio.buffer.toString('base64') },
      config: {
        encoding: 'WEBM_OPUS',
        languageCode: 'pt-BR',
        enableAutomaticPunctuation: true,
      },
    })

    if (response.results?.length) {
      return response.results[0].alternatives[0].transcript
    }
    return null
  } catch (error) {
    throw new ExternalAPIError(`Erro ao processar áudio: ${error.message}`)
  }
}
