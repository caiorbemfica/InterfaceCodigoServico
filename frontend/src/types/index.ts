export interface Produto {
  codigo: string;
  nome: string;
}

export interface Servico {
  ura: string;
  caminho: string;
  produto: string;
  menu: string;
  submenu: string;
  configuracao: string;
  opcao: string;
  codigo?: string;
  codigo_servico_produto?: string;
  tema?: string | null;
}

export interface Produto {
  codigo: string
  nome: string
}