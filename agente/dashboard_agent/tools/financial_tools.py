#!/usr/bin/env python3
"""
Ferramentas Financeiras para o Agente de Mobilidade
Baseado no workflow n8n para gestão de gastos da empresa
"""

import os
import random
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Configurar logging
logger = logging.getLogger(__name__)

class GastoEmpresa(BaseModel):
    """Modelo para gastos da empresa"""
    id: Optional[int] = Field(None, description="ID único do gasto (gerado automaticamente se não fornecido)")
    data_despesa: Optional[str] = Field(None, description="Data da despesa (YYYY-MM-DD)")
    valor_total: Optional[float] = Field(None, description="Valor total da despesa")
    descricao_item: Optional[str] = Field(None, description="Descrição do item/serviço")
    tipo_documento: Optional[str] = Field(None, description="Tipo do documento (Comprovante, Nota Fiscal)")
    fornecedor: Optional[str] = Field(None, description="Nome do fornecedor")
    natureza_do_gasto: Optional[str] = Field(None, description="Natureza: Alimentação, Transporte, Material de Escritório, Serviços, Marketing, Viagem, Outros")
    descricao_imagem: Optional[str] = Field(None, description="Descrição extraída da imagem do documento")
    arquivo_drive_url: Optional[str] = Field(None, description="URL do arquivo no Google Drive")
    possui_nota_fiscal: Optional[bool] = Field(None, description="Se possui nota fiscal correspondente")
    id_documento_vinculado: Optional[int] = Field(None, description="ID do documento vinculado (NF)")
    status_documentacao: Optional[str] = Field(None, description="Status da documentação")
    observacoes: Optional[str] = Field(None, description="Observações adicionais")
    numero_nota_fiscal: Optional[str] = Field(None, description="Número da nota fiscal")
    serie_nota_fiscal: Optional[str] = Field(None, description="Série da nota fiscal")
    chave_acesso_nfe: Optional[str] = Field(None, description="Chave de acesso da NFe")
    cnpj_emissor: Optional[str] = Field(None, description="CNPJ do emissor")
    inscricao_estadual: Optional[str] = Field(None, description="Inscrição estadual")
    data_processamento: Optional[str] = Field(None, description="Data de processamento")

from agno.tools import Toolkit

