<template>
  <div class="w-full p-4 lg:p-6">
    <h2 class="text-3xl font-bold text-[#003641] mb-6">{{ isEdit ? 'Editar Serviço' : 'Criar Novo Serviço' }}</h2>
    <div v-if="!isLoading" class="bg-white p-6 rounded-lg shadow-md">
      <form @submit.prevent="submitForm" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-[#003641] font-medium mb-2">Produto/Tema:</label>
            <template v-if="!isEdit">
              <select 
                v-model="form.produto" 
                required 
                class="border border-[#75b62f] p-3 w-full rounded-lg focus:ring-2 focus:ring-[#1fa193] focus:border-transparent"
                @change="onProdutoChange"
              >
                <option v-for="produto in produtos" 
                  :key="produto.codigo" 
                  :value="produto.codigo"
                >
                  {{ produto.nome }}
                </option>
              </select>
            </template>
            <template v-else>
              <input 
                type="text"
                :value="productNomeSelecionado"
                readonly
                class="border border-[#75b62f] p-3 w-full rounded-lg bg-gray-100 text-[#003641] cursor-not-allowed"
              />
            </template>
          </div>
          <div>
            <label class="block text-[#003641] font-medium mb-2">URA:</label>
            <input 
              type="text"
              v-model="form.ura"
              readonly
              class="border border-[#75b62f] p-3 w-full rounded-lg bg-gray-100 text-[#003641] cursor-not-allowed"
            />
          </div>
          <div>
            <label class="block text-[#003641] font-medium mb-2">Caminho:</label>
            <input v-model="form.caminho" type="text" required class="border border-[#75b62f] p-3 w-full rounded-lg focus:ring-2 focus:ring-[#1fa193] focus:border-transparent" />
          </div>
          <div>
            <label class="block text-[#003641] font-medium mb-2">Menu:</label>
            <div class="relative">
              <input 
                v-model="menuSearch"
                type="text"
                class="border border-[#75b62f] p-3 w-full rounded-lg focus:ring-2 focus:ring-[#1fa193] focus:border-transparent"
                placeholder="Digite para buscar ou criar novo menu"
                @input="onMenuInput"
                @focus="openMenuDropdown"
                @blur="closeMenuDropdownDelayed"
              />
              <div v-if="filteredMenus.length && showMenuDropdown" 
                class="absolute z-10 w-full bg-white border border-gray-200 rounded-lg mt-1 max-h-60 overflow-y-auto">
                <div 
                  v-for="menu in filteredMenus" 
                  :key="menu"
                  class="p-2 hover:bg-gray-100 cursor-pointer"
                  @click="selectMenu(menu)"
                >
                  {{ menu }}
                </div>
              </div>
            </div>
          </div>
          <div>
            <label class="block text-[#003641] font-medium mb-2">Submenu:</label>
            <input 
              v-model="form.submenu" 
              type="text" 
              class="border border-[#75b62f] p-3 w-full rounded-lg focus:ring-2 focus:ring-[#1fa193] focus:border-transparent" 
              placeholder="Opcional"
            />
          </div>
          <div>
            <label class="block text-[#003641] font-medium mb-2">Configuração:</label>
            <input v-model="form.configuracao" type="text" required class="border border-[#75b62f] p-3 w-full rounded-lg focus:ring-2 focus:ring-[#1fa193] focus:border-transparent" />
          </div>
          <div>
            <label class="block text-[#003641] font-medium mb-2">Tipo:</label>
            <select 
              v-model="form.tipo" 
              required 
              class="border border-[#75b62f] p-3 w-full rounded-lg focus:ring-2 focus:ring-[#1fa193] focus:border-transparent" 
              @change="updateOpcao"
            >
              <option value="H">Humano</option>
              <option value="D">Digital</option>
              <option value="S">Serviço URA</option>
            </select>
          </div>
          <div>
            <label class="block text-[#003641] font-medium mb-2">Opção:</label>
            <input v-model="form.opcaoNome" type="text" required class="border border-[#75b62f] p-3 w-full rounded-lg focus:ring-2 focus:ring-[#1fa193] focus:border-transparent" @input="updateOpcao" />
          </div>
          <!--<div class="md:col-span-2">
            <label class="block text-[#003641] font-medium mb-2">Tema (Opcional):</label>
            <input v-model="form.tema" type="text" class="border border-[#75b62f] p-3 w-full rounded-lg focus:ring-2 focus:ring-[#1fa193] focus:border-transparent" />
          </div>-->
          <div v-if="isEdit" class="md:col-span-2">
            <label class="block text-[#003641] font-medium mb-2">Código Serviço Produto:</label>
            <input v-model="form.codigo_servico_produto" type="text" readonly class="border border-[#75b62f] p-3 w-full rounded-lg bg-gray-100 text-gray-600" />
          </div>
        </div>
        <button type="submit" class="bg-[#1fa193] text-white p-3 rounded-lg hover:bg-[#00ae9d] transition duration-200"> {{ isEdit ? 'Salvar' : 'Criar' }}</button>
      </form>
    </div>
    <div v-else class="flex justify-center items-center h-full">
      <div class="loader"></div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
        <h3 class="text-xl font-bold text-[#003641] mb-4">
          {{ isEdit ? 'Serviço Editado' : 'Serviço Criado' }}
        </h3>
        <p class="text-gray-700 mb-6">
          {{ isEdit ? 'Serviço editado' : 'Serviço criado' }} com o código: 
          <span class="font-bold">{{ modalCodigo }}</span>
        </p>
        <button 
          @click="closeModal" 
          class="bg-[#1fa193] text-white px-4 py-2 rounded-lg hover:bg-opacity-90 w-full"
        >
          Fechar
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import axios from 'axios'
import { cache, getProdutos } from '../servicesCache'
import { Produto, Servico } from '@/types'

interface FormState {
  ura: string;
  caminho: string;
  produto: string;
  menu: string;
  submenu: string | null;
  configuracao: string;
  tipo: 'H' | 'D' | 'S';
  opcaoNome: string;
  opcao: string;
  tema: string | null;
  codigo_servico_produto: string | undefined;
}

export default defineComponent({
  name: 'CreateService',
  setup() {
    const isLoading = ref(false)
    const showModal = ref(false)
    const modalCodigo = ref('')

    return { isLoading, showModal, modalCodigo }
  },
  data() {
    return {
      produtos: [] as Produto[],
      form: {
        ura: '',
        caminho: '',
        produto: '',
        menu: '',
        submenu: null,
        configuracao: '',
        tipo: 'H' as const,
        opcaoNome: '',
        opcao: '',
        tema: null,
        codigo_servico_produto: undefined,
      } as FormState,
      isEdit: false,
      uras: [] as string[],
      menus: [] as string[],
      menuSearch: '',
      filteredMenus: [] as string[],
      showMenuDropdown: false,
      productNomeSelecionado: '',
    }
  },
  async mounted() {
    this.isLoading = true
    try {
      // Carregar produtos usando cache
      this.produtos = await getProdutos()
      
      // Carregar URAs únicas
      this.uras = [...new Set(cache.servicos.map(s => s.ura))].sort()


      // Modo edição
      if (this.$route.query.edit) {
        const codigo = this.$route.query.edit as string
        const servicoResponse = await axios.get<Servico[]>(`http://127.0.0.1:8000/servico/${codigo}`)
        const servico = servicoResponse.data[0]
        
        // Mapeia produto de nome -> código (backend pode retornar nome em edições)
        const produtoMatch = this.produtos.find(p => p.codigo === servico.produto || p.nome === servico.produto)
        const produtoCodigo = produtoMatch ? produtoMatch.codigo : servico.produto

        this.form = {
          ura: servico.ura,
          caminho: servico.caminho,
          produto: produtoCodigo,
          menu: servico.menu,
          submenu: servico.submenu,
          configuracao: servico.configuracao,
          tipo: servico.opcao[0] as 'H' | 'D' | 'S',
          opcaoNome: servico.opcao.slice(2),
          opcao: servico.opcao,
          tema: servico.tema ?? null,
          codigo_servico_produto: servico.codigo_servico_produto,
        }

        this.isEdit = true
        this.updateOpcao()
        await this.loadMenus()
        // Preenche o campo de busca/visualização do menu no modo edição
        this.menuSearch = this.form.menu
        // Define o nome do produto selecionado para exibição somente leitura
        this.productNomeSelecionado = produtoMatch ? produtoMatch.nome : servico.produto
      }
    } catch (error: any) {
      alert('Erro ao carregar dados: ' + error.message)
    } finally {
      this.isLoading = false
    }
  },
  methods: {
    onProdutoChange() {
      // Deriva URA "genérica" a partir do nome do produto (ex.: "URA SIPAG 2.0" -> "URA SIPAG")
      const selected = this.produtos.find(p => p.codigo === this.form.produto)
      if (!selected) {
        this.form.ura = ''
        this.menus = []
        this.menuSearch = ''
        this.filteredMenus = []
        return
      }

      const nomeUpper = selected.nome.toUpperCase().trim()
      let baseUra = nomeUpper
      if (nomeUpper.startsWith('URA ')) {
        const rest = nomeUpper.slice(4).trim() // após 'URA '
        const tokens = rest.split(/\s+/)
        // Caso especial: "URA CARTOES <BANCO> [VIP|BLACK|...]" → preservar sufixos (não ignorar)
        if (tokens[0] === 'CARTOES') {
          const banco = tokens[1] || ''
          const sufixo = tokens[2] && ['VIP', 'BLACK'].includes(tokens[2]) ? ` ${tokens[2]}` : ''
          baseUra = `URA CARTOES ${banco}${sufixo}`.trim()
        } else {
          // Regra geral: "URA <CATEGORIA> ..." → "URA <CATEGORIA>"
          const categoria = tokens[0] || ''
          baseUra = `URA ${categoria}`
        }
      }

      // Procura uma URA existente que combine
      const candidateExact = this.uras.find(u => u.toUpperCase() === baseUra)
      const needle = baseUra.replace('URA ', '').trim()
      const candidateContains = this.uras.find(u => u.toUpperCase().includes(needle))

      if (candidateExact) {
        this.form.ura = candidateExact
      } else if (candidateContains) {
        this.form.ura = candidateContains
      } else {
        // Fallback: tenta pelos serviços existentes com o mesmo produto (comportamento antigo)
        const matchingService = cache.servicos.find(s => s.produto === this.form.produto)
        this.form.ura = matchingService ? matchingService.ura : ''
      }

      // Carrega menus conforme a URA definida
      if (this.form.ura) {
        this.loadMenus()
      } else {
        this.menus = []
        this.menuSearch = ''
        this.filteredMenus = []
      }
    },
    updateOpcao() {
      if (this.form.tipo && this.form.opcaoNome) {
        this.form.opcao = `${this.form.tipo}-${this.form.opcaoNome}`
      }
    },
    async submitForm() {
      this.isLoading = true
      try {
        // Se o usuário digitou um novo menu e não clicou na lista, usa o texto digitado
        if (!this.form.menu && this.menuSearch) {
          this.form.menu = this.menuSearch.trim()
        }

        const payload: Servico = { 
          ...this.form, 
          opcao: this.form.opcao,
          tema: this.form.tema ?? '',
          codigo_servico_produto: this.form.codigo_servico_produto ?? '',
          submenu: this.form.submenu ?? '',
        }
        delete (payload as any).tipo
        delete (payload as any).opcaoNome

        let response
        if (this.isEdit) {
          response = await axios.put(`http://127.0.0.1:8000/servico/${this.$route.query.edit}`, payload)
          this.modalCodigo = response.data.codigo_servico_produto
          const index = cache.servicos.findIndex(s => s.codigo_servico_produto === this.form.codigo_servico_produto)
          if (index >= 0) cache.servicos[index] = response.data
        } else {
          response = await axios.post('http://127.0.0.1:8000/servicos', payload)
          this.modalCodigo = response.data.codigo_servico_produto
          cache.servicos.push(response.data)
        }

        this.showModal = true
        
      } catch (error: any) {
        alert('Erro ao salvar o serviço: ' + error.message)
      } finally {
        this.isLoading = false
      }
    },
    closeModal() {
      this.showModal = false
      this.$router.push('/services')
    },
    async loadMenus() {
      if (!this.form.ura) return
      
      try {
        const response = await axios.get<string[]>(`http://127.0.0.1:8000/menus/${this.form.ura}`)
        this.menus = response.data
        this.filterMenus()
        this.showMenuDropdown = false
      } catch (error: any) {
        console.error('Erro ao carregar menus:', error)
      }
    },
    
    filterMenus() {
      if (!this.menuSearch) {
        this.filteredMenus = this.menus
      } else {
        this.filteredMenus = this.menus.filter(menu => 
          menu.toLowerCase().includes(this.menuSearch.toLowerCase())
        )
      }
    },

    openMenuDropdown() {
      if (this.filteredMenus.length) {
        this.showMenuDropdown = true
      }
    },

    closeMenuDropdownDelayed() {
      // Aguarda clique no item antes de fechar
      setTimeout(() => {
        this.showMenuDropdown = false
      }, 150)
    },

    onMenuInput() {
      this.filterMenus()
      this.openMenuDropdown()
    },
    
    selectMenu(menu: string) {
      this.form.menu = menu
      this.menuSearch = menu
      this.showMenuDropdown = false
    }
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