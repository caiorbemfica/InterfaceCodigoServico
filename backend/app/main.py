from fastapi import FastAPI
from fastapi import HTTPException
from app.firebase import db  # Importe o db do firebase.py
from app.firebase import get_servicos
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.models import ProdutoResponse
from app.models import ProdutoCreate, Servico, Produto  # Importação corrigida
from app.crud import (
    consultar_produtos, consultar_servicos, consultar_servico_por_codigo,
    adicionar_produto, adicionar_servico, excluir_servico_por_codigo, excluir_servico_por_opcao, editar_servico
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configuração do middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Permite requisições do frontend Vue
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

#Retorna todos os produtos
@app.get("/produtos", response_model=list[Produto])
def get_produtos():
    try:
        return consultar_produtos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#Adiciona um novo produto
@app.post("/produtos", response_model=ProdutoResponse)
def post_produto(produto: ProdutoCreate):
    try:
        novo_produto = adicionar_produto(produto.nome)
        return {"mensagem": "Produto adicionado com sucesso", "produto": novo_produto}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Retorna todos os serviços (dados brutos)
@app.get("/servicos")
def listar_servicos():  # Renomeie a função para evitar conflito
    try:
        servicos = get_servicos()  # Chama a função do firebase.py
        return servicos
    except Exception as e:
        logger.error(f"Erro ao consultar serviços: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
# Obter um serviço pelo código
@app.get("/servico/{codigo}")
def get_servico(codigo: str):
    try:
        servicos = consultar_servico_por_codigo(codigo)
        return servicos
    except Exception as e:
        logger.error(f"Erro ao buscar serviço por código: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Função para adicionar serviço na tabela precificacao
@app.post("/servicos")
async def criar_servico(servico: dict):
    return adicionar_servico(servico)

# Excluir um serviço pelo código
@app.delete("/servico/{codigo_servico_produto}")
def delete_servico(codigo_servico_produto: str):
    try:
        excluir_servico_por_codigo(codigo_servico_produto)
        return {"status": "success", "message": f"Serviço com código {codigo_servico_produto} excluído."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/servico/opcao/{opcao}")
def delete_servico_por_opcao(opcao: str):
    try:
        excluir_servico_por_opcao(opcao)
        return {"status": "success", "message": f"Serviço com opção {opcao} excluído."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Edita um serviço pelo código
@app.put("/servico/{codigo_servico_produto}", response_model=Servico)
def update_servico(codigo_servico_produto: str, servico: Servico):
    try:
        updated_servico = editar_servico(codigo_servico_produto, servico, db)
        if updated_servico is None:
            raise HTTPException(status_code=404, detail=f"Serviço com código {codigo_servico_produto} não encontrado.")
        return updated_servico
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/menus/{ura}")
def get_menus_by_ura(ura: str):
    try:
        servicos_ref = db.collection('precificacao')
        query = servicos_ref.where('ura', '==', ura).get()
        menus = list(set(doc.to_dict()['menu'] for doc in query))
        return sorted(menus)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)