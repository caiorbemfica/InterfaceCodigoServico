<template>
    <div class="min-h-screen bg-[#ffffff] p-4 lg:p-6">
      <h2 class="text-3xl font-bold text-[#003641] mb-4">Dashboard de Cards</h2>
      <p class="text-[#003641] mb-6">Visão Resumida</p>
  
    <!-- Indicador de carregamento com círculo girando -->
    <div v-if="isLoading" class="flex justify-center items-center h-64">
      <div class="w-12 h-12 border-4 border-t-[#00ae9d] border-[#003641] rounded-full animate-spin"></div>
    </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-[#75b62f] p-6 rounded-lg shadow-md text-[#ffffff] text-center">
          <h3 class="text-lg font-semibold">Total de Serviços</h3>
          <p class="text-4xl mt-2">{{ servicos.length }}</p>
        </div>
        <div class="bg-[#00ae9d] p-6 rounded-lg shadow-md text-[#ffffff] text-center">
          <h3 class="text-lg font-semibold">Produto Mais Frequente</h3>
          <p class="text-2xl mt-2">{{ produtoMaisFrequente }}</p>
        </div>
        <div class="bg-[#c8d400] p-6 rounded-lg shadow-md text-[#003641] text-center">
          <h3 class="text-lg font-semibold">Menu Mais Usado</h3>
          <p class="text-2xl mt-2">{{ menuMaisUsado }}</p>
        </div>
      </div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent } from 'vue';
  
  interface Servico {
    submenu: string | null;
    produto: string;
    opcao: string;
    menu: string;
    ura: string;
    caminho: string;
    codigo_servico_produto: string;
    configuracao: string | null;
  }
  
  interface Produto {
    codigo: string;
    nome: string;
  }
  
  // Cache global simples
  const cache: { servicos?: Servico[]; produtos?: Produto[] } = {};
  
  export default defineComponent({
    name: 'DashboardCards',
    data() {
      return {
        servicos: [] as Servico[],
        produtos: [] as Produto[],
        isLoading: true,
      };
    },
    computed: {
      produtoMaisFrequente() {
        const count = this.servicos.reduce((acc, s) => {
          acc[s.produto] = (acc[s.produto] || 0) + 1;
          return acc;
        }, {} as Record<string, number>);
        return Object.entries(count).sort((a, b) => b[1] - a[1])[0]?.[0] || 'Nenhum';
      },
      menuMaisUsado() {
        const count = this.servicos.reduce((acc, s) => {
          acc[s.menu] = (acc[s.menu] || 0) + 1;
          return acc;
        }, {} as Record<string, number>);
        return Object.entries(count).sort((a, b) => b[1] - a[1])[0]?.[0] || 'Nenhum';
      },
    },
    async mounted() {
      await this.loadData();
    },
    methods: {
      async loadData() {
        this.isLoading = true;
        try {
          // Usa cache se disponível
          if (cache.servicos && cache.produtos) {
            this.servicos = cache.servicos;
            this.produtos = cache.produtos;
          } else {
            const servicosResponse = await fetch('http://127.0.0.1:8000/servicos');
            this.servicos = await servicosResponse.json();
            cache.servicos = this.servicos;
  
            const produtosResponse = await fetch('http://127.0.0.1:8000/produtos');
            this.produtos = await produtosResponse.json();
            cache.produtos = this.produtos;
          }
        } catch (error) {
          console.error('Erro ao carregar dados:', error);
        } finally {
          this.isLoading = false;
        }
      },
    },
  });
  </script>
  
  <style scoped>
  .shadow-md:hover {
    box-shadow: 0 4px 20px rgba(0, 174, 157, 0.2);
    transition: box-shadow 0.3s ease;
  }
  </style>