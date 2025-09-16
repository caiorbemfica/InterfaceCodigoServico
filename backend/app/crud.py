# app/crud.py
from app.firebase import db
from app.utils import gerar_codigo_produto, gerar_codigo_servico
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
def adicionar_servico(servico_data):
    try:
        # Verifica se já existe um serviço com o mesmo código_servico_produto
        docs = db.collection('precificacao').stream()
        codigos_existentes = [doc.to_dict().get('codigo_servico_produto', '') for doc in docs]
        
        # Gera o código do serviço
        codigo = gerar_codigo_servico(
            db=db,
            ura=servico_data['ura'],
            menu=servico_data['menu']
        )
        
        # Adiciona o código ao dicionário de dados do serviço
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

        doc_ref = docs[0].reference
        doc_atual = docs[0].to_dict()
        servico_data = servico.dict()

        # Mantém o código original do serviço
        servico_data['codigo'] = doc_atual['codigo']
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