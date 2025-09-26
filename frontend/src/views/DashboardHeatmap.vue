<template>
  <div class="bg-[#ffffff] p-4 lg:p-6 max-w-7xl mx-auto">
    <div class="mb-6">
      <h2 class="text-2xl lg:text-3xl font-bold text-[#003641] mb-2">Mapa de Calor URA × Menu</h2>
      <p class="text-sm text-[#003641] mb-4">Análise de frequência e distribuição de serviços</p>
    </div>

    <!-- Filtros -->
    <div class="bg-gray-50 p-4 rounded-lg mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-[#003641] mb-2">Produto</label>
          <select v-model="filtros.produto" class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#1fa193]">
            <option value="">Todos os Produtos</option>
            <option v-for="produto in produtos" :key="produto.codigo" :value="produto.codigo">
              {{ produto.nome }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-[#003641] mb-2">Tipo de Serviço</label>
          <select v-model="filtros.tipo" class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#1fa193]">
            <option value="">Todos os Tipos</option>
            <option value="H">Humano</option>
            <option value="D">Digital</option>
            <option value="S">Serviço URA</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-[#003641] mb-2">Período</label>
          <select v-model="filtros.periodo" class="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#1fa193]">
            <option value="todos">Todos</option>
            <option value="recentes">Últimos 30 dias</option>
            <option value="semana">Última semana</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="aplicarFiltros" class="w-full bg-[#1fa193] text-white p-2 rounded-lg hover:bg-[#00ae9d] transition-colors">
            Aplicar Filtros
          </button>
        </div>
      </div>
    </div>

    <!-- Indicador de carregamento -->
    <div v-if="isLoading" class="flex justify-center items-center h-64">
      <div class="w-12 h-12 border-4 border-t-[#00ae9d] border-[#003641] rounded-full animate-spin"></div>
    </div>

    <!-- Dashboard Principal -->
    <div v-else class="space-y-6">
      <!-- Cards de Resumo -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="bg-gradient-to-r from-[#75b62f] to-[#5f9c26] p-4 rounded-lg text-white">
          <div class="text-2xl font-bold">{{ totalServicos }}</div>
          <div class="text-sm opacity-90">Total de Serviços</div>
        </div>
        <div class="bg-gradient-to-r from-[#00ae9d] to-[#008c7e] p-4 rounded-lg text-white">
          <div class="text-2xl font-bold">{{ urasUnicas.length }}</div>
          <div class="text-sm opacity-90">URAs Únicas</div>
        </div>
        <div class="bg-gradient-to-r from-[#c8d400] to-[#a8b300] p-4 rounded-lg text-[#003641]">
          <div class="text-2xl font-bold">{{ menusUnicos.length }}</div>
          <div class="text-sm opacity-90">Menus Únicos</div>
        </div>
        <div class="bg-gradient-to-r from-[#1fa193] to-[#00ae9d] p-4 rounded-lg text-white">
          <div class="text-2xl font-bold">{{ combinacaoMaisFrequente.count }}</div>
          <div class="text-sm opacity-90">Maior Frequência</div>
        </div>
      </div>

      <!-- Heatmap Principal -->
      <div class="bg-white p-6 rounded-lg shadow-lg border">
        <h3 class="text-lg font-semibold text-[#003641] mb-4">Distribuição URA × Menu</h3>
        <div class="relative">
          <canvas ref="heatmapChart" class="w-full h-96"></canvas>
        </div>
        <!-- Legenda -->
        <div class="mt-4 flex items-center justify-center space-x-4">
          <div class="flex items-center space-x-2">
            <div class="w-4 h-4 bg-gray-200 border"></div>
            <span class="text-sm text-gray-600">0 serviços</span>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-4 h-4 bg-[#1fa193]"></div>
            <span class="text-sm text-gray-600">1-2 serviços</span>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-4 h-4 bg-[#75b62f]"></div>
            <span class="text-sm text-gray-600">3-5 serviços</span>
          </div>
          <div class="flex items-center space-x-2">
            <div class="w-4 h-4 bg-[#c8d400]"></div>
            <span class="text-sm text-gray-600">6+ serviços</span>
          </div>
        </div>
      </div>

      <!-- Tabela de Dados -->
      <div class="bg-white p-6 rounded-lg shadow-lg border">
        <h3 class="text-lg font-semibold text-[#003641] mb-4">Dados Detalhados</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="bg-gray-50">
                <th class="px-4 py-2 text-left font-medium text-[#003641]">URA</th>
                <th class="px-4 py-2 text-left font-medium text-[#003641]">Menu</th>
                <th class="px-4 py-2 text-center font-medium text-[#003641]">Frequência</th>
                <th class="px-4 py-2 text-center font-medium text-[#003641]">Intensidade</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in dadosTabela" :key="`${item.ura}-${item.menu}`" class="border-b hover:bg-gray-50">
                <td class="px-4 py-2 font-medium">{{ item.ura }}</td>
                <td class="px-4 py-2">{{ item.menu }}</td>
                <td class="px-4 py-2 text-center">
                  <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                        :class="getIntensidadeClass(item.count)">
                    {{ item.count }}
                  </span>
                </td>
                <td class="px-4 py-2 text-center">
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="h-2 rounded-full transition-all duration-300"
                         :class="getIntensidadeClass(item.count)"
                         :style="{ width: `${(item.count / maxFrequencia) * 100}%` }"></div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, nextTick } from 'vue';
import { Chart, registerables } from 'chart.js';

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

interface Filtros {
  produto: string;
  tipo: string;
  periodo: string;
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
      filtros: {
        produto: '',
        tipo: '',
        periodo: 'todos'
      } as Filtros,
      servicosFiltrados: [] as Servico[],
    };
  },
  computed: {
    totalServicos() {
      return this.servicosFiltrados.length;
    },
    urasUnicas() {
      return [...new Set(this.servicosFiltrados.map(s => s.ura))].sort();
    },
    menusUnicos() {
      return [...new Set(this.servicosFiltrados.map(s => s.menu))].sort();
    },
    dadosHeatmap() {
      const frequencyMap = this.servicosFiltrados.reduce((acc, s) => {
        const key = `${s.ura}|${s.menu}`;
        acc[key] = (acc[key] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);

      return Object.entries(frequencyMap).map(([key, count]) => {
        const [ura, menu] = key.split('|');
        return { ura, menu, count };
      }).sort((a, b) => b.count - a.count);
    },
    dadosTabela() {
      return this.dadosHeatmap.slice(0, 20); // Top 20
    },
    maxFrequencia() {
      return Math.max(...this.dadosHeatmap.map(d => d.count), 1);
    },
    combinacaoMaisFrequente() {
      return this.dadosHeatmap[0] || { ura: '', menu: '', count: 0 };
    }
  },
  async mounted() {
    await this.loadData();
    this.aplicarFiltros();
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
    aplicarFiltros() {
      let filtrados = [...this.servicos];

      if (this.filtros.produto) {
        filtrados = filtrados.filter(s => s.produto === this.filtros.produto);
      }

      if (this.filtros.tipo) {
        filtrados = filtrados.filter(s => s.opcao.startsWith(this.filtros.tipo));
      }

      // Filtro de período (simulado - você pode implementar com timestamps reais)
      if (this.filtros.periodo === 'recentes') {
        // Simulação: pega os últimos 30% dos serviços
        filtrados = filtrados.slice(-Math.floor(filtrados.length * 0.3));
      } else if (this.filtros.periodo === 'semana') {
        // Simulação: pega os últimos 10% dos serviços
        filtrados = filtrados.slice(-Math.floor(filtrados.length * 0.1));
      }

      this.servicosFiltrados = filtrados;
      this.$nextTick(() => {
        this.renderHeatmap();
      });
    },
    getIntensidadeClass(count: number) {
      if (count === 0) return 'bg-gray-200 text-gray-600';
      if (count <= 2) return 'bg-[#1fa193] text-white';
      if (count <= 5) return 'bg-[#75b62f] text-white';
      return 'bg-[#c8d400] text-[#003641]';
    },
    renderHeatmap() {
      const ctx = this.heatmapChart?.getContext('2d');
      if (!ctx || this.dadosHeatmap.length === 0) return;

      // Destruir gráfico anterior se existir
      if ((this as any).chartInstance) {
        (this as any).chartInstance.destroy();
      }

      const uras = this.urasUnicas;
      const menus = this.menusUnicos;

      // Criar matriz de dados
      const matrixData = uras.map((ura, uraIndex) => 
        menus.map((menu, menuIndex) => {
          const item = this.dadosHeatmap.find(d => d.ura === ura && d.menu === menu);
          return {
            x: menuIndex,
            y: uraIndex,
            v: item ? item.count : 0
          };
        })
      ).flat();

      (this as any).chartInstance = new Chart(ctx, {
        type: 'scatter',
        data: {
          datasets: [{
            label: 'Frequência URA × Menu',
            data: matrixData,
            backgroundColor: (context: any) => {
              const value = context.parsed.v;
              if (value === 0) return 'rgba(156, 163, 175, 0.3)';
              if (value <= 2) return 'rgba(31, 161, 147, 0.8)';
              if (value <= 5) return 'rgba(117, 182, 47, 0.8)';
              return 'rgba(200, 212, 0, 0.8)';
            },
            borderColor: (context: any) => {
              const value = context.parsed.v;
              if (value === 0) return 'rgba(156, 163, 175, 0.5)';
              return 'rgba(0, 54, 65, 0.8)';
            },
            borderWidth: 1,
            pointRadius: 15,
            pointHoverRadius: 20,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                title: (context: any) => {
                  const point = context[0];
                  const ura = uras[point.parsed.y];
                  const menu = menus[point.parsed.x];
                  return `${ura} × ${menu}`;
                },
                label: (context: any) => {
                  return `Serviços: ${context.parsed.v}`;
                }
              }
            }
          },
          scales: {
            x: {
              type: 'linear',
              position: 'bottom',
              min: -0.5,
              max: menus.length - 0.5,
              ticks: {
                stepSize: 1,
                callback: (value: any) => {
                  const index = Math.round(value);
                  return menus[index] || '';
                },
                maxRotation: 45,
                minRotation: 45
              },
              grid: {
                display: true,
                color: 'rgba(0, 0, 0, 0.1)'
              }
            },
            y: {
              type: 'linear',
              min: -0.5,
              max: uras.length - 0.5,
              ticks: {
                stepSize: 1,
                callback: (value: any) => {
                  const index = Math.round(value);
                  return uras[index] || '';
                }
              },
              grid: {
                display: true,
                color: 'rgba(0, 0, 0, 0.1)'
              }
            }
          }
        }
      });
    }
  }
});
</script>

<style scoped>
.shadow-lg {
  box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.hover\:bg-gray-50:hover {
  background-color: rgba(249, 250, 251, 1);
}
</style>