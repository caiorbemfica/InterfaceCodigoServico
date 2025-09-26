// src/servicesCache.ts
import axios from 'axios'
import type { Servico, Produto } from '@/types'

export const cache = {
  servicos: [] as Servico[],
  produtos: [] as Produto[],
  lastFetchServicos: 0, // timestamp do último fetch de serviços
  lastFetchProdutos: 0, // timestamp do último fetch de produtos
}

// Busca produtos com cache (expira em 5 minutos)
export async function getProdutos(): Promise<Produto[]> {
  const CACHE_DURATION_MS = 5 * 60 * 1000

  if (cache.produtos.length > 0 && (Date.now() - cache.lastFetchProdutos) < CACHE_DURATION_MS) {
    return cache.produtos
  }

  try {
    const response = await axios.get<Produto[]>('http://127.0.0.1:8000/produtos')
    cache.produtos = response.data
    cache.lastFetchProdutos = Date.now()
    return cache.produtos
  } catch (error) {
    console.error('Erro ao buscar produtos:', error)
    return cache.produtos
  }
}

// Invalida o cache de produtos (chamar após criar/editar/excluir produto)
export function invalidateProdutosCache(): void {
  cache.produtos = []
  cache.lastFetchProdutos = 0
}
