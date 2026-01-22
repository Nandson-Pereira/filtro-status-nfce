import os
import xml.etree.ElementTree as ET
import shutil

# --- Configurações ---
# O diretório base onde o script está.
DIRETORIO_BASE = r'C:\Users\nandson.silva\Desktop\filtro status'
# Subdiretório onde estão os XMLs originais.
DIRETORIO_XMLS = os.path.join(DIRETORIO_BASE, 'xmls')
# Subdiretórios de destino.
DIRETORIO_AUTORIZADA = os.path.join(DIRETORIO_XMLS, 'AUTORIZADA')
DIRETORIO_INUTILIZADA = os.path.join(DIRETORIO_XMLS, 'INUTILIZADA')
# NOVO DIRETÓRIO
DIRETORIO_CANCELADA = os.path.join(DIRETORIO_XMLS, 'CANCELADA')

# Namespace da NFe/NFCe. Crucial para o parser XML encontrar as tags corretas.
NAMESPACE = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

# --- Funções ---

def buscar_status_xml(caminho_arquivo):
    """
    Busca o código de status (cStat) dentro do XML da NFC-e.
    """
    try:
        # Tenta fazer a análise do XML
        tree = ET.parse(caminho_arquivo)
        root = tree.getroot()

        # Caminho XPATH para o código de status (cStat)
        cStat_element = root.find('.//nfe:cStat', NAMESPACE)

        if cStat_element is not None:
            return cStat_element.text
        else:
            # Em alguns casos, o cStat pode estar em uma estrutura de evento (como no cancelamento)
            # Mas geralmente, para a NFe/NFCe processada, ele fica em protNFe/infProt/cStat.
            return None

    except ET.ParseError:
        # Ignora arquivos que não são XMLs válidos ou estão corrompidos
        return None
    except Exception:
        # Ignora outros erros inesperados
        return None

def organizar_xmls():
    """
    Percorre o diretório de XMLs e move os arquivos para as pastas de destino
    baseado no valor da tag <cStat>.
    """
    if not os.path.exists(DIRETORIO_XMLS):
        print(f"🛑 Erro: O diretório de origem '{DIRETORIO_XMLS}' não foi encontrado.")
        print("Crie a pasta 'xmls' dentro do diretório base.")
        return

    # Cria os diretórios de destino se não existirem
    os.makedirs(DIRETORIO_AUTORIZADA, exist_ok=True)
    os.makedirs(DIRETORIO_INUTILIZADA, exist_ok=True)
    os.makedirs(DIRETORIO_CANCELADA, exist_ok=True) # Cria a nova pasta
    
    contador_total = 0
    contador_movido = 0
    
    print(f"Iniciando a organização de XMLs em '{DIRETORIO_XMLS}'...")
    print(f"Arquivos com cStat 100 ou 150 serão movidos para 'AUTORIZADA'.")
    print(f"Arquivos com cStat 102 serão movidos para 'INUTILIZADA'.")
    print(f"Arquivos com cStat 135 serão movidos para 'CANCELADA'.\n")

    # Lista os itens do diretório, filtrando arquivos e ignorando as subpastas
    arquivos_para_processar = [f for f in os.listdir(DIRETORIO_XMLS) 
                               if os.path.isfile(os.path.join(DIRETORIO_XMLS, f)) and f.lower().endswith('.xml')]

    for nome_arquivo in arquivos_para_processar:
        caminho_origem = os.path.join(DIRETORIO_XMLS, nome_arquivo)
        contador_total += 1
        print(f"Processando: {nome_arquivo}...", end="")

        status = buscar_status_xml(caminho_origem)

        if status:
            destino = None
            
            # 100: Autorizada / 150: Autorizada fora de prazo
            if status in ['100', '150']:
                destino = DIRETORIO_AUTORIZADA
                status_descricao = "AUTORIZADA"
            # 102: Inutilização de número homologado
            elif status == '102':
                destino = DIRETORIO_INUTILIZADA
                status_descricao = "INUTILIZADA"
            # NOVO STATUS: 135: Evento de Cancelamento registrado
            elif status == '135':
                destino = DIRETORIO_CANCELADA
                status_descricao = "CANCELADA"
            else:
                print(f" Status: {status} -> IGNORADO/OUTROS 🟡")
                continue
                
            # Realiza a movimentação
            if destino:
                caminho_destino = os.path.join(destino, nome_arquivo)
                shutil.move(caminho_origem, caminho_destino)
                contador_movido += 1
                print(f" Status: {status} ({status_descricao}) -> MOVIDO ✅")

        else:
            # Se status for None (erro de leitura ou tag não encontrada)
            print(" Status: Não encontrado/Erro -> IGNORADO ⚠️⚠️⚠️⚠️⚠️")

    print("\n--- Concluído ---")
    print(f"Total de XMLs processados: {contador_total}")
    print(f"Total de XMLs movidos: {contador_movido}")
    print("Os arquivos com status diferentes de 100, 150, 102 e 135 permanecem na pasta 'xmls'.")

# Execução do script
if __name__ == "__main__":
    organizar_xmls()