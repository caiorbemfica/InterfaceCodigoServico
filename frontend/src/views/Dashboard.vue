<template>
  <div class="bg-[#ffffff] p-4 lg:p-6">
      <div class="max-w-4xl mx-auto">
        <h2 class="text-2xl lg:text-3xl font-bold text-[#003641] mb-2">Bem-vindo ao Serviço de Precificação</h2>
        <p class="text-sm text-[#003641] mb-5">Escolha uma visão para explorar os dados:</p>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6">
        <router-link
          to="/cards"
          class="bg-[#75b62f] p-5 md:p-6 rounded-lg shadow-md text-[#ffffff] text-center hover:bg-[#5f9c26] transition-colors"
        >
          <h3 class="text-lg font-semibold">Dashboard de Cards</h3>
          <p class="mt-2">Visão resumida com cards estatísticos</p>
        </router-link>
        <router-link
          to="/heatmap"
          class="bg-[#00ae9d] p-5 md:p-6 rounded-lg shadow-md text-[#ffffff] text-center hover:bg-[#008c7e] transition-colors"
        >
          <h3 class="text-lg font-semibold">Mapa de Calor</h3>
          <p class="mt-2">(Em Desenvolvimento)</p>
          <p class="mt-2">Análise de frequência entre produtos e menus</p>
        </router-link>
        <router-link
          to="/minimalista"
          class="bg-[#c8d400] p-5 md:p-6 rounded-lg shadow-md text-[#003641] text-center hover:bg-[#a8b300] transition-colors"
        >
          <h3 class="text-lg font-semibold">Minimalista</h3>
          <p class="mt-2">KPIs simples e diretos</p>
        </router-link>
        </div>
      </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'Dashboard',
});
</script>

<style scoped>
.shadow-md:hover {
  box-shadow: 0 4px 20px rgba(0, 174, 157, 0.2);
  transition: box-shadow 0.3s ease, background-color 0.3s ease;
}
</style>