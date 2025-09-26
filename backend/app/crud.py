# app/crud.py
from app.firebase import db
from app.utils import gerar_codigo_produto
from app.firebase import (
    get_produtos, get_servicos, get_servico_by_codigo, delete_servico_by_codigo,
    delete_servico_by_opcao, add_produto_to_firestore, add_servico_to_firestore, update_servico_in_firestore
)
from app.models import Servico, Produto
import logging
from fastapi import HTTPException
import math

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def consultar_produtos():
    try:
        produtos = get_produtos()
        return [Produto(**produto) for produto in produtos]
    except Exception as e:
        logger.error(f"Erro ao consultar produtos: {e}")
        raise

def adicionar_produto(nome: str):
    try:
        produtos_ref = db.collection("produto")
        produtos = produtos_ref.order_by("codigo", direction="DESCENDING").limit(1).stream()
        
        last_codigo = None
        for prod in produtos:
            last_codigo = prod.to_dict().get("codigo")
        
        if not last_codigo:
            last_codigo = "00_"  # Começa com "00_" se não houver produtos

        novo_codigo = gerar_codigo_produto(last_codigo)
        novo_produto = Produto(codigo=novo_codigo, nome=nome)

        produtos_ref.document().set(novo_produto.dict())
        return novo_produto
    except Exception as e:
        logger.error(f"Erro ao adicionar produto: {e}")
        raise

def consultar_servicos():
    try:
        servicos = get_servicos()  # Chama a função do firebase.py
        return [Servico(**servico) for servico in servicos]  # Converte para o modelo Servico
    except Exception as e:
        logger.error(f"Erro ao consultar serviços: {e}")
        raise

# Obter um serviço pelo código
def consultar_servico_por_codigo(codigo: str):
    try:
        servicos = get_servico_by_codigo(codigo)
        
        # Validar e limpar os dados antes de retornar
        for servico in servicos:
            for key, value in servico.items():
                # Substituir valores NaN por None
                if isinstance(value, float) and math.isnan(value):
                    servico[key] = None
                # Garantir que strings não sejam None
                elif value is None and isinstance(servico.get(key, ''), str):
                    servico[key] = ''
        
        return servicos
    except Exception as e:
        logger.error(f"Erro ao consultar serviço por código: {e}")
        raise

# Função para adicionar serviço na tabela precificacao
def _extrair_codigo_triple(codigo: str):
    # Espera formato: "1_" + 6 dígitos (pp mm oo)
    try:
        if isinstance(codigo, str) and codigo.startswith('1_'):
            resto = codigo[2:]
            if len(resto) >= 6 and resto[:6].isdigit():
                prod2 = resto[:2]
                menu2 = resto[2:4]
                opt2 = resto[4:6]
                return prod2, menu2, opt2
    except Exception:
        pass
    return None, None, None

def _gerar_codigo_servico_triplo(db, produto_codigo: str, menu_nome: str | None):
    # produto_codigo esperado como "NN_" (ex: "10_") ou algo que permita extrair NN
    prod2 = ''
    if isinstance(produto_codigo, str):
        # tenta XX_ -> XX
        if len(produto_codigo) >= 2 and produto_codigo[:2].isdigit():
            prod2 = produto_codigo[:2]
        else:
            # caso venha nome, não temos como inferir; default 00
            prod2 = '00'
    else:
        prod2 = '00'

    # Varre a coleção e coleta códigos válidos do mesmo produto
    docs = db.collection('precificacao').stream()
    codigos_mesmo_produto = []
    codigos_mesmo_menu = []
    for doc in docs:
        d = doc.to_dict()
        cod = d.get('codigo', '') or d.get('codigo_servico_produto', '')
        mnome = d.get('menu', '')
        p = d.get('produto', '')
        p2, m2, o2 = _extrair_codigo_triple(cod)
        if p2 == prod2:
            codigos_mesmo_produto.append((m2, o2, cod, mnome))
            if menu_nome and isinstance(menu_nome, str) and mnome == menu_nome:
                codigos_mesmo_menu.append((m2, o2, cod))

    # Se menu fornecido → usa mesmo menu2 e incrementa opção
    if menu_nome:
        # tenta descobrir menu2 a partir dos códigos existentes do mesmo menu
        menu2_existente = None
        max_opt = 0
        for m2, o2, _ in codigos_mesmo_menu:
            if m2 and o2 and o2.isdigit():
                max_opt = max(max_opt, int(o2))
                # assume que todos do mesmo menu têm o mesmo m2; captura o primeiro não nulo
                if not menu2_existente and m2.isdigit():
                    menu2_existente = m2
        if not menu2_existente:
            # menu novo para esse produto: descobrir o próximo menu2
            max_menu = 0
            for m2, _, _, _ in codigos_mesmo_produto:
                if m2 and m2.isdigit():
                    max_menu = max(max_menu, int(m2))
            menu2_existente = f"{max_menu + 1:02d}"
            max_opt = 0
        opt2_novo = f"{max_opt + 1:02d}"
        return f"1_{prod2}{menu2_existente}{opt2_novo}"

    # Sem menu fornecido (criando novo menu): pega maior menu e incrementa; opção inicia em 01
    max_menu = 0
    for m2, _, _, _ in codigos_mesmo_produto:
        if m2 and m2.isdigit():
            max_menu = max(max_menu, int(m2))
    novo_menu2 = f"{max_menu + 1:02d}"
    return f"1_{prod2}{novo_menu2}01"


