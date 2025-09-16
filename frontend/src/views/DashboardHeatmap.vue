<template>
    <div class="min-h-screen bg-[#ffffff] p-4 lg:p-6">
      <h2 class="text-3xl font-bold text-[#003641] mb-4">Dashboard de Mapa de Calor</h2>
      <p class="text-[#003641] mb-6">Análise de Frequência</p>
  
      <!-- Indicador de carregamento com círculo girando -->
      <div v-if="isLoading" class="flex justify-center items-center h-64">
        <div class="w-12 h-12 border-4 border-t-[#00ae9d] border-[#003641] rounded-full animate-spin"></div>
      </div>
      <div v-else class="max-w-4xl mx-auto">
        <canvas ref="heatmapChart"></canvas>
      </div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref, onMounted } from 'vue';
  import { Chart, registerables, Scale, Tick } from 'chart.js';
  import 'chartjs-chart-matrix';
  
  Chart.register(...registerables);
  
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
    name: 'DashboardHeatmap',
    setup() {
      const heatmapChart = ref<HTMLCanvasElement | null>(null);
      return { heatmapChart };
    },
    data() {
      return {
        servicos: [] as Servico[],
        produtos: [] as Produto[],
        isLoading: true,
      };
    },
    async mounted() {
      await this.loadData();
      if (!this.isLoading) this.renderHeatmap();
    },
    methods: {
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
      renderHeatmap() {
        const ctx = this.heatmapChart?.getContext('2d');
        if (!ctx) return;
  
        // Calcular a frequência de cada combinação produto-menu
        const frequencyMap = this.servicos.reduce((acc, s) => {
          const key = `${s.produto}|${s.menu}`;
          acc[key] = (acc[key] || 0) + 1;
          return acc;
        }, {} as Record<string, number>);
  
        const produtoKeys = [...new Set(this.servicos.map(s => s.produto))];
        const menuKeys = [...new Set(this.servicos.map(s => s.menu))];
  
        const data = Object.entries(frequencyMap).map(([key, value]) => {
          const [produto, menu] = key.split('|');
          return {
            x: produtoKeys.indexOf(produto),
            y: menuKeys.indexOf(menu),
            v: value,
          };
        });
  
        new Chart(ctx, {
          type: 'matrix',
          data: {
            datasets: [
              {
                label: 'Frequência',
                data,
                backgroundColor: (c: any) => {
                  const value = c.dataset.data[c.dataIndex].v;
                  // Gradiente de cores baseado no valor
                  if (value > 5) return '#c5d20e';
                  if (value > 2) return '#75b62f';
                  return '#1fa193';
                },
                borderColor: '#003641',
                borderWidth: 1,
                width: ({ chart }) => (chart.chartArea || {}).width / produtoKeys.length - 1,
                height: ({ chart }) => (chart.chartArea || {}).height / menuKeys.length - 1,
              },
            ],
          },
          options: {
            responsive: true,
            scales: {
              x: {
                ticks: {
                  callback: function (
                    this: Scale,
                    tickValue: string | number,
                    index: number,
                    ticks: Tick[]
                  ): string {
                    return typeof tickValue === 'number' ? produtoKeys[tickValue] || '' : '';
                  },
                },
              },
              y: {
                ticks: {
                  callback: function (
                    this: Scale,
                    tickValue: string | number,
                    index: number,
                    ticks: Tick[]
                  ): string {
                    return typeof tickValue === 'number' ? menuKeys[tickValue] || '' : '';
                  },
                },
              },
            },
          },
        });
      },
    },
  });
  </script>