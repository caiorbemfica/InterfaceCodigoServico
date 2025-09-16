import logging
from app.firebase import db
from google.cloud import firestore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def gerar_codigo_servico(produto_codigo: str, opcao: str, menu: str, ura: str, db):
    try:
        produto_numero = produto_codigo.rstrip('_')

        # Buscar o número do menu existente ou gerar novo
        menu_numero = get_menu_number(ura, menu, db)
        
        # Buscar última opção do menu
        ultima_opcao = get_last_option_number(db, ura, menu)
        opcao_numero = ultima_opcao + 1

        # Gerar novo código
        if menu_numero < 100:
            novo_codigo = f"1_{produto_numero}{menu_numero:02d}{opcao_numero:02d}"
        else:
            novo_codigo = f"1_{produto_numero}{menu_numero:03d}{opcao_numero:03d}"

        codigo_servico_produto = f"{novo_codigo}_{opcao}"
        
        return novo_codigo, codigo_servico_produto

    except Exception as e:
        logger.error(f"Erro ao gerar código do serviço: {e}")
        raise

def get_menu_number(ura: str, menu: str, db):
    try:
        # Buscar serviços com a mesma URA e menu
        query = db.collection('precificacao') \
                 .where('ura', '==', ura) \
                 .where('menu', '==', menu) \
                 .get()

        # Se encontrar o menu, retorna seu número
        for doc in query:
            codigo = doc.to_dict().get('codigo', '')
            if codigo and len(codigo.split('_')) >= 2:
                partes = codigo.split('_')[1]
                menu_num = partes[2:4] if len(partes) == 6 else partes[2:5]
                return int(menu_num)

        # Se não encontrar, busca o último número de menu usado
        query = db.collection('precificacao') \
                 .where('ura', '==', ura) \
                 .get()

        max_menu = 0
        for doc in query:
            codigo = doc.to_dict().get('codigo', '')
            if codigo and len(codigo.split('_')) >= 2:
                partes = codigo.split('_')[1]
                menu_num = partes[2:4] if len(partes) == 6 else partes[2:5]
                try:
                    max_menu = max(max_menu, int(menu_num))
                except ValueError:
                    continue

        return max_menu + 1

    except Exception as e:
        logger.error(f"Erro ao obter número do menu: {e}")
        raise

def get_last_option_number(db, ura, menu):
    """
    Obtém o último número de opção usado para um determinado menu em uma URA
    """
    try:
        # Busca todos os serviços do menu específico
        servicos = db.collection('servicos') \
            .where('ura', '==', ura) \
            .where('menu', '==', menu) \
            .get()

        # Se não houver serviços, retorna 0
        if not servicos:
            return 0

        # Extrai os números das opções existentes
        numeros = []
        for servico in servicos:
            dados = servico.to_dict()
            opcao = dados.get('opcao', '')
            # Extrai o número da opção (assumindo formato tipo 'H-1', 'D-2', etc)
            if '-' in opcao:
                numero_str = opcao.split('-')[1]
                try:
                    numero = int(numero_str)
                    numeros.append(numero)
                except ValueError:
                    continue

        # Retorna o maior número encontrado, ou 0 se não houver números
        return max(numeros) if numeros else 0

    except Exception as e:
        print(f"Erro ao obter último número de opção: {str(e)}")
        return 0

def gerar_codigo_produto(last_codigo: str) -> str:
    if not last_codigo:
        return "01_"
    
    last_num = int(last_codigo.split('_')[0])
    new_num = last_num + 1
    new_codigo = f"{new_num:02d}_"
    return new_codigo