"""
🗄️ SCRIPT DE ANÁLISE DO BANCO DE DADOS
Executa queries de análise nas tabelas de metas e gera relatório
"""

import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('backend/.env.production')

# Configuração do banco
DB_HOST = os.getenv('DB_HOST', '148.230.73.27')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'n8n_db')
DB_USER = os.getenv('DB_USER', 'n8n_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'n8n_pw')


def conectar_banco():
    """Conecta ao banco de dados PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return None


def print_section(title):
    """Imprime título de seção formatado"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def print_table(headers, rows):
    """Imprime tabela formatada"""
    if not rows:
        print("  (Nenhum dado encontrado)")
        return
    
    # Calcular largura das colunas
    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(val) if val is not None else ''))
    
    # Imprimir cabeçalho
    header_line = "  " + " | ".join(str(h).ljust(w) for h, w in zip(headers, col_widths))
    print(header_line)
    print("  " + "-" * (len(header_line) - 2))
    
    # Imprimir linhas
    for row in rows:
        values = [str(v) if v is not None else '' for v in row]
        print("  " + " | ".join(v.ljust(w) for v, w in zip(values, col_widths)))


def analise_metas_progressivas(cursor):
    """Análise da tabela metas_progressivas"""
    print_section("📊 ANÁLISE: metas_progressivas")
    
    # Query 1: Visão geral
    query1 = """
    SELECT 
      COUNT(*) as total_registros,
      COUNT(DISTINCT cidade_id) as cidades_com_metas,
      COUNT(DISTINCT fase_id) as fases_distintas,
      MIN(mes) as mes_minimo,
      MAX(mes) as mes_maximo
    FROM metas_progressivas;
    """
    cursor.execute(query1)
    result = cursor.fetchone()
    
    print("📈 Visão Geral:")
    print(f"  Total de registros: {result[0] or 0}")
    print(f"  Cidades com metas: {result[1] or 0}")
    print(f"  Fases distintas: {result[2] or 0}")
    print(f"  Intervalo de meses: {result[3] or 'N/A'} a {result[4] or 'N/A'}")
    
    # Query 2: Dados reais vs. vazios
    query2 = """
    SELECT 
      COUNT(*) as total_metas,
      SUM(CASE WHEN resultado_corridas > 0 THEN 1 ELSE 0 END) as com_resultados_corridas,
      SUM(CASE WHEN resultado_corridas = 0 OR resultado_corridas IS NULL THEN 1 ELSE 0 END) as sem_resultados_corridas,
      SUM(CASE WHEN resultado_motoristas > 0 THEN 1 ELSE 0 END) as com_resultados_motoristas,
      SUM(CASE WHEN resultado_receita > 0 THEN 1 ELSE 0 END) as com_resultados_receita
    FROM metas_progressivas;
    """
    cursor.execute(query2)
    result = cursor.fetchone()
    
    print("\n🔍 Status dos Dados:")
    print(f"  Total de metas: {result[0] or 0}")
    print(f"  ✅ Com resultados (corridas): {result[1] or 0}")
    print(f"  ❌ Sem resultados (corridas): {result[2] or 0}")
    print(f"  ✅ Com resultados (motoristas): {result[3] or 0}")
    print(f"  ✅ Com resultados (receita): {result[4] or 0}")
    
    if result[0] and result[0] > 0:
        percentual_com_dados = (result[1] / result[0]) * 100 if result[1] else 0
        print(f"  📊 Percentual com dados reais: {percentual_com_dados:.1f}%")
    
    # Query 3: Metas por cidade
    query3 = """
    SELECT 
      cidade_nome,
      COUNT(*) as total_metas,
      SUM(CASE WHEN resultado_corridas > 0 THEN 1 ELSE 0 END) as metas_com_dados,
      ROUND(AVG(meta_corridas)::numeric, 0) as media_meta_corridas,
      ROUND(AVG(resultado_corridas)::numeric, 0) as media_resultado_corridas,
      SUM(CASE WHEN atingida = true THEN 1 ELSE 0 END) as metas_atingidas
    FROM metas_progressivas
    GROUP BY cidade_nome
    ORDER BY cidade_nome
    LIMIT 15;
    """
    cursor.execute(query3)
    results = cursor.fetchall()
    
    print("\n📋 Metas por Cidade:")
    headers = ["Cidade", "Total", "Com Dados", "Média Meta", "Média Real", "Atingidas"]
    print_table(headers, results)


def analise_fases_planejamento(cursor):
    """Análise da tabela fases_planejamento"""
    print_section("🎯 ANÁLISE: fases_planejamento")
    
    # Listar todas as fases
    query = """
    SELECT 
      id,
      nome,
      status,
      data_inicio,
      data_fim,
      ROUND(progresso_percentual::numeric, 1) as progresso,
      meta_cidades,
      meta_motoristas,
      meta_corridas
    FROM fases_planejamento
    ORDER BY id;
    """
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("📅 Fases Cadastradas:")
    headers = ["ID", "Nome", "Status", "Início", "Fim", "Progresso%", "Meta Cid.", "Meta Mot.", "Meta Corr."]
    print_table(headers, results)


def analise_cidades_demografia(cursor):
    """Análise da tabela cidades_demografia"""
    print_section("🏙️ ANÁLISE: cidades_demografia")
    
    query = """
    SELECT 
      cidade,
      populacao_estimada_2024,
      populacao_15_44_anos,
      CASE 
        WHEN populacao_estimada_2024 > 0 
        THEN ROUND((populacao_15_44_anos::numeric / populacao_estimada_2024::numeric) * 100, 1)
        ELSE 0
      END as percentual_publico_alvo
    FROM cidades_demografia
    ORDER BY populacao_estimada_2024 DESC
    LIMIT 15;
    """
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("👥 Dados Demográficos:")
    headers = ["Cidade", "População Total", "População 15-44 anos", "% Público-Alvo"]
    print_table(headers, results)


def cidades_sem_metas(cursor):
    """Identifica cidades sem metas cadastradas"""
    print_section("🔍 CIDADES SEM METAS")
    
    query = """
    SELECT 
      c.id,
      c.cidade,
      c.populacao_estimada_2024
    FROM cidades_demografia c
    LEFT JOIN metas_progressivas m ON c.id = m.cidade_id
    WHERE m.id IS NULL
    ORDER BY c.cidade;
    """
    cursor.execute(query)
    results = cursor.fetchall()
    
    if results:
        print(f"⚠️ Encontradas {len(results)} cidades sem metas cadastradas:")
        headers = ["ID", "Cidade", "População"]
        print_table(headers, results)
        print(f"\n💡 Sugestão: Executar script de população de metas para estas cidades")
    else:
        print("✅ Todas as cidades têm metas cadastradas!")


def gerar_resumo_final(cursor):
    """Gera resumo executivo"""
    print_section("📋 RESUMO EXECUTIVO")
    
    # Contar totais
    cursor.execute("SELECT COUNT(*) FROM cidades_demografia")
    total_cidades = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM metas_progressivas")
    total_metas = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM fases_planejamento")
    total_fases = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM metas_progressivas WHERE resultado_corridas > 0")
    metas_com_resultados = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT cidade_id) FROM metas_progressivas")
    cidades_com_metas = cursor.fetchone()[0]
    
    print(f"🏙️  Total de cidades: {total_cidades}")
    print(f"📊 Total de metas cadastradas: {total_metas}")
    print(f"🎯 Total de fases: {total_fases}")
    print(f"✅ Metas com resultados reais: {metas_com_resultados}")
    print(f"🗺️  Cidades com metas: {cidades_com_metas}")
    
    if total_metas > 0:
        percentual = (metas_com_resultados / total_metas) * 100
        print(f"\n📈 Percentual de metas com dados reais: {percentual:.1f}%")
        
        if percentual < 10:
            print("\n⚠️  ALERTA: Poucos dados reais! Banco precisa ser populado.")
        elif percentual < 50:
            print("\n⏳ ATENÇÃO: Banco parcialmente populado.")
        else:
            print("\n✅ Banco bem populado com dados reais.")
    else:
        print("\n❌ CRÍTICO: Nenhuma meta cadastrada! Execute script de população.")
    
    print("\n" + "="*80)


def main():
    """Função principal"""
    print("\n" + "="*80)
    print("  🗄️  ANÁLISE DO BANCO DE DADOS - METAS POR CIDADE")
    print("  📅 Data: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print("="*80)
    
    conn = conectar_banco()
    if not conn:
        print("\n❌ Não foi possível conectar ao banco de dados.")
        print(f"   Host: {DB_HOST}:{DB_PORT}")
        print(f"   Database: {DB_NAME}")
        print(f"   User: {DB_USER}")
        return
    
    print(f"\n✅ Conectado ao banco: {DB_NAME}@{DB_HOST}")
    
    cursor = conn.cursor()
    
    try:
        # Executar todas as análises
        analise_metas_progressivas(cursor)
        analise_fases_planejamento(cursor)
        analise_cidades_demografia(cursor)
        cidades_sem_metas(cursor)
        gerar_resumo_final(cursor)
        
        print("\n✅ Análise concluída com sucesso!")
        print("\n💡 Próximos passos:")
        print("  1. Se banco estiver vazio/incompleto, executar: python popular_metas_base.py")
        print("  2. Verificar se há cidades sem metas e popular")
        print("  3. Integrar com rides_data para preencher resultados reais")
        
    except Exception as e:
        print(f"\n❌ Erro ao executar análise: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
