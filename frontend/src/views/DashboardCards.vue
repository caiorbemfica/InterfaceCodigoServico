<template>
  <div class="bg-[#ffffff] p-4 lg:p-6 max-w-6xl mx-auto">
      <h2 class="text-2xl lg:text-3xl font-bold text-[#003641] mb-2">Dashboard de Cards</h2>
      <p class="text-sm text-[#003641] mb-5">Visão Resumida</p>
  
    <!-- Indicador de carregamento com círculo girando -->
    <div v-if="isLoading" class="flex justify-center items-center h-64">
      <div class="w-12 h-12 border-4 border-t-[#00ae9d] border-[#003641] rounded-full animate-spin"></div>
    </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
        <div class="bg-[#75b62f] p-5 md:p-6 rounded-lg shadow-md text-[#ffffff] text-center">
          <h3 class="text-sm uppercase tracking-wide opacity-90">Total de Serviços</h3>
          <p class="text-3xl md:text-4xl mt-2 font-semibold">{{ servicos.length }}</p>
        </div>
        <div class="bg-[#00ae9d] p-5 md:p-6 rounded-lg shadow-md text-[#ffffff] text-center">
          <h3 class="text-sm uppercase tracking-wide opacity-90">Produto Mais Frequente</h3>
          <p class="text-xl md:text-2xl mt-2 font-semibold break-words">{{ produtoMaisFrequente }}</p>
          <p class="text-xs md:text-sm mt-1 opacity-90">Quantidade: {{ produtoMaisFrequenteCount }}</p>
        </div>
        <div class="bg-[#c8d400] p-5 md:p-6 rounded-lg shadow-md text-[#003641] text-center">
          <h3 class="text-sm uppercase tracking-wide opacity-90">Menu Mais Usado</h3>
          <p class="text-xl md:text-2xl mt-2 font-semibold break-words">{{ menuMaisUsado }}</p>
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
          const display = this.getProdutoNome(s.produto);
          if (!display) return acc;
          acc[display] = (acc[display] || 0) + 1;
          return acc;
        }, {} as Record<string, number>);
        const top = Object.entries(count).sort((a, b) => b[1] - a[1])[0];
        return top ? top[0] : 'Nenhum';
      },
      produtoMaisFrequenteCount() {
        const count = this.servicos.reduce((acc, s) => {
          const display = this.getProdutoNome(s.produto);
          if (!display) return acc;
          acc[display] = (acc[display] || 0) + 1;
          return acc;
        }, {} as Record<string, number>);
        const top = Object.entries(count).sort((a, b) => b[1] - a[1])[0];
        return top ? top[1] : 0;
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
      getProdutoNome(valor: string) {
        if (!valor) return '';
        const prod = this.produtos.find(p => p.codigo === valor || p.nome === valor);
        if (prod) return prod.nome;
        // Se vier no formato "NN_", não encontrado na lista, mantém o valor cru
        return valor;
      },
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