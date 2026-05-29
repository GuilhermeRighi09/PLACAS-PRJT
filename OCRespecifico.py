import easyocr
import re

print("Iniciando o leitor EasyOCR Específico...")
leitor = easyocr.Reader(['en'])
padrao_placa = re.compile(r'[A-Z]{3}[0-9][A-Z0-9][0-9]{2}')

def ler_especifico(caminho_imagem):
    resultados = leitor.readtext(caminho_imagem)
    textos_encontrados = []

    for (caixa, texto, confianca) in resultados:
        texto_limpo = texto.upper().replace(" ", "").replace("-", "")
        if len(texto_limpo) > 2:
            textos_encontrados.append(texto_limpo)

        busca = padrao_placa.search(texto_limpo)
        if busca:
            placa_exata = busca.group()
            # Retorna apenas o ícone e a placa, sem conferência
            return f"✅ {placa_exata}"

    if textos_encontrados:
        return f"❌ Padrão não encontrado. Brutos: {', '.join(textos_encontrados)}"
    return "❌ Placa não detectada"