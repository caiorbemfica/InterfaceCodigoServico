# app/dashboard.py
from app.firebase import get_servicos
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def obter_estatisticas_dashboard():
    try:
        servicos = get_servicos()
        temas = {}
        tipos = {'H': 0, 'D': 0, 'S': 0}

        for servico in servicos:
            data = servico.to_dict()
            tema = data.get('produto', 'Desconhecido')
            tipo = data.get('configuracao', '').upper()

            # Contagem de temas
            if tema not in temas:
                temas[tema] = 0
            temas[tema] += 1

            # Contagem por tipo de serviço
            if tipo in tipos:
                tipos[tipo] += 1

        return {"temas": temas, "tipos": tipos}
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise