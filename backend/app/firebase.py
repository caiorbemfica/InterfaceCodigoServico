# app/firebase.py
import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging
from google.cloud.firestore_v1 import FieldFilter
import math
from app.models import Servico, Produto

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Caminho do arquivo de credenciais
cred_path = os.path.join(os.path.dirname(__file__), "..", "firebase-sdk.json")

# Inicialização do Firebase
def init_firebase():
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {'projectId': 'precificacaoura'})
        logger.info("Firebase inicializado com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao inicializar Firebase: {e}")
        raise

# Inicializa o Firebase ao importar o módulo
init_firebase()

# Obter uma instância do Firestore
db = firestore.client()

# Obter todos os produtos
def get_produtos():
    try:
        produtos = db.collection('produto').stream()
        produtos_list = [produto.to_dict() for produto in produtos]  # Itera sobre o generator
        logger.info(f"Produtos recuperados: {produtos_list}")

        # Debug extra para verificar a lista
        if not produtos_list:
            logger.warning("Nenhum produto encontrado no Firebase.")

        return produtos_list
    except Exception as e:
        logger.error(f"Erro ao obter produtos: {e}")
        raise

# Função para adicionar produto na tabela produtos
def add_produto_to_firestore(produto: Produto):
    try:
        produtos_ref = db.collection('produto')
        produto_data = produto.dict()
        produtos_ref.add(produto_data)
        logger.info(f"Produto adicionado: {produto_data}")
    except Exception as e:
        logger.error(f"Erro ao adicionar produto: {e}")
        raise

# Obter todos os serviços
def get_servicos():
    try:
        logger.info("Iniciando consulta ao Firestore...")
        servicos = db.collection('precificacao').stream()
        servicos_list = []
        for servico in servicos:
            data = servico.to_dict()
            # Substitui NaN por None
            for key, value in data.items():
                if isinstance(value, float) and math.isnan(value):
                    data[key] = None
            servicos_list.append(data)
        logger.info(f"Serviços recuperados: {servicos_list}")
        return servicos_list
    except Exception as e:
        logger.error(f"Erro ao obter serviços: {e}")
        raise

# Obter um serviço pelo código
def get_servico_by_codigo(codigo: str):
    try:
        # Busca documentos onde o campo "codigo_servico_produto" começa com o código fornecido
        servicos = db.collection('precificacao') \
                     .where('codigo_servico_produto', '>=', codigo) \
                     .where('codigo_servico_produto', '<=', codigo + '\uf8ff') \
                     .stream()
        servicos_list = [servico.to_dict() for servico in servicos]
        logger.info(f"Serviços encontrados para o código {codigo}: {servicos_list}")
        return servicos_list
    except Exception as e:
        logger.error(f"Erro ao buscar serviço por código: {e}")
        raise

# Função para adicionar serviço na tabela precificacao
def add_servico_to_firestore(servico: Servico, db):
    try:
        precificacao_ref = db.collection('precificacao')
        servico_data = servico.dict()
        precificacao_ref.add(servico_data)
        logger.info(f"Serviço adicionado: {servico_data}")
    except Exception as e:
        logger.error(f"Erro ao adicionar serviço: {e}")
        raise

def buscar_ultimo_codigo_por_produto_e_opcao(produto_codigo: str, opcao: str, db):
    try:
        # Remove o '_' do produto_codigo para buscar apenas o prefixo numérico (ex.: "08")
        produto_prefixo = produto_codigo.rstrip('_')
        
        # Busca documentos onde codigo_servico_produto começa com o prefixo do produto
        # e contém a opção, ordenando pelo código de forma descendente
        servicos = db.collection('precificacao') \
                     .where('codigo_servico_produto', '>=', f"{produto_prefixo}_") \
                     .where('codigo_servico_produto', '<=', f"{produto_prefixo}_\uf8ff") \
                     .where(filter=FieldFilter('opcao', '==', opcao)) \
                     .order_by('codigo_servico_produto', direction=firestore.Query.DESCENDING) \
                     .limit(1) \
                     .stream()
        
        # Retorna o último código encontrado
        for servico in servicos:
            return servico.to_dict().get('codigo_servico_produto')
        
        # Se não houver códigos para o produto e a opção, retorna None
        return None
    except Exception as e:
        logger.error(f"Erro ao buscar último código para o produto {produto_codigo} e opção {opcao}: {e}")
        raise

# Excluir um serviço pelo código
def delete_servico_by_codigo(codigo_servico: str):
    try:
        services = db.collection('precificacao').where('codigo_servico_produto', '==', codigo_servico).stream()
        deleted = 0
        for service in services:
            service.reference.delete()
            deleted += 1
        logger.info(f"{deleted} serviço(s) com código {codigo_servico} excluído(s).")
        return deleted  # Retorna o número de serviços excluídos
    except Exception as e:
        logger.error(f"Erro ao excluir serviço por código: {e}")
        raise

# Excluir um serviço pela opção
def delete_servico_by_opcao(opcao: str):
    try:
        services = db.collection('precificacao').where('opcao', '==', opcao).stream()
        deleted = 0
        for service in services:
            service.reference.delete()
            deleted += 1
        logger.info(f"{deleted} serviço(s) com opção {opcao} excluído(s).")
    except Exception as e:
        logger.error(f"Erro ao excluir serviço por opção: {e}")
        raise

def update_servico_in_firestore(doc_ref, servico_data: dict):
    try:
        doc_ref.set(servico_data)
        logger.info(f"Serviço atualizado: {servico_data}")
    except Exception as e:
        logger.error(f"Erro ao atualizar serviço: {e}")
        raise
