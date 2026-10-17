/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // A transcrição de áudio usa o @google-cloud/speech de forma opcional
  // (import dinâmico). Marcamos como externo para o Next não tentar resolver
  // no build quando o pacote não está instalado.
  serverExternalPackages: ['@google-cloud/speech'],
}

export default nextConfig
