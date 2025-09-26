<template>
    <div class="bg-[#ffffff] p-4 lg:p-6 max-w-5xl mx-auto flex flex-col items-center">
      <h2 class="text-2xl lg:text-3xl font-bold text-[#003641] mb-2">Dashboard Minimalista</h2>
      <p class="text-sm text-[#003641] mb-5">KPIs Principais</p>
  
      <!-- Indicador de carregamento com círculo girando -->
      <div v-if="isLoading" class="flex justify-center items-center h-64">
        <div class="w-12 h-12 border-4 border-t-[#00ae9d] border-[#003641] rounded-full animate-spin"></div>
      </div>
      <div v-else class="flex flex-col md:flex-row gap-6 md:gap-8">
        <div class="text-center">
          <p class="text-4xl md:text-5xl font-bold text-[#003641]">{{ servicos.length }}</p>
          <p class="text-sm md:text-lg text-[#003641]">Total de Serviços</p>
        </div>
        <div class="text-center">
          <p class="text-3xl md:text-5xl font-bold text-[#1fa193] break-words">{{ produtoMaisFrequente }}</p>
          <p class="text-sm md:text-lg text-[#003641]">Produto Dominante</p>
          <p class="text-xs md:text-sm text-[#003641]">Quantidade: {{ produtoMaisFrequenteCount }}</p>
        </div>
        <div class="text-center">
          <p class="text-3xl md:text-5xl font-bold text-[#c5d20e] break-words">{{ menuMaisUsado }}</p>
          <p class="text-sm md:text-lg text-[#003641]">Menu Dominante</p>
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
  
  const cache: { servicos?: Servico[]; produtos?: Produto[] } = {};
  
  export default defineComponent({
    name: 'DashboardMinimalista',
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
        return valor;
      },
      async loadData() {
        this.isLoading = true;
        try {
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