def adicionar_servico(servico_data):
    try:
        # Verifica se já existe um serviço com o mesmo código_servico_produto
        docs = db.collection('precificacao').stream()
        codigos_existentes = [doc.to_dict().get('codigo_servico_produto', '') for doc in docs]
        
        # Gera o código do serviço no formato 1_PPMMOO
        codigo = _gerar_codigo_servico_triplo(
            db=db,
            produto_codigo=servico_data.get('produto', ''),
            menu_nome=servico_data.get('menu', '') or None,
        )
        servico_data['codigo'] = codigo
        
        # Gera o código_servico_produto
        novo_codigo_servico_produto = f"{codigo}_{servico_data['opcao']}"
        
        # Verifica se o código_servico_produto já existe
        if novo_codigo_servico_produto in codigos_existentes:
            raise ValueError(f"Já existe um serviço com o código {novo_codigo_servico_produto}")
        
        servico_data['codigo_servico_produto'] = novo_codigo_servico_produto
        
        # Adiciona o documento ao Firestore
        doc_ref = db.collection('precificacao').document(codigo)
        doc_ref.set(servico_data)
        
        return servico_data
        
    except Exception as e:
        logger.error(f"Erro ao adicionar serviço: {str(e)}")
        raise

# Excluir um serviço pelo código
def excluir_servico_por_codigo(codigo_servico: str):
    try:
        delete_servico_by_codigo(codigo_servico)  # Passa o código corretamente
    except Exception as e:
        logger.error(f"Erro ao excluir serviço por código: {e}")
        raise

def excluir_servico_por_opcao(opcao: str):
    try:
        delete_servico_by_opcao(opcao)
    except Exception as e:
        logger.error(f"Erro ao excluir serviço por opção: {e}")
        raise

def editar_servico(codigo_servico_produto: str, servico: Servico, db):
    try:
        servicos_ref = db.collection('precificacao')
        query = servicos_ref.where('codigo_servico_produto', '==', codigo_servico_produto)
        docs = query.get()

        if not docs:
            logger.error(f"Serviço não encontrado: {codigo_servico_produto}")
            raise HTTPException(status_code=404, detail="Serviço não encontrado")

        doc_snapshot = docs[0]
        doc_ref = doc_snapshot.reference
        doc_atual = doc_snapshot.to_dict()
        # Alguns documentos antigos podem não ter o campo 'codigo' persistido; usa o id do documento como fallback
        codigo_existente = doc_atual.get('codigo') if isinstance(doc_atual, dict) else None
        if not codigo_existente:
            try:
                codigo_existente = doc_snapshot.id  # id do documento no Firestore
            except Exception:
                codigo_existente = None
        servico_data = servico.dict()

        # Mantém o código original do serviço
        # 'codigo' é opcional: só atualiza se existir algum valor conhecido
        if codigo_existente:
            servico_data['codigo'] = codigo_existente
        elif 'codigo' in servico_data and not servico_data['codigo']:
            # remove o campo vazio para não sobrescrever no Firestore
            servico_data.pop('codigo', None)
        servico_data['codigo_servico_produto'] = doc_atual['codigo_servico_produto']

        # Limpar valores NaN
        for key, value in servico_data.items():
            if isinstance(value, float) and math.isnan(value):
                servico_data[key] = None
            elif value is None and isinstance(servico_data.get(key, ''), str):
                servico_data[key] = ''

        # Mapeamento de produtos
        produtos = {
            "14_": "URA Prevencao",
            "06_": "URA Coopera",
            "09_": "URA SAC",
            "02_": "Sipag 1.0",
            "12_": "URA CARTOES CRESOL",
            "04_": "Sipag 1.0 e Sipag 2.0",
            "05_": "ADQ Cabal",
            "13_": "URA CARTOES VIP",
            "03_": "Sipag 2.0",
            "10_": "URA CAMBIO",
            "08_": "URA PUC",
            "07_": "URA Coopcerto",
            "11_": "URA CARTOES",
            "01_": "Consorcio"
        }

        # Define o nome do produto
        servico_data['produto'] = produtos.get(servico.produto, servico.produto)

        # Log para debug
        logger.info(f"Atualizando serviço: {codigo_servico_produto}")
        logger.info(f"Dados atualizados: {servico_data}")

        update_servico_in_firestore(doc_ref, servico_data)
        return servico_data
        
    except Exception as e:
        logger.error(f"Erro ao editar serviço: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def gerar_codigo_servico(db, ura, menu):
    """
    Gera um código único para o serviço, garantindo que não haja duplicatas
    """
    try:
        # Extrai o número da URA
        ura_numero = ura.split('.')[0]

        # Busca todos os documentos da coleção precificacao
        docs = db.collection('precificacao').stream()
        
        # Coleta todos os códigos existentes
        codigos_existentes = set()  # Usando set para evitar duplicatas
        for doc in docs:
            dados = doc.to_dict()
            codigo = dados.get('codigo', '')
            if codigo and codigo.startswith(f"{ura_numero}_"):
                codigos_existentes.add(codigo)

        # Se não existirem códigos, começa com 084301
        if not codigos_existentes:
            return f"{ura_numero}_084301"

        # Encontra o maior número existente
        maior_numero = 84300  # valor inicial padrão
        for codigo in codigos_existentes:
            try:
                num = int(codigo.split('_')[1])
                if num > maior_numero:
                    maior_numero = num
            except (IndexError, ValueError):
                continue

        # Gera um novo código incrementando o maior número encontrado
        novo_numero = maior_numero + 1
        novo_codigo = f"{ura_numero}_{novo_numero:06d}"

        # Verifica se o novo código já existe
        while novo_codigo in codigos_existentes:
            novo_numero += 1
            novo_codigo = f"{ura_numero}_{novo_numero:06d}"

        return novo_codigo

    except Exception as e:
        logger.error(f"Erro ao gerar código do serviço: {str(e)}")
        raise