// src/servicesCache.ts
import type { Servico } from '@/types'

export const cache = {
  servicos: [] as Servico[],
  produtos: [] as string[],
  lastFetch: 0, // timestamp do último fetch
}
