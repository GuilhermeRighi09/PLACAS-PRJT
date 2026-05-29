import easyocr

print("Carregando o modelo do EasyOCR Normal...")
leitor = easyocr.Reader(['en'])

def ler_normal(caminho_imagem):
    resultados = leitor.readtext(caminho_imagem)
    if len(resultados) == 0:
        return "Nenhum texto encontrado."

    # Pega apenas o texto, sem a confiança (porcentagem)
    textos_lidos = [res[1].upper() for res in resultados]
    return " | ".join(textos_lidos)