class FinancialTools(Toolkit):
    """Ferramentas financeiras para gestão de gastos da empresa"""
    
    def __init__(self):
        # Configurar URL do banco para psycopg2 (remover asyncpg)
        db_url = os.getenv("DATABASE_URL", "postgresql://n8n_user:n8n_pw@148.230.73.27:5432/n8n_db")
        if "postgresql+asyncpg://" in db_url:
            self.db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        else:
            self.db_url = db_url
        
        # ✅ DEFINIR FERRAMENTAS COMO MÉTODOS - INCLUINDO NOVAS PARA CONSULTAS INTELIGENTES
        tools = [
            self.inserir_gasto_empresa,
            self.atualizar_gasto_empresa,
            self.consultar_gastos_empresa,
            self.validar_documentacao_fiscal,
            self.obter_resumo_financeiro,
            self.consultar_gastos_por_periodo,
            self.consultar_gastos_por_categoria,
            self.calcular_total_gastos_geral
        ]
        
        # ✅ INICIALIZAR COMO TOOLKIT
        super().__init__(name="financial_tools", tools=tools)
        logger.info(f"✅ [INIT] FinancialTools inicializado com {len(tools)} ferramentas")
    
    def _get_connection(self):
        """Obtém conexão com PostgreSQL"""
        try:
            return psycopg2.connect(self.db_url)
        except Exception as e:
            logger.error(f"Erro ao conectar PostgreSQL: {e}")
            raise
    
    def _generate_unique_id(self, conn, max_attempts=5):
        """Gera ID único para a tabela"""
        for attempt in range(max_attempts):
            new_id = random.randint(100000, 999999)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM gastos_empresa WHERE id = %s", (new_id,))
            if not cursor.fetchone():
                cursor.close()
                return new_id
            cursor.close()
        raise Exception("Não foi possível gerar ID único após 5 tentativas")
    
    def inserir_gasto_empresa(self, 
                             descricao_imagem: str,
                             arquivo_drive_url: str,
                             data_despesa: Optional[str] = None,
                             valor_total: Optional[float] = None,
                             descricao_item: Optional[str] = None,
                             tipo_documento: str = "Comprovante",
                             fornecedor: Optional[str] = None) -> Dict[str, Any]:
        """
        ETAPA 1: Insere um novo gasto na empresa baseado na descrição da imagem e URL do arquivo.
        Esta é a primeira ferramenta que deve ser usada ao receber dados de despesa.
        
        Args:
            descricao_imagem: Descrição extraída da imagem do documento
            arquivo_drive_url: URL do arquivo salvo no Google Drive
            data_despesa: Data da despesa (formato YYYY-MM-DD)
            valor_total: Valor total da despesa
            descricao_item: Descrição do item/serviço
            tipo_documento: Tipo do documento (Comprovante ou Nota Fiscal)
            fornecedor: Nome do fornecedor
            
        Returns:
            Dict com resultado da inserção incluindo o ID gerado
        """
        try:
            with self._get_connection() as conn:
                # Gerar ID único
                new_id = self._generate_unique_id(conn)
                
                # Preparar dados para inserção
                gasto = GastoEmpresa(
                    id=new_id,
                    data_despesa=data_despesa or datetime.now().strftime("%Y-%m-%d"),
                    valor_total=valor_total,
                    descricao_item=descricao_item,
                    tipo_documento=tipo_documento,
                    fornecedor=fornecedor,
                    descricao_imagem=descricao_imagem,
                    arquivo_drive_url=arquivo_drive_url,
                    data_processamento=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                
                # Query de inserção
                cursor = conn.cursor()
                insert_query = """
                INSERT INTO gastos_empresa (
                    id, data_despesa, valor_total, descricao_item, tipo_documento,
                    fornecedor, descricao_imagem, arquivo_drive_url, data_processamento
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(insert_query, (
                    gasto.id, gasto.data_despesa, gasto.valor_total, gasto.descricao_item,
                    gasto.tipo_documento, gasto.fornecedor, gasto.descricao_imagem,
                    gasto.arquivo_drive_url, gasto.data_processamento
                ))
                
                conn.commit()
                cursor.close()
                
                return {
                    "sucesso": True,
                    "id_inserido": new_id,
                    "mensagem": f"Dados inseridos com sucesso! ID: {new_id}. Agora preciso de mais informações:\n\n1) Este comprovante possui Nota Fiscal correspondente? (Sim/Não)\n2) Qual a natureza deste gasto? (Alimentação, Transporte, Material de Escritório, Serviços, Marketing, Viagem, Outros)\n3) Confirme se o nome do fornecedor extraído está correto: {fornecedor or 'Não identificado'}",
                    "gasto_inserido": gasto.dict()
                }
                
        except Exception as e:
            logger.error(f"Erro ao inserir gasto: {e}")
            return {
                "sucesso": False,
                "erro": str(e),
                "mensagem": "Erro ao inserir dados. Tentando novamente com ID diferente..."
            }
    
    def atualizar_gasto_empresa(self,
                               id_gasto: int,
                               possui_nota_fiscal: Optional[bool] = None,
                               natureza_do_gasto: Optional[str] = None,
                               fornecedor: Optional[str] = None,
                               id_documento_vinculado: Optional[int] = None,
                               status_documentacao: Optional[str] = None,
                               observacoes: Optional[str] = None,
                               numero_nota_fiscal: Optional[str] = None,
                               serie_nota_fiscal: Optional[str] = None,
                               chave_acesso_nfe: Optional[str] = None,
                               cnpj_emissor: Optional[str] = None,
                               inscricao_estadual: Optional[str] = None) -> Dict[str, Any]:
        """
        ETAPA 3: Atualiza um gasto existente com informações adicionais sobre nota fiscal e natureza do gasto.
        Use o ID retornado pela inserção inicial.
        
        Args:
            id_gasto: ID do gasto a ser atualizado (retornado pela inserção)
            possui_nota_fiscal: Se possui nota fiscal correspondente
            natureza_do_gasto: Natureza do gasto (Alimentação, Transporte, etc.)
            fornecedor: Nome correto do fornecedor
            id_documento_vinculado: ID da nota fiscal vinculada
            status_documentacao: Status da documentação
            observacoes: Observações adicionais
            numero_nota_fiscal: Número da nota fiscal
            serie_nota_fiscal: Série da nota fiscal
            chave_acesso_nfe: Chave de acesso da NFe
            cnpj_emissor: CNPJ do emissor
            inscricao_estadual: Inscrição estadual
            
        Returns:
            Dict com resultado da atualização
        """
        try:
            with self._get_connection() as conn:
                # Construir query dinâmica baseada nos campos fornecidos
                campos_update = []
                valores = []
                
                if possui_nota_fiscal is not None:
                    campos_update.append("possui_nota_fiscal = %s")
                    valores.append(possui_nota_fiscal)
                
                if natureza_do_gasto:
                    campos_update.append("natureza_do_gasto = %s")
                    valores.append(natureza_do_gasto)
                
                if fornecedor:
                    campos_update.append("fornecedor = %s")
                    valores.append(fornecedor)
                
                if id_documento_vinculado:
                    campos_update.append("id_documento_vinculado = %s")
                    valores.append(id_documento_vinculado)
                
                if status_documentacao:
                    campos_update.append("status_documentacao = %s")
                    valores.append(status_documentacao)
                
                if observacoes:
                    campos_update.append("observacoes = %s")
                    valores.append(observacoes)
                
                if numero_nota_fiscal:
                    campos_update.append("numero_nota_fiscal = %s")
                    valores.append(numero_nota_fiscal)
                
                if serie_nota_fiscal:
                    campos_update.append("serie_nota_fiscal = %s")
                    valores.append(serie_nota_fiscal)
                
                if chave_acesso_nfe:
                    campos_update.append("chave_acesso_nfe = %s")
                    valores.append(chave_acesso_nfe)
                
                if cnpj_emissor:
                    campos_update.append("cnpj_emissor = %s")
                    valores.append(cnpj_emissor)
                
                if inscricao_estadual:
                    campos_update.append("inscricao_estadual = %s")
                    valores.append(inscricao_estadual)
                
                if not campos_update:
                    return {
                        "sucesso": False,
                        "erro": "Nenhum campo para atualizar foi fornecido"
                    }
                
                # Adicionar ID para WHERE
                valores.append(id_gasto)
                
                update_query = f"""
                UPDATE gastos_empresa 
                SET {', '.join(campos_update)}
                WHERE id = %s
                """
                
                cursor = conn.cursor()
                cursor.execute(update_query, valores)
                
                if cursor.rowcount == 0:
                    cursor.close()
                    return {
                        "sucesso": False,
                        "erro": f"Nenhum registro encontrado com ID {id_gasto}"
                    }
                
                conn.commit()
                cursor.close()
                
                return {
                    "sucesso": True,
                    "id_atualizado": id_gasto,
                    "campos_atualizados": len(campos_update),
                    "mensagem": f"Gasto ID {id_gasto} atualizado com sucesso!"
                }
                
        except Exception as e:
            logger.error(f"Erro ao atualizar gasto: {e}")
            return {
                "sucesso": False,
                "erro": str(e)
            }
    
    def consultar_gastos_empresa(self,
                                id_gasto: Optional[int] = None,
                                fornecedor: Optional[str] = None,
                                natureza_do_gasto: Optional[str] = None,
                                data_inicio: Optional[str] = None,
                                data_fim: Optional[str] = None,
                                limite: int = 10) -> Dict[str, Any]:
        """
        Consulta gastos da empresa com filtros opcionais.
        
        Args:
            id_gasto: ID específico do gasto
            fornecedor: Nome do fornecedor
            natureza_do_gasto: Natureza do gasto
            data_inicio: Data inicial (YYYY-MM-DD)
            data_fim: Data final (YYYY-MM-DD)
            limite: Limite de registros retornados
            
        Returns:
            Dict com lista de gastos encontrados
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                
                # Construir query dinâmica
                where_clauses = []
                valores = []
                
                if id_gasto:
                    where_clauses.append("id = %s")
                    valores.append(id_gasto)
                
                if fornecedor:
                    where_clauses.append("fornecedor ILIKE %s")
                    valores.append(f"%{fornecedor}%")
                
                if natureza_do_gasto:
                    where_clauses.append("natureza_do_gasto = %s")
                    valores.append(natureza_do_gasto)
                
                if data_inicio:
                    where_clauses.append("data_despesa >= %s")
                    valores.append(data_inicio)
                
                if data_fim:
                    where_clauses.append("data_despesa <= %s")
                    valores.append(data_fim)
                
                where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
                
                query = f"""
                SELECT * FROM gastos_empresa
                {where_sql}
                ORDER BY data_despesa DESC, id DESC
                LIMIT %s
                """
                valores.append(limite)
                
                cursor.execute(query, valores)
                resultados = cursor.fetchall()
                cursor.close()
                
                return {
                    "sucesso": True,
                    "total_encontrados": len(resultados),
                    "gastos": [dict(row) for row in resultados]
                }
                
        except Exception as e:
            logger.error(f"Erro ao consultar gastos: {e}")
            return {
                "sucesso": False,
                "erro": str(e)
            }
    
    def validar_documentacao_fiscal(self, id_gasto: int) -> Dict[str, Any]:
        """
        Valida se a documentação fiscal está completa para um gasto.
        
        Args:
            id_gasto: ID do gasto a ser validado
            
        Returns:
            Dict com status da validação
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                
                cursor.execute("SELECT * FROM gastos_empresa WHERE id = %s", (id_gasto,))
                gasto = cursor.fetchone()
                cursor.close()
                
                if not gasto:
                    return {
                        "sucesso": False,
                        "erro": f"Gasto com ID {id_gasto} não encontrado"
                    }
                
                gasto = dict(gasto)
                
                # Verificar completude da documentação
                problemas = []
                
                if not gasto.get('fornecedor'):
                    problemas.append("Fornecedor não informado")
                
                if not gasto.get('natureza_do_gasto'):
                    problemas.append("Natureza do gasto não informada")
                
                if gasto.get('possui_nota_fiscal') and not gasto.get('numero_nota_fiscal'):
                    problemas.append("Possui NF mas número da nota não informado")
                
                if not gasto.get('arquivo_drive_url'):
                    problemas.append("URL do arquivo não informada")
                
                status = "COMPLETO" if not problemas else "INCOMPLETO"
                
                return {
                    "sucesso": True,
                    "id_gasto": id_gasto,
                    "status_documentacao": status,
                    "problemas_encontrados": problemas,
                    "possui_nota_fiscal": gasto.get('possui_nota_fiscal', False),
                    "fornecedor": gasto.get('fornecedor'),
                    "natureza_do_gasto": gasto.get('natureza_do_gasto'),
                    "valor_total": gasto.get('valor_total')
                }
                
        except Exception as e:
            logger.error(f"Erro ao validar documentação: {e}")
            return {
                "sucesso": False,
                "erro": str(e)
            }

    def buscar_gastos_pendentes_usuario(self, user_name: str) -> Optional[Dict[str, Any]]:
        """
        Buscar gastos recentes do usuário que ainda estão pendentes de informações complementares
        (útil para recuperar contexto de fluxos de registro ativos)
        """
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Buscar gastos inseridos nas últimas 2 horas que ainda não têm todos os campos preenchidos
                    cursor.execute("""
                        SELECT id, data_despesa, valor_total, descricao_item, fornecedor, 
                               natureza_do_gasto, possui_nota_fiscal, data_processamento
                        FROM gastos_empresa 
                        WHERE (observacoes LIKE %s OR observacoes IS NULL)
                        AND data_processamento::timestamp >= NOW() - INTERVAL '2 hours'
                        AND (natureza_do_gasto IS NULL OR possui_nota_fiscal IS NULL)
                        ORDER BY data_processamento::timestamp DESC 
                        LIMIT 1
                    """, (f'%{user_name}%',))
                    
                    gasto = cursor.fetchone()
                    
                    if gasto:
                        return {
                            "gasto_id": gasto['id'],
                            "data_despesa": str(gasto['data_despesa']),
                            "valor_total": float(gasto['valor_total']) if gasto['valor_total'] else 0,
                            "fornecedor": gasto['fornecedor'],
                            "natureza_do_gasto": gasto['natureza_do_gasto'],
                            "possui_nota_fiscal": gasto['possui_nota_fiscal']
                        }
                    
                    return None
                    
        except Exception as e:
            logger.error(f"Erro ao buscar gastos pendentes: {e}")
            return None

    def obter_resumo_financeiro(self) -> Dict[str, Any]:
        """
        Obtém um resumo completo dos gastos registrados no sistema.
        
        Returns:
            Dict com resumo financeiro incluindo totais, quantidade e estatísticas
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                
                # Total geral de gastos
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_registros,
                        COALESCE(SUM(valor_total), 0) as total_gastos,
                        COALESCE(AVG(valor_total), 0) as ticket_medio,
                        MIN(data_despesa) as primeira_despesa,
                        MAX(data_despesa) as ultima_despesa
                    FROM gastos_empresa 
                    WHERE valor_total IS NOT NULL
                """)
                resumo_geral = cursor.fetchone()
                
                # Gastos por categoria
                cursor.execute("""
                    SELECT 
                        natureza_do_gasto,
                        COUNT(*) as quantidade,
                        COALESCE(SUM(valor_total), 0) as total_categoria
                    FROM gastos_empresa 
                    WHERE valor_total IS NOT NULL 
                    AND natureza_do_gasto IS NOT NULL
                    GROUP BY natureza_do_gasto
                    ORDER BY total_categoria DESC
                """)
                gastos_por_categoria = cursor.fetchall()
                
                cursor.close()
                
                return {
                    "sucesso": True,
                    "total_gastos": float(resumo_geral['total_gastos']),
                    "quantidade_gastos": int(resumo_geral['total_registros']),
                    "ticket_medio": float(resumo_geral['ticket_medio']),
                    "primeira_despesa": str(resumo_geral['primeira_despesa']) if resumo_geral['primeira_despesa'] else None,
                    "ultima_despesa": str(resumo_geral['ultima_despesa']) if resumo_geral['ultima_despesa'] else None,
                    "gastos_por_categoria": [dict(row) for row in gastos_por_categoria]
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter resumo financeiro: {e}")
            return {
                "sucesso": False,
                "erro": str(e)
            }

    def consultar_gastos_por_periodo(self, data_inicio: str, data_fim: str) -> Dict[str, Any]:
        """
        Consulta gastos em um período específico.
        
        Args:
            data_inicio: Data inicial no formato YYYY-MM-DD
            data_fim: Data final no formato YYYY-MM-DD
            
        Returns:
            Dict com gastos do período e estatísticas
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                
                # Consultar gastos do período
                cursor.execute("""
                    SELECT 
                        COUNT(*) as quantidade_gastos,
                        COALESCE(SUM(valor_total), 0) as total_gastos,
                        COALESCE(AVG(valor_total), 0) as ticket_medio
                    FROM gastos_empresa 
                    WHERE data_despesa >= %s 
                    AND data_despesa <= %s 
                    AND valor_total IS NOT NULL
                """, (data_inicio, data_fim))
                
                estatisticas = cursor.fetchone()
                
                # Detalhes dos gastos
                cursor.execute("""
                    SELECT id, data_despesa, valor_total, descricao_item, 
                           fornecedor, natureza_do_gasto, tipo_documento
                    FROM gastos_empresa 
                    WHERE data_despesa >= %s 
                    AND data_despesa <= %s 
                    ORDER BY data_despesa DESC, valor_total DESC
                """, (data_inicio, data_fim))
                
                gastos_detalhados = cursor.fetchall()
                cursor.close()
                
                return {
                    "sucesso": True,
                    "periodo": f"{data_inicio} a {data_fim}",
                    "total_gastos": float(estatisticas['total_gastos']),
                    "quantidade_gastos": int(estatisticas['quantidade_gastos']),
                    "ticket_medio": float(estatisticas['ticket_medio']),
                    "gastos_detalhados": [dict(row) for row in gastos_detalhados]
                }
                
        except Exception as e:
            logger.error(f"Erro ao consultar gastos por período: {e}")
            return {
                "sucesso": False,
                "erro": str(e)
            }

    def consultar_gastos_por_categoria(self, categoria: str) -> Dict[str, Any]:
        """
        Consulta gastos de uma categoria específica.
        
        Args:
            categoria: Nome da categoria (Alimentação, Transporte, etc.)
            
        Returns:
            Dict com gastos da categoria e estatísticas
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                
                # Estatísticas da categoria
                cursor.execute("""
                    SELECT 
                        COUNT(*) as quantidade_gastos,
                        COALESCE(SUM(valor_total), 0) as total_gastos,
                        COALESCE(AVG(valor_total), 0) as ticket_medio,
                        MIN(data_despesa) as primeira_despesa,
                        MAX(data_despesa) as ultima_despesa
                    FROM gastos_empresa 
                    WHERE natureza_do_gasto = %s 
                    AND valor_total IS NOT NULL
                """, (categoria,))
                
                estatisticas = cursor.fetchone()
                
                # Detalhes dos gastos da categoria
                cursor.execute("""
                    SELECT id, data_despesa, valor_total, descricao_item, 
                           fornecedor, tipo_documento
                    FROM gastos_empresa 
                    WHERE natureza_do_gasto = %s 
                    ORDER BY data_despesa DESC, valor_total DESC
                    LIMIT 20
                """, (categoria,))
                
                gastos_detalhados = cursor.fetchall()
                cursor.close()
                
                return {
                    "sucesso": True,
                    "categoria": categoria,
                    "total_gastos": float(estatisticas['total_gastos']),
                    "quantidade_gastos": int(estatisticas['quantidade_gastos']),
                    "ticket_medio": float(estatisticas['ticket_medio']),
                    "primeira_despesa": str(estatisticas['primeira_despesa']) if estatisticas['primeira_despesa'] else None,
                    "ultima_despesa": str(estatisticas['ultima_despesa']) if estatisticas['ultima_despesa'] else None,
                    "gastos_detalhados": [dict(row) for row in gastos_detalhados]
                }
                
        except Exception as e:
            logger.error(f"Erro ao consultar gastos por categoria: {e}")
            return {
                "sucesso": False,
                "erro": str(e)
            }

    def calcular_total_gastos_geral(self) -> Dict[str, Any]:
        """
        Calcula o total geral de todos os gastos registrados.
        
        Returns:
            Dict com total geral e estatísticas básicas
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_registros,
                        COALESCE(SUM(valor_total), 0) as total_gastos,
                        COALESCE(AVG(valor_total), 0) as ticket_medio,
                        MIN(valor_total) as menor_gasto,
                        MAX(valor_total) as maior_gasto
                    FROM gastos_empresa 
                    WHERE valor_total IS NOT NULL
                """)
                
                resultado = cursor.fetchone()
                cursor.close()
                
                return {
                    "sucesso": True,
                    "total_gastos": float(resultado['total_gastos']),
                    "total_registros": int(resultado['total_registros']),
                    "ticket_medio": float(resultado['ticket_medio']),
                    "menor_gasto": float(resultado['menor_gasto']) if resultado['menor_gasto'] else 0,
                    "maior_gasto": float(resultado['maior_gasto']) if resultado['maior_gasto'] else 0
                }
                
        except Exception as e:
            logger.error(f"Erro ao calcular total geral: {e}")
            return {
                "sucesso": False,
                "erro": str(e)
            }

# Exportar para uso no agente
__all__ = ["FinancialTools"]
