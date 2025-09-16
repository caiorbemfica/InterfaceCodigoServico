from pydantic import BaseModel, validator
from typing import Optional

class Produto(BaseModel):
    codigo: Optional[str] = None  # Agora o código é opcional na entrada
    nome: str

    @validator('codigo', pre=True, always=True)
    def validate_codigo(cls, v):
        if v is None:  # Permite que o código seja gerado automaticamente
            return v
        if not v.endswith('_'):
            raise ValueError("Código do produto deve terminar com '_'.")
        return v

class ProdutoCreate(BaseModel):
    nome: str


class ProdutoResponse(BaseModel):  # Adicione esta classe
    mensagem: str
    produto: Produto

class Servico(BaseModel):
    ura: str
    caminho: str  # Alterado para str
    produto: str
    menu: str
    submenu: str
    configuracao: str  # Sem validação
    opcao: str
    codigo: Optional[str] = None  # Novo campo para armazenar apenas "08_000001"
    codigo_servico_produto: Optional[str] = None
    tema: Optional[str] = None