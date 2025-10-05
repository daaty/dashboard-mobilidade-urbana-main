"""
API endpoints para analytics e gráficos da aba de Motoristas
Baseado nos 5 tipos de dados: Active Drivers, Driver Performance, Drivers Enrollment, Leaderboard, Deactive Drivers
"""

from fastapi import APIRouter, HTTPException, Query
import psycopg2
from datetime import datetime, timedelta
from typing import Optional
import json

router = APIRouter()

# Configuração do banco
DB_CONFIG = {
    'host': '148.230.73.27',
    'port': 5432,
    'database': 'n8n_db',
    'user': 'n8n_user',
    'password': 'n8n_pw'
}

def get_db_connection():
    """Estabelece conexão com PostgreSQL"""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão com o banco: {str(e)}")

def get_period_date_filter(period: str) -> Optional[datetime]:
    """
    Converte o período selecionado em uma data de início para filtro
    Períodos: hoje, 7_days, 30_days, 3_months, 6_months, 12_months
    """
    now = datetime.now()
    
    if period == 'hoje':
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == '7_days':
        return now - timedelta(days=7)
    elif period == '30_days':
        return now - timedelta(days=30)
    elif period == '3_months':
        return now - timedelta(days=90)
    elif period == '6_months':
        return now - timedelta(days=180)
    elif period == '12_months':
        return now - timedelta(days=365)
    else:
        return None  # Sem filtro de data (todos os dados)


# ===================================================================
# 1. DISTRIBUIÇÃO POR CIDADE (Active Drivers)
# ===================================================================
@router.get("/drivers/analytics/by-city")
def get_drivers_by_city(
    period: str = Query(None, description="Período: hoje, 7_days, 30_days, 3_months, 6_months, 12_months")
):
    """
    Retorna distribuição de motoristas ativos por cidade
    Fonte: Active Drivers -> additional_data->>'City'
    Filtrado por período se especificado
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        start_date = get_period_date_filter(period)
        date_filter = ""
        if start_date:
            date_filter = "AND scraped_at >= %s"
        
        query = f"""
            SELECT 
                additional_data->>'City' as cidade,
                COUNT(DISTINCT driver_id) as total_motoristas,
                COUNT(*) as total_registros
            FROM drivers_data
            WHERE additional_data->>'City' IS NOT NULL
                AND additional_data->>'City' != ''
                AND data_type = 'active'
                {date_filter}
            GROUP BY additional_data->>'City'
            ORDER BY total_motoristas DESC;
        """
        
        if start_date:
            cursor.execute(query, (start_date,))
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        
        data = [
            {
                "cidade": row[0],
                "total": row[1],
                "registros": row[2]
            }
            for row in result
        ]
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "data": data,
            "total_cidades": len(data)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# 2. TOP PERFORMERS (Driver Performance)
# ===================================================================
@router.get("/drivers/analytics/top-performers")
def get_top_performers(
    limit: int = 10,
    period: str = Query(None, description="Período: hoje, 7_days, 30_days, 3_months, 6_months, 12_months")
):
    """
    Retorna os top motoristas por corridas realizadas no período
    Fonte: driver_personal_details -> rides_history (data real das corridas)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obter data de início baseada no período
        start_date = get_period_date_filter(period)
        
        if start_date:
            # Filtrar corridas por data real (drop_time)
            query = f"""
                WITH rides_data AS (
                    SELECT 
                        d.driver_id,
                        d.personal_data->>'driver_name' as driver_name,
                        d.personal_data->>'phone_no' as phone_no,
                        jsonb_array_elements(d.rides_history) as ride
                    FROM driver_personal_details d
                    WHERE d.rides_history IS NOT NULL 
                        AND jsonb_array_length(d.rides_history) > 0
                ),
                filtered_rides AS (
                    SELECT 
                        driver_id,
                        driver_name,
                        phone_no,
                        ride
                    FROM rides_data
                    WHERE TO_TIMESTAMP(ride->>'drop_time', 'DD/MM/YYYY : HH:MI am') >= '{start_date.isoformat()}'
                        OR TO_TIMESTAMP(ride->>'drop_time', 'DD/MM/YYYY : HH:MI pm') >= '{start_date.isoformat()}'
                )
                SELECT 
                    driver_name as name,
                    driver_id,
                    COUNT(*) as success_rides,
                    0 as online_hours,
                    0 as rejected_rides,
                    0 as missed_rides,
                    phone_no as phone
                FROM filtered_rides
                GROUP BY driver_id, driver_name, phone_no
                HAVING COUNT(*) > 0
                ORDER BY success_rides DESC
                LIMIT %s;
            """
        else:
            # Sem filtro de período - todas as corridas
            query = """
                SELECT 
                    d.personal_data->>'driver_name' as name,
                    d.driver_id,
                    jsonb_array_length(d.rides_history) as success_rides,
                    0 as online_hours,
                    0 as rejected_rides,
                    0 as missed_rides,
                    d.personal_data->>'phone_no' as phone
                FROM driver_personal_details d
                WHERE d.rides_history IS NOT NULL 
                    AND jsonb_array_length(d.rides_history) > 0
                ORDER BY success_rides DESC
                LIMIT %s;
            """
        
        cursor.execute(query, (limit,))
        
        result = cursor.fetchall()
        
        data = [
            {
                "name": row[0],
                "driver_id": row[1],
                "success_rides": int(row[2]) if row[2] else 0,
                "online_hours": float(row[3]) if row[3] else 0,
                "rejected_rides": int(row[4]) if row[4] else 0,
                "missed_rides": int(row[5]) if row[5] else 0,
                "phone": row[6]
            }
            for row in result
        ]
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "data": data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# 3. DISTRIBUIÇÃO DE AVALIAÇÕES (Active Drivers)
# ===================================================================
@router.get("/drivers/analytics/ratings-distribution")
def get_ratings_distribution():
    """
    Retorna distribuição de avaliações dos motoristas ativos
    Fonte: Active Drivers -> additional_data->>'Driver Ratings'
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                CASE 
                    WHEN CAST(additional_data->>'Driver Ratings' AS FLOAT) >= 4.8 THEN '4.8 - 5.0'
                    WHEN CAST(additional_data->>'Driver Ratings' AS FLOAT) >= 4.5 THEN '4.5 - 4.7'
                    WHEN CAST(additional_data->>'Driver Ratings' AS FLOAT) >= 4.0 THEN '4.0 - 4.4'
                    WHEN CAST(additional_data->>'Driver Ratings' AS FLOAT) >= 3.5 THEN '3.5 - 3.9'
                    WHEN CAST(additional_data->>'Driver Ratings' AS FLOAT) >= 3.0 THEN '3.0 - 3.4'
                    ELSE '< 3.0'
                END as faixa_avaliacao,
                COUNT(*) as quantidade
            FROM drivers_data
            WHERE additional_data->>'Driver Ratings' IS NOT NULL
                AND additional_data->>'Driver Ratings' != ''
                AND data_type = 'active'
            GROUP BY faixa_avaliacao
            ORDER BY faixa_avaliacao DESC;
        """
        
        cursor.execute(query)
        result = cursor.fetchall()
        
        data = [
            {
                "faixa": row[0],
                "quantidade": row[1]
            }
            for row in result
        ]
        
        # Calcular média geral
        avg_query = """
            SELECT 
                AVG(CAST(additional_data->>'Driver Ratings' AS FLOAT)) as media_geral,
                COUNT(*) as total_avaliados
            FROM drivers_data
            WHERE additional_data->>'Driver Ratings' IS NOT NULL
                AND additional_data->>'Driver Ratings' != ''
                AND data_type = 'active';
        """
        
        cursor.execute(avg_query)
        avg_result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "data": data,
            "summary": {
                "media_geral": round(float(avg_result[0]), 2) if avg_result[0] else 0,
                "total_avaliados": avg_result[1]
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# 4. CADASTROS RECENTES (Drivers Enrollment)
# ===================================================================
@router.get("/drivers/analytics/recent-enrollments")
def get_recent_enrollments(days: int = 30):
    """
    Retorna motoristas cadastrados recentemente
    Fonte: Drivers Enrollment -> additional_data->>'Registered On'
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Últimos cadastros
        query = """
            SELECT 
                driver_id,
                name,
                additional_data->>'Phone Number' as phone,
                additional_data->>'Registered On' as registered_on,
                additional_data->>'No of docs uploaded' as docs_status,
                additional_data->>'Action' as action,
                scraped_at
            FROM drivers_data
            WHERE data_type = 'enrollment'
            ORDER BY scraped_at DESC
            LIMIT 20;
        """
        
        cursor.execute(query)
        result = cursor.fetchall()
        
        enrollments = [
            {
                "driver_id": row[0],
                "name": row[1],
                "phone": row[2],
                "registered_on": row[3],
                "docs_status": row[4],
                "action": row[5],
                "scraped_at": row[6].isoformat() if row[6] else None
            }
            for row in result
        ]
        
        # Timeline de cadastros (últimos 30 dias)
        timeline_query = """
            SELECT 
                DATE(scraped_at) as data,
                COUNT(*) as novos_cadastros
            FROM drivers_data
            WHERE data_type = 'enrollment'
                AND scraped_at >= NOW() - INTERVAL '30 days'
            GROUP BY DATE(scraped_at)
            ORDER BY data DESC;
        """
        
        cursor.execute(timeline_query)
        timeline_result = cursor.fetchall()
        
        timeline = [
            {
                "data": row[0].isoformat(),
                "novos_cadastros": row[1]
            }
            for row in timeline_result
        ]
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "data": {
                "recent_enrollments": enrollments,
                "timeline": timeline
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# 5. MÉTRICAS DE PERFORMANCE AGREGADAS (Driver Performance)
# ===================================================================
@router.get("/drivers/analytics/performance-metrics")
def get_performance_metrics(
    period: str = Query(None, description="Período: hoje, 7_days, 30_days, 3_months, 6_months, 12_months")
):
    """
    Retorna métricas agregadas de performance dos motoristas no período
    Fonte: driver_personal_details -> rides_history (data real das corridas)
    MÉTRICAS REAIS baseadas em corridas efetivamente realizadas
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obter data de início baseada no período
        start_date = get_period_date_filter(period)
        
        if start_date:
            # Filtrar corridas por data real com validação de formato
            query = f"""
                WITH rides_data AS (
                    SELECT 
                        d.driver_id,
                        d.personal_data->>'driver_name' as driver_name,
                        jsonb_array_elements(d.rides_history) as ride
                    FROM driver_personal_details d
                    WHERE d.rides_history IS NOT NULL 
                        AND jsonb_array_length(d.rides_history) > 0
                ),
                filtered_rides AS (
                    SELECT 
                        driver_id,
                        driver_name,
                        ride,
                        CASE 
                            WHEN ride->>'drop_time' ~ '^\d{{2}}/\d{{2}}/\d{{4}} : \d{{1,2}}:\d{{2}} am$' 
                            THEN TO_TIMESTAMP(ride->>'drop_time', 'DD/MM/YYYY : HH:MI am')
                            WHEN ride->>'drop_time' ~ '^\d{{2}}/\d{{2}}/\d{{4}} : \d{{1,2}}:\d{{2}} pm$' 
                            THEN TO_TIMESTAMP(ride->>'drop_time', 'DD/MM/YYYY : HH12:MI pm')
                        END as drop_timestamp
                    FROM rides_data
                )
                SELECT 
                    COUNT(*) as total_rides,
                    COUNT(DISTINCT driver_id) as total_drivers,
                    SUM(CAST(NULLIF(ride->>'fare', '') AS FLOAT)) as total_revenue,
                    AVG(CAST(NULLIF(ride->>'fare', '') AS FLOAT)) as avg_ticket,
                    SUM(CAST(NULLIF(ride->>'duration', '') AS FLOAT)) as total_duration_minutes,
                    AVG(CAST(NULLIF(ride->>'duration', '') AS FLOAT)) as avg_duration_minutes,
                    SUM(CAST(NULLIF(ride->>'distance_travelled', '') AS FLOAT)) as total_distance_km,
                    AVG(CAST(NULLIF(ride->>'distance_travelled', '') AS FLOAT)) as avg_distance_km,
                    COUNT(DISTINCT driver_id) FILTER (WHERE drop_timestamp >= '{start_date.isoformat()}') as active_drivers_period
                FROM filtered_rides
                WHERE drop_timestamp >= '{start_date.isoformat()}';
            """
        else:
            # Sem filtro - todas as corridas
            query = """
                WITH rides_data AS (
                    SELECT 
                        d.driver_id,
                        d.personal_data->>'driver_name' as driver_name,
                        jsonb_array_elements(d.rides_history) as ride
                    FROM driver_personal_details d
                    WHERE d.rides_history IS NOT NULL 
                        AND jsonb_array_length(d.rides_history) > 0
                )
                SELECT 
                    COUNT(*) as total_rides,
                    COUNT(DISTINCT driver_id) as total_drivers,
                    SUM(CAST(NULLIF(ride->>'fare', '') AS FLOAT)) as total_revenue,
                    AVG(CAST(NULLIF(ride->>'fare', '') AS FLOAT)) as avg_ticket,
                    SUM(CAST(NULLIF(ride->>'duration', '') AS FLOAT)) as total_duration_minutes,
                    AVG(CAST(NULLIF(ride->>'duration', '') AS FLOAT)) as avg_duration_minutes,
                    SUM(CAST(NULLIF(ride->>'distance_travelled', '') AS FLOAT)) as total_distance_km,
                    AVG(CAST(NULLIF(ride->>'distance_travelled', '') AS FLOAT)) as avg_distance_km,
                    COUNT(DISTINCT driver_id) as active_drivers_period
                FROM rides_data;
            """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        # Distribuição de corridas por motorista
        rides_distribution_query = """
            WITH driver_rides AS (
                SELECT 
                    d.driver_id,
                    jsonb_array_length(d.rides_history) as total_rides
                FROM driver_personal_details d
                WHERE jsonb_array_length(d.rides_history) > 0
            )
            SELECT 
                CASE 
                    WHEN total_rides >= 50 THEN '50+ corridas'
                    WHEN total_rides >= 20 THEN '20-49 corridas'
                    WHEN total_rides >= 10 THEN '10-19 corridas'
                    WHEN total_rides >= 5 THEN '5-9 corridas'
                    ELSE '1-4 corridas'
                END as faixa_corridas,
                COUNT(*) as quantidade_motoristas
            FROM driver_rides
            GROUP BY faixa_corridas
            ORDER BY quantidade_motoristas DESC;
        """
        
        cursor.execute(rides_distribution_query)
        rides_dist = cursor.fetchall()
        
        # Distribuição por período do dia (AM/PM)
        period_distribution_query = """
            WITH rides_expanded AS (
                SELECT 
                    jsonb_array_elements(rides_history) as ride
                FROM driver_personal_details
                WHERE jsonb_array_length(rides_history) > 0
            )
            SELECT 
                CASE 
                    WHEN ride->>'drop_time' LIKE '%am%' THEN 'Manhã (AM)'
                    WHEN ride->>'drop_time' LIKE '%pm%' THEN 'Tarde/Noite (PM)'
                    ELSE 'Não identificado'
                END as periodo,
                COUNT(*) as quantidade
            FROM rides_expanded
            WHERE ride->>'drop_time' IS NOT NULL
            GROUP BY periodo
            ORDER BY quantidade DESC;
        """
        
        cursor.execute(period_distribution_query)
        period_dist = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "data": {
                "summary": {
                    "total_rides": int(result[0]) if result[0] else 0,
                    "total_drivers": int(result[1]) if result[1] else 0,
                    "total_revenue": round(float(result[2]), 2) if result[2] else 0,
                    "avg_ticket": round(float(result[3]), 2) if result[3] else 0,
                    "total_duration_hours": round(float(result[4]) / 60.0, 2) if result[4] else 0,
                    "avg_duration_minutes": round(float(result[5]), 1) if result[5] else 0,
                    "total_distance_km": round(float(result[6]), 2) if result[6] else 0,
                    "avg_distance_km": round(float(result[7]), 2) if result[7] else 0,
                    "active_drivers_period": int(result[8]) if result[8] else 0
                },
                "rides_distribution": [
                    {
                        "faixa": row[0],
                        "quantidade": row[1]
                    }
                    for row in rides_dist
                ],
                "period_distribution": [
                    {
                        "periodo": row[0],
                        "quantidade": row[1]
                    }
                    for row in period_dist
                ]
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# 6. ATIVIDADE ONLINE (Active Drivers - Last Login)
# ===================================================================
@router.get("/drivers/analytics/online-activity")
def get_online_activity():
    """
    Retorna análise de atividade baseada em Last Login
    Identifica motoristas que não estão ficando online
    Fonte: Active Drivers -> Last Login, Last Ride
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Motoristas por status
        status_query = """
            SELECT 
                additional_data->>'Status' as status,
                COUNT(*) as quantidade
            FROM drivers_data
            WHERE data_type = 'active'
                AND additional_data->>'Status' IS NOT NULL
            GROUP BY additional_data->>'Status';
        """
        
        cursor.execute(status_query)
        status_result = cursor.fetchall()
        
        # Atividade recente (7d vs 30d)
        activity_query = """
            SELECT 
                name,
                driver_id,
                additional_data->>'City' as cidade,
                additional_data->>'Status' as status,
                additional_data->>'Last Login' as last_login,
                additional_data->>'Last Ride' as last_ride,
                additional_data->>'Rides in Last 7 Days' as rides_7d,
                additional_data->>'Rides in Last 30 Days' as rides_30d,
                additional_data->>'Driver Ratings' as rating
            FROM drivers_data
            WHERE data_type = 'active'
            ORDER BY 
                CAST(COALESCE(NULLIF(additional_data->>'Rides in Last 30 Days', ''), '0') AS INTEGER) DESC
            LIMIT 20;
        """
        
        cursor.execute(activity_query)
        activity_result = cursor.fetchall()
        
        # Motoristas inativos (sem login recente ou offline)
        inactive_query = """
            SELECT 
                name,
                driver_id,
                additional_data->>'City' as cidade,
                additional_data->>'Status' as status,
                additional_data->>'Last Login' as last_login,
                additional_data->>'Phone Number' as phone
            FROM drivers_data
            WHERE data_type = 'active'
                AND additional_data->>'Status' = 'Offline'
                AND (additional_data->>'Rides in Last 7 Days' = '0' 
                     OR additional_data->>'Rides in Last 7 Days' IS NULL)
            LIMIT 15;
        """
        
        cursor.execute(inactive_query)
        inactive_result = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "data": {
                "status_distribution": [
                    {
                        "status": row[0],
                        "quantidade": row[1]
                    }
                    for row in status_result
                ],
                "top_active": [
                    {
                        "name": row[0],
                        "driver_id": row[1],
                        "cidade": row[2],
                        "status": row[3],
                        "last_login": row[4],
                        "last_ride": row[5],
                        "rides_7d": int(row[6]) if row[6] else 0,
                        "rides_30d": int(row[7]) if row[7] else 0,
                        "rating": row[8]
                    }
                    for row in activity_result
                ],
                "inactive_drivers": [
                    {
                        "name": row[0],
                        "driver_id": row[1],
                        "cidade": row[2],
                        "status": row[3],
                        "last_login": row[4],
                        "phone": row[5]
                    }
                    for row in inactive_result
                ]
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# 7. COMPARATIVO 7D vs 30D (Active Drivers)
# ===================================================================
@router.get("/drivers/analytics/activity-comparison")
def get_activity_comparison(limit: int = 15):
    """
    Retorna comparativo de corridas 7 dias vs 30 dias
    Fonte: Active Drivers -> Rides in Last 7 Days / Rides in Last 30 Days
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                name,
                driver_id,
                additional_data->>'City' as cidade,
                CAST(COALESCE(NULLIF(additional_data->>'Rides in Last 7 Days', ''), '0') AS INTEGER) as rides_7d,
                CAST(COALESCE(NULLIF(additional_data->>'Rides in Last 30 Days', ''), '0') AS INTEGER) as rides_30d,
                additional_data->>'Status' as status
            FROM drivers_data
            WHERE data_type = 'active'
                AND additional_data->>'Rides in Last 30 Days' IS NOT NULL
            ORDER BY rides_30d DESC
            LIMIT %s;
        """
        
        cursor.execute(query, (limit,))
        result = cursor.fetchall()
        
        data = [
            {
                "name": row[0],
                "driver_id": row[1],
                "cidade": row[2],
                "rides_7d": row[3],
                "rides_30d": row[4],
                "status": row[5]
            }
            for row in result
        ]
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "data": data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# 8. CITY GROWTH ANALYTICS
# ===================================================================
@router.get("/drivers/analytics/city-growth")
def get_city_growth(
    period: str = Query(None, description="Período: hoje, 7_days, 30_days, 3_months, 6_months, 12_months")
):
    """
    Retorna crescimento de motoristas cadastrados e ativos por cidade
    Compara cadastrados vs ativos para análise de engajamento
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        start_date = get_period_date_filter(period)
        
        # Query para motoristas cadastrados por cidade (usando joining_date do personal_data)
        if start_date:
            cadastrados_query = """
                WITH city_registrations AS (
                    SELECT 
                        city,
                        COUNT(DISTINCT driver_id) as total_cadastrados,
                        COUNT(DISTINCT CASE 
                            WHEN personal_data->>'joining_date' IS NOT NULL 
                                AND personal_data->>'joining_date' ~ '^\d{2}/\d{2}/\d{4}$'
                                AND TO_DATE(personal_data->>'joining_date', 'DD/MM/YYYY') >= %s 
                            THEN driver_id 
                        END) as novos_cadastrados
                    FROM driver_personal_details
                    WHERE city IS NOT NULL 
                        AND city != ''
                    GROUP BY city
                )
                SELECT * FROM city_registrations
                WHERE total_cadastrados > 0
                ORDER BY total_cadastrados DESC;
            """
            cursor.execute(cadastrados_query, (start_date,))
        else:
            cadastrados_query = """
                SELECT 
                    city,
                    COUNT(DISTINCT driver_id) as total_cadastrados,
                    COUNT(DISTINCT driver_id) as novos_cadastrados
                FROM driver_personal_details
                WHERE city IS NOT NULL 
                    AND city != ''
                GROUP BY city
                ORDER BY total_cadastrados DESC;
            """
            cursor.execute(cadastrados_query)
        
        cadastrados_data = {row[0]: {"total_cadastrados": row[1], "novos_cadastrados": row[2]} for row in cursor.fetchall()}
        
        # Query para motoristas ativos por cidade (com rides_history)
        ativos_query = """
            SELECT 
                city,
                COUNT(DISTINCT driver_id) as total_ativos
            FROM driver_personal_details
            WHERE city IS NOT NULL 
                AND city != ''
                AND jsonb_array_length(rides_history) > 0
            GROUP BY city
            ORDER BY total_ativos DESC;
        """
        cursor.execute(ativos_query)
        ativos_data = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Combinar dados
        all_cities = set(list(cadastrados_data.keys()) + list(ativos_data.keys()))
        
        data = []
        for cidade in all_cities:
            cadastrados_info = cadastrados_data.get(cidade, {"total_cadastrados": 0, "novos_cadastrados": 0})
            ativos = ativos_data.get(cidade, 0)
            
            total_cadastrados = cadastrados_info["total_cadastrados"]
            taxa_ativacao = round((ativos / total_cadastrados * 100), 1) if total_cadastrados > 0 else 0
            
            data.append({
                "cidade": cidade,
                "total_cadastrados": total_cadastrados,
                "novos_cadastrados": cadastrados_info["novos_cadastrados"],
                "total_ativos": ativos,
                "taxa_ativacao": taxa_ativacao
            })
        
        # Ordenar por total de cadastrados
        data.sort(key=lambda x: x["total_cadastrados"], reverse=True)
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "data": data,
            "total_cidades": len(data)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# 9. INACTIVE DRIVERS BY CITY
# ===================================================================
@router.get("/drivers/analytics/inactive-by-city")
def get_inactive_by_city(
    period: str = Query(None, description="Período: hoje, 7_days, 30_days, 3_months, 6_months, 12_months")
):
    """
    Retorna motoristas inativos por cidade
    Compara total cadastrados vs inativos vs recém inativos no período
    Inativo = cadastrado mas sem corridas no rides_history
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        start_date = get_period_date_filter(period)
        
        # Query para motoristas por cidade
        if start_date:
            query = """
                WITH city_stats AS (
                    SELECT 
                        city,
                        COUNT(DISTINCT driver_id) as total_cadastrados,
                        COUNT(DISTINCT CASE 
                            WHEN jsonb_array_length(rides_history) = 0 
                            THEN driver_id 
                        END) as total_inativos,
                        COUNT(DISTINCT CASE 
                            WHEN jsonb_array_length(rides_history) = 0
                                AND personal_data->>'joining_date' IS NOT NULL 
                                AND personal_data->>'joining_date' ~ '^\d{2}/\d{2}/\d{4}$'
                                AND TO_DATE(personal_data->>'joining_date', 'DD/MM/YYYY') >= %s
                            THEN driver_id 
                        END) as novos_inativos,
                        COUNT(DISTINCT CASE 
                            WHEN jsonb_array_length(rides_history) > 0 
                            THEN driver_id 
                        END) as total_ativos
                    FROM driver_personal_details
                    WHERE city IS NOT NULL 
                        AND city != ''
                    GROUP BY city
                )
                SELECT 
                    city,
                    total_cadastrados,
                    total_inativos,
                    novos_inativos,
                    total_ativos,
                    ROUND((total_inativos::DECIMAL / NULLIF(total_cadastrados, 0) * 100), 1) as taxa_inatividade
                FROM city_stats
                WHERE total_inativos > 0
                ORDER BY total_inativos DESC;
            """
            cursor.execute(query, (start_date,))
        else:
            query = """
                WITH city_stats AS (
                    SELECT 
                        city,
                        COUNT(DISTINCT driver_id) as total_cadastrados,
                        COUNT(DISTINCT CASE 
                            WHEN jsonb_array_length(rides_history) = 0 
                            THEN driver_id 
                        END) as total_inativos,
                        COUNT(DISTINCT CASE 
                            WHEN jsonb_array_length(rides_history) = 0 
                            THEN driver_id 
                        END) as novos_inativos,
                        COUNT(DISTINCT CASE 
                            WHEN jsonb_array_length(rides_history) > 0 
                            THEN driver_id 
                        END) as total_ativos
                    FROM driver_personal_details
                    WHERE city IS NOT NULL 
                        AND city != ''
                    GROUP BY city
                )
                SELECT 
                    city,
                    total_cadastrados,
                    total_inativos,
                    novos_inativos,
                    total_ativos,
                    ROUND((total_inativos::DECIMAL / NULLIF(total_cadastrados, 0) * 100), 1) as taxa_inatividade
                FROM city_stats
                WHERE total_inativos > 0
                ORDER BY total_inativos DESC;
            """
            cursor.execute(query)
        
        result = cursor.fetchall()
        
        data = [
            {
                "cidade": row[0],
                "total_cadastrados": row[1],
                "total_inativos": row[2],
                "novos_inativos": row[3],
                "total_ativos": row[4],
                "taxa_inatividade": float(row[5]) if row[5] else 0
            }
            for row in result
        ]
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "data": data,
            "total_cidades": len(data)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
