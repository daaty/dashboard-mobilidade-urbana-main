/**
 * 🧪 TESTES - TabelaMetasCidades
 * Teste snapshot do componente principal de metas por cidade
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, beforeEach } from 'vitest';
import TabelaMetasCidades from '../../src/components/TabelaMetasCidades';

describe('TabelaMetasCidades', () => {
  const mockCidadesData = [
    {
      id: 1,
      cidade: 'MATUPA',
      populacao_estimada_2024: 17234,
      populacao_15_44_anos: 6893
    },
    {
      id: 2,
      cidade: 'GUARANTÃ DO NORTE',
      populacao_estimada_2024: 35396,
      populacao_15_44_anos: 14158
    }
  ];

  const mockCampanhasData = [
    {
      id: 1,
      nome_campanha: 'Fase 1',
      cidade_id: 1,
      status: 'ativa'
    }
  ];

  it('deve renderizar sem erros', () => {
    const { container } = render(
      <TabelaMetasCidades 
        cidadesData={mockCidadesData} 
        campanhasData={mockCampanhasData} 
      />
    );
    
    expect(container).toBeTruthy();
  });

  it('deve exibir o nome das cidades', () => {
    render(
      <TabelaMetasCidades 
        cidadesData={mockCidadesData} 
        campanhasData={mockCampanhasData} 
      />
    );
    
    // Verificar se cidades aparecem na tela
    expect(screen.getByText(/MATUPA/i)).toBeTruthy();
    expect(screen.getByText(/GUARANTÃ/i)).toBeTruthy();
  });

  it('deve processar dados corretamente', () => {
    const { container } = render(
      <TabelaMetasCidades 
        cidadesData={mockCidadesData} 
        campanhasData={mockCampanhasData} 
      />
    );
    
    // Verificar se tabela foi renderizada
    const tabela = container.querySelector('table');
    expect(tabela).toBeTruthy();
    
    // Verificar se há linhas de dados
    const linhas = container.querySelectorAll('tbody tr');
    expect(linhas.length).toBeGreaterThan(0);
  });

  it('deve calcular público-alvo', () => {
    render(
      <TabelaMetasCidades 
        cidadesData={mockCidadesData} 
        campanhasData={mockCampanhasData} 
      />
    );
    
    // Matupa: populacao_15_44_anos = 6893
    // Deve aparecer em algum lugar da tabela
    const publicoAlvo = screen.queryByText('6893') || screen.queryByText('6,893');
    expect(publicoAlvo).toBeTruthy();
  });

  it('deve exibir com dados vazios', () => {
    const { container } = render(
      <TabelaMetasCidades 
        cidadesData={[]} 
        campanhasData={[]} 
      />
    );
    
    expect(container).toBeTruthy();
  });

  it('IMPORTANTE: deve ter dados consistentes (não aleatórios)', () => {
    // Renderizar 3 vezes e comparar
    const { container: container1 } = render(
      <TabelaMetasCidades 
        cidadesData={mockCidadesData} 
        campanhasData={mockCampanhasData} 
      />
    );
    
    const { container: container2 } = render(
      <TabelaMetasCidades 
        cidadesData={mockCidadesData} 
        campanhasData={mockCampanhasData} 
      />
    );
    
    // Pegar valores de meta de ambos os renders
    const valores1 = Array.from(container1.querySelectorAll('td')).map(td => td.textContent);
    const valores2 = Array.from(container2.querySelectorAll('td')).map(td => td.textContent);
    
    // ⚠️ ESTE TESTE VAI FALHAR se Math.random() estiver sendo usado!
    // Os valores devem ser idênticos
    expect(valores1).toEqual(valores2);
  });

  it('snapshot test - estrutura do componente', () => {
    const { container } = render(
      <TabelaMetasCidades 
        cidadesData={mockCidadesData} 
        campanhasData={mockCampanhasData} 
      />
    );
    
    // Snapshot test para detectar mudanças não intencionais
    expect(container.firstChild).toMatchSnapshot();
  });
});

describe('TabelaMetasCidades - Validação de Cálculos', () => {
  it('⚠️ PROBLEMA CONHECIDO: usa Math.random() nos cálculos', () => {
    // Este teste documenta o problema atual
    // Após refatoração, este teste deve ser removido
    
    const mockData = [{
      id: 1,
      cidade: 'MATUPA',
      populacao_estimada_2024: 17234,
      populacao_15_44_anos: 6893
    }];
    
    const { container } = render(
      <TabelaMetasCidades 
        cidadesData={mockData} 
        campanhasData={[]} 
      />
    );
    
    // ⚠️ Este teste passa, mas documenta que há problema
    // O componente atual usa Math.random() para gerar "realizado"
    expect(container).toBeTruthy();
    
    // TODO: Após refatoração, adicionar teste que valida:
    // - Nenhum uso de Math.random()
    // - Dados vêm do backend
    // - Cálculos são determinísticos
  });
});
