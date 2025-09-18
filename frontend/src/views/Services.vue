<template>
  <div class="w-full p-4 lg:p-6">
    <h2 class="text-3xl font-bold text-[#003641] mb-6">Consulta de Serviços</h2>
    <div v-if="!isLoading" class="space-y-6">
      <button @click="$router.push('/create-service')" class="bg-[#1fa193] text-white p-3 rounded-lg">
      Criar Serviço
    </button>
      <!-- Campo de busca por código -->
      <div class="mb-4 flex gap-4">
        <div class="flex-1">
          <input
            v-model="filtroCodigo"
            @keyup.enter="buscarPorCodigo"
            placeholder="Digite o código do serviço (ex.: 1_080001)"
            class="border border-[#75b62f] p-3 w-full rounded-lg focus:ring-2 focus:ring-[#1fa193] focus:border-transparent"
          />
        </div>
        <button
          @click="buscarPorCodigo"
          class="bg-[#1fa193] text-white p-3 rounded-lg hover:bg-[#00ae9d] transition duration-200"
        >
          Buscar
        </button>
        <button
          v-if="filtroCodigo"
          @click="limparBusca"
          class="bg-red-500 text-white p-3 rounded-lg hover:bg-red-600 transition duration-200"
        >
          Limpar
        </button>
      </div>
      <!-- Filtros existentes -->
      <div class="mb-4 flex flex-col sm:flex-row gap-4">
        <select
          v-model="filtroProduto"
          @change="updateMenus"
          class="border border-[#75b62f] p-3 rounded-lg focus:ring-2 focus:ring-[#1fa193] focus:border-transparent"
          :disabled="!!filtroCodigo"
        >
          <option value="">Todos os Produtos</option>
          <option v-for="produto in produtos" :key="produto" :value="produto">{{ produto }}</option>
        </select>
        <select
          v-model="filtroMenu"
          class="w-full border border-[#75b62f] p-3 rounded-lg focus:ring-2 focus:ring-[#1fa193] focus:border-transparent"
          :disabled="!filtroProduto || !!filtroCodigo"
        >
          <option value="">Todos os Menus</option>
          <option v-if="!filtroProduto" disabled value="">Selecione primeiro um produto para ver os menus referentes</option>
          <option v-for="menu in menusUnicos" :key="menu" :value="menu">{{ menu }}</option>
        </select>
        <button
          @click="exportCSV"
          class="bg-[#75b62f] text-white p-3 rounded-lg hover:bg-[#1fa193] transition duration-200"
        >
          Exportar CSV
        </button>
      </div>
      <div class="bg-white p-6 rounded-lg shadow-md">
        <table class="w-full border-collapse">
          <thead>
            <tr class="bg-[#75b62f] text-white">
              <th class="border border-[#75b62f] p-3 font-semibold">URA</th>
              <th class="border border-[#75b62f] p-3 font-semibold">Caminho</th>
              <th class="border border-[#75b62f] p-3 font-semibold">Código</th>
              <th class="border border-[#75b62f] p-3 font-semibold">Produto</th>
              <th class="border border-[#75b62f] p-3 font-semibold">Menu</th>
              <th class="border border-[#75b62f] p-3 font-semibold">Submenu</th>
              <th class="border border-[#75b62f] p-3 font-semibold">Opção</th>
              <th class="border border-[#75b62f] p-3 font-semibold">Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="servico in filteredServicos" :key="servico.codigo_servico_produto" class="hover:bg-gray-50">
              <td class="border border-[#75b62f] p-1 text-[#003641]">{{ servico.ura }}</td>
              <td class="border border-[#75b62f] p-1 text-[#003641]">{{ servico.caminho }}</td>
              <td class="border border-[#75b62f] p-1 text-[#003641]">{{ servico.codigo_servico_produto }}</td>
              <td class="border border-[#75b62f] p-1 text-[#003641]">{{ servico.produto }}</td>
              <td class="border border-[#75b62f] p-1 text-[#003641]">{{ servico.menu }}</td>
              <td class="border border-[#75b62f] p-1 text-[#003641]">{{ servico.submenu }}</td>
              <td class="border border-[#75b62f] p-1 text-[#003641]">{{ servico.opcao }}</td>
              <td class="border border-[#75b62f] p-1">
                <button @click="editServico(servico)" class="text-[#1fa193] mr-2 hover:underline">Editar</button>
                <button @click="deleteServico(servico.codigo_servico_produto as string)" class="text-red-500 hover:underline">Excluir</button>
              </td>
            </tr>
            <tr v-if="filteredServicos.length === 0">
              <td colspan="6" class="border border-[#75b62f] p-3 text-center text-[#003641] text-lg">Nenhum serviço encontrado</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-else class="flex justify-center items-center h-full">
      <div class="loader"></div>
    </div>

    <!-- Modal de Exclusão -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
        <h3 class="text-xl font-bold text-[#003641] mb-4">
          Confirmar Exclusão
        </h3>
        <p class="text-gray-700 mb-6">
          Tem certeza que deseja excluir o serviço com o código: 
          <span class="font-bold">{{ servicoParaExcluir }}</span>?
        </p>
        <div class="flex gap-4">
          <button 
            @click="confirmarExclusao" 
            class="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 w-full"
          >
            Excluir
          </button>
          <button 
            @click="cancelarExclusao" 
            class="bg-[#1fa193] text-white px-4 py-2 rounded-lg hover:bg-opacity-90 w-full"
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch } from 'vue'
import { cache } from '@/servicesCache'
import axios from 'axios'
import Papa from 'papaparse'
import { Servico } from '@/types'

export default defineComponent({
  name: 'Services',
  setup() {
    const isLoading = ref(false)

    return { isLoading }
  },
  data() {
    return {
      produtos: [] as string[],
      servicos: [] as Servico[],
      filtroProduto: '',
      filtroMenu: '',
      filtroCodigo: '',
      servicoPorCodigo: null as Servico | null, // Armazena o serviço retornado pela busca por código
      cacheTimestamp: 0,
      cacheDuration: 5 * 60 * 1000,
      showDeleteModal: false,
      servicoParaExcluir: '',
    }
  },
  computed: {
    menusUnicos(): string[] {
      console.log('filtroProduto:', this.filtroProduto)
      if (!this.filtroProduto) {
        return []
      }
      return [...new Set(this.servicos
        .filter(s => s.produto === this.filtroProduto)
        .map(s => s.menu))].sort()
    },
    filteredServicos(): Servico[] {
      console.log('Filtrando com filtroProduto:', this.filtroProduto, 'filtroMenu:', this.filtroMenu, 'filtroCodigo:', this.filtroCodigo)
      // Se houver um filtro por código, exibe apenas o serviço retornado
      if (this.filtroCodigo && this.servicoPorCodigo) {
        return [this.servicoPorCodigo]
      }
      if (this.filtroCodigo && !this.servicoPorCodigo) {
        return []
      }
      // Caso contrário, aplica a filtragem padrão por produto e menu
      if (!this.filtroProduto && !this.filtroMenu) {
        console.log('Nenhum filtro, retornando todos os serviços:', this.servicos.length)
        return this.servicos
      }
      const filtered = this.servicos.filter(s => {
        const matchesProduct = !this.filtroProduto || s.produto === this.filtroProduto
        const matchesMenu = !this.filtroMenu || s.menu === this.filtroMenu
        console.log('Serviço:', s, 'matchesProduct:', matchesProduct, 'matchesMenu:', matchesMenu)
        return matchesProduct && matchesMenu
      })
      console.log('filteredServicos:', filtered.length)
      return filtered
    },
  },
  watch: {
    filtroProduto(newValue) {
      if (newValue) {
        this.filtroMenu = ''
      }
    },
  },
  async mounted() {
  // 1️⃣ Carrega do cache em memória, se houver
  if (Date.now() - cache.lastFetch < this.cacheDuration && cache.servicos.length > 0) {
    this.servicos = cache.servicos
    this.produtos = cache.produtos
    console.log('Dados carregados do cache em memória')
    return
  }

  // 2️⃣ Carrega do localStorage se memória estiver vazia
  const cachedServicos = localStorage.getItem('cachedServicos')
  const cachedProdutos = localStorage.getItem('cachedProdutos')
  const cachedTimestamp = localStorage.getItem('cacheTimestamp')

  if (cachedServicos && cachedProdutos && cachedTimestamp) {
    const timestamp = parseInt(cachedTimestamp, 10)
    if (Date.now() - timestamp < this.cacheDuration) {
      this.servicos = JSON.parse(cachedServicos)
      this.produtos = JSON.parse(cachedProdutos)
      cache.servicos = this.servicos
      cache.produtos = this.produtos
      cache.lastFetch = timestamp
      console.log('Dados carregados do localStorage')
      return
    }
  }

  // 3️⃣ Se cache vazio ou expirado, chama API
  this.isLoading = true
  try {
    const res = await axios.get('http://127.0.0.1:8000/servicos', { timeout: 30000 })
    this.servicos = res.data
    this.produtos = [...new Set(this.servicos.map(s => s.produto))].sort()

    // atualiza cache em memória
    cache.servicos = this.servicos
    cache.produtos = this.produtos
    cache.lastFetch = Date.now()

    // atualiza localStorage
    localStorage.setItem('cachedServicos', JSON.stringify(this.servicos))
    localStorage.setItem('cachedProdutos', JSON.stringify(this.produtos))
    localStorage.setItem('cacheTimestamp', cache.lastFetch.toString())

    console.log('Dados carregados da API')
    } catch (error: any) {
      console.error('Erro ao carregar dados:', error)
      alert('Erro ao carregar dados: ' + error.message)
    } finally {
      this.isLoading = false
    }
  },
  methods: {
    async buscarPorCodigo() {
      if (!this.filtroCodigo) {
        this.servicoPorCodigo = null
        return
      }
      this.isLoading = true
      try {
        const response = await axios.get<Servico[]>(`http://127.0.0.1:8000/servico/${this.filtroCodigo}`, { timeout: 30000 })
        this.servicoPorCodigo = response.data[0] || null
        if (!this.servicoPorCodigo) {
          alert('Nenhum serviço encontrado para o código informado.')
        }
      } catch (error: any) {
        console.error('Erro ao buscar serviço por código:', error)
        this.servicoPorCodigo = null
        if (error.response?.status === 404) {
          alert('Nenhum serviço encontrado para o código informado.')
        } else if (error.response?.status === 429) {
          alert('Quota excedida ao buscar serviço. Tente novamente mais tarde.')
        } else {
          alert('Erro ao buscar serviço: ' + error.message)
        }
      } finally {
        this.isLoading = false
      }
    },
    limparBusca() {
      this.filtroCodigo = ''
      this.servicoPorCodigo = null
      this.filtroProduto = ''
      this.filtroMenu = ''
    },
    editServico(servico: Servico) {
      this.$router.push({ name: 'CreateService', query: { edit: servico.codigo_servico_produto } })
    },
    async deleteServico(codigo: string) {
      this.servicoParaExcluir = codigo
      this.showDeleteModal = true
    },
    async confirmarExclusao() {
      this.isLoading = true
      try {
        await axios.delete(`http://127.0.0.1:8000/servico/${this.servicoParaExcluir}`, { timeout: 30000 })
        this.servicos = this.servicos.filter(s => s.codigo_servico_produto !== this.servicoParaExcluir)
        this.produtos = [...new Set(this.servicos.map(s => s.produto))].sort()
        localStorage.setItem('cachedServicos', JSON.stringify(this.servicos))
        localStorage.setItem('cachedProdutos', JSON.stringify(this.produtos))
        
        if (this.servicoPorCodigo && this.servicoPorCodigo.codigo_servico_produto === this.servicoParaExcluir) {
          this.limparBusca()
        }
      } catch (error: any) {
        if (error.response?.status === 429) {
          alert('Quota excedida ao excluir serviço. Tente novamente mais tarde.')
        } else {
          alert('Erro ao excluir o serviço: ' + error.message)
        }
      } finally {
        this.isLoading = false
        this.showDeleteModal = false
        this.servicoParaExcluir = ''
      }
    },
    cancelarExclusao() {
      this.showDeleteModal = false
      this.servicoParaExcluir = ''
    },
    exportCSV() {
      const csv = Papa.unparse(this.filteredServicos)
      const blob = new Blob([csv], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'servicos.csv'
      a.click()
    },
    updateMenus() {
      this.filtroMenu = ''
    },
  },
})
</script>

<style scoped>
.loader {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #1fa193;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>