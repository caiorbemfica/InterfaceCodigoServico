<template>
  <div class="w-full p-4 lg:p-6">
    <h2 class="text-3xl font-bold text-[#003641] mb-6">Gestão de Produtos</h2>
    <div v-if="!isLoading" class="space-y-8">
      <!-- Formulário para criar novo produto -->
      <div class="bg-white p-6 rounded-lg shadow-md">
        <h3 class="text-xl font-semibold text-[#003641] mb-4">Adicionar Novo Produto</h3>
        <form @submit.prevent="createProduct" class="space-y-4">
          <div>
            <label class="block text-[#003641] font-medium mb-2">Nome do Produto:</label>
            <input
              v-model="newProductName"
              type="text"
              required
              class="border border-[#75b62f] p-3 w-full rounded-lg text-[#003641] focus:ring-2 focus:ring-[#1fa193] focus:border-transparent"
              placeholder="Ex.: URA PUC"
            />
          </div>
          <button
            type="submit"
            class="bg-[#1fa193] text-white p-3 rounded-lg hover:bg-[#00ae9d] transition duration-200"
          >
            Criar Produto
          </button>
          <p v-if="createMessage" class="mt-3 text-[#c8d400] font-medium">{{ createMessage }}</p>
        </form>
      </div>

      <!-- Tabela de produtos -->
      <div class="bg-white p-6 rounded-lg shadow-md">
        <h3 class="text-xl font-semibold text-[#003641] mb-4">Lista de Produtos</h3>
        <table class="w-full border-collapse">
          <thead>
            <tr class="bg-[#75b62f] text-white">
              <th class="border border-[#75b62f] p-3 font-semibold text-center">
                <button 
                  @click="toggleSort" 
                  class="flex items-center justify-center gap-2 hover:text-gray-200 transition-colors mx-auto"
                >
                  Código
                  <span class="text-sm">
                    {{ sortOrder === 'asc' ? '↑' : '↓' }}
                  </span>
                </button>
              </th>
              <th class="border border-[#75b62f] p-3 font-semibold text-center">Nome</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="produto in sortedProdutos" :key="produto.codigo" class="hover:bg-gray-50">
              <td class="border border-[#75b62f] p-3 text-[#003641] text-center">{{ produto.codigo }}</td>
              <td class="border border-[#75b62f] p-3 text-[#003641] text-center">{{ produto.nome }}</td>
            </tr>
            <tr v-if="sortedProdutos.length === 0">
              <td colspan="2" class="border border-[#75b62f] p-3 text-center text-[#003641]">
                Nenhum produto encontrado
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-else class="flex justify-center items-center h-full">
      <div class="loader"></div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import axios from 'axios'
import { Produto } from '@/types'
import { getProdutos, invalidateProdutosCache } from '@/servicesCache'

export default defineComponent({
  name: 'Products',
  setup() {
    const isLoading = ref(false)

    return { isLoading }
  },
  data() {
    return {
      produtos: [] as Produto[],
      newProductName: '',
      createMessage: '',
      sortOrder: 'asc' as 'asc' | 'desc', // 'asc' para crescente, 'desc' para decrescente
    }
  },
  async mounted() {
    this.isLoading = true
    try {
      console.log('Componente Products montado, buscando produtos...')
      await this.fetchProducts()
      console.log('Produtos após busca:', this.produtos)
    } catch (error: any) {
      console.error('Erro ao buscar produtos:', error.message)
      if (error.response) {
        console.error('Detalhes do erro:', error.response.data)
      }
    } finally {
      this.isLoading = false
    }
  },
  computed: {
    sortedProdutos() {
      return [...this.produtos].sort((a, b) => {
        if (this.sortOrder === 'asc') {
          return a.codigo.localeCompare(b.codigo)
        } else {
          return b.codigo.localeCompare(a.codigo)
        }
      })
    }
  },
  methods: {
    async fetchProducts() {
      this.produtos = await getProdutos()
    },
    async createProduct() {
      this.isLoading = true
      try {
        const response = await axios.post('http://127.0.0.1:8000/produtos', {
          nome: this.newProductName,
        })
        this.createMessage = response.data.mensagem
        
        // Invalidar cache e recarregar produtos
        invalidateProdutosCache()
        await this.fetchProducts()
        
        this.newProductName = ''
        setTimeout(() => (this.createMessage = ''), 4000)
      } catch (error: any) {
        console.error('Erro ao criar produto:', error)
        this.createMessage = 'Erro ao criar produto: ' + error.message
      } finally {
        this.isLoading = false
      }
    },
    toggleSort() {
      this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc'
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