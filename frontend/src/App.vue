<template>
  <div class="min-h-screen bg-white flex flex-col">
    <!-- Navbar -->
    <nav class="bg-[#003641] p-4 text-white fixed w-full top-0 z-10 shadow-md">
      <div class="container mx-auto flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <img src="@/assets/logo2.png" alt="Logo Sicoob" class="h-10" />
          <h1 class="text-2xl font-bold">Controle dos Códigos de Serviços CXone - PROIN</h1>
        </div>
        <div class="space-x-4">
          <router-link to="/" class="hover:text-[#00ae9d] transition">Home</router-link>
          <router-link to="/services" class="hover:text-[#00ae9d] transition">Serviços</router-link>
          <!--<router-link to="/create-service" class="hover:text-[#00ae9d] transition">Criar Serviço</router-link>-->
          <router-link to="/products" class="hover:text-[#00ae9d] transition">Produtos</router-link>
        </div>
      </div>
    </nav>

    <!-- Conteúdo Principal -->
    <div class="flex-1 mt-16 w-full p-4 lg:p-6">
      <router-view v-if="!isLoading"></router-view>
      <div v-else class="flex justify-center items-center h-full">
        <div class="loader"></div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="bg-[#003641] text-white p-4 w-full">
      <div class="container mx-auto text-center">
        <p class="text-sm">
          © 2025 PROIN - Controle dos Códigos de Serviços CXone - PROIN. Todos os direitos reservados.
        </p>
        <p class="text-xs mt-2">
          Desenvolvido por <span class="text-[#00ae9d]">Equipe PROIN</span>
        </p>
      </div>
    </footer>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'App',
  setup() {
    const isLoading = ref(false);

    // Método para setar o estado de carregamento (usado pelos componentes filhos via provide/inject, se necessário)
    const setLoading = (value: boolean) => {
      isLoading.value = value;
    };

    return { isLoading, setLoading };
  },
});
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

/* Estilização para responsividade */
nav .container {
  flex-wrap: wrap; /* Permite que os itens quebrem em telas menores */
}

nav .flex.items-center {
  flex-shrink: 0; /* Impede que o logo e o título encolham demais */
}

nav .space-x-4 {
  flex-shrink: 0; /* Impede que os links encolham demais */
}

@media (max-width: 768px) {
  nav .container {
    flex-direction: column;
    text-align: center;
  }
  nav .flex.items-center {
    margin-bottom: 1rem; /* Espaço entre logo/título e links em telas pequenas */
  }
}
</style>