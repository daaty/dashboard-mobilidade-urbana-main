"""
Script para reescrever o arquivo drivers_analytics.py com psycopg2
"""

NEW_CONTENT = '''"""
API endpoints para analytics e gráficos da aba de Motoristas
Baseado nos 5 tipos de dados: Active Drivers, Driver Performance, Drivers Enrollment, Leaderboard, Deactive Drivers
"""

from fastapi import APIRouter, HTTPException
import psycopg2
from datetime import datetime, timedelta
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


# ===================================================================
# 1. DISTRIBUIÇÃO POR CIDADE (Active Drivers)
# ===================================================================
@router.get("/analytics/by-city")
def get_drivers_by_city():
    """
    Retorna distribuição de motoristas ativos por cidade
    Fonte: Active Drivers -> additional_data->>'City'
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                additional_data->>'City' as cidade,
                COUNT(DISTINCT driver_id) as total_motoristas,
                COUNT(*) as total_registros
            FROM drivers_data
            WHERE additional_data->>'City' IS NOT NULL
                AND additional_data->>'City' != ''
                AND data_type = 'active'
            GROUP BY additional_data->>'City'
            ORDER BY total_motoristas DESC;
        """
        
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
@router.get("/analytics/top-performers")
def get_top_performers(limit: int = 10):
    """
    Retorna os top motoristas por corridas realizadas (Success Rides)
    Fonte: Driver Performance -> additional_data->>'Success Rides'
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                name,
                driver_id,
                additional_data->>'Success Rides' as success_rides,
                additional_data->>'Online Hours' as online_hours,
                additional_data->>'Rejected Rides' as rejected_rides,
                additional_data->>'Missed Rides' as missed_rides,
                additional_data->>'Phone Number' as phone
            FROM drivers_data
            WHERE data_type = 'performance'
                AND additional_data->>'Success Rides' IS NOT NULL
                AND additional_data->>'Success Rides' != ''
            ORDER BY CAST(additional_data->>'Success Rides' AS INTEGER) DESC
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
@router.get("/analytics/ratings-distribution")
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
@router.get("/analytics/recent-enrollments")
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
@router.get("/analytics/performance-metrics")
def get_performance_metrics():
    """
    Retorna métricas agregadas de performance dos motoristas
    Fonte: Driver Performance -> várias métricas
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                SUM(CAST(additional_data->>'Success Rides' AS INTEGER)) as total_success_rides,
                SUM(CAST(additional_data->>'Rejected Rides' AS INTEGER)) as total_rejected_rides,
                SUM(CAST(additional_data->>'Missed Rides' AS INTEGER)) as total_missed_rides,
                SUM(CAST(additional_data->>'User Cancelled Rides' AS INTEGER)) as total_user_cancelled,
                SUM(CAST(additional_data->>'Driver Cancelled Rides' AS INTEGER)) as total_driver_cancelled,
                SUM(CAST(additional_data->>'Online Hours' AS FLOAT)) as total_online_hours,
                AVG(CAST(additional_data->>'Online Hours' AS FLOAT)) as avg_online_hours,
                COUNT(DISTINCT driver_id) as total_drivers
            FROM drivers_data
            WHERE data_type = 'performance'
                AND additional_data->>'Success Rides' IS NOT NULL;
        """
        
        cursor.execute(query)
        result = cursor.fetchone()
        
        # Distribuição de horas online
        hours_dist_query = """
            SELECT 
                CASE 
                    WHEN CAST(additional_data->>'Online Hours' AS FLOAT) >= 8 THEN '8+ horas'
                    WHEN CAST(additional_data->>'Online Hours' AS FLOAT) >= 6 THEN '6-8 horas'
                    WHEN CAST(additional_data->>'Online Hours' AS FLOAT) >= 4 THEN '4-6 horas'
                    WHEN CAST(additional_data->>'Online Hours' AS FLOAT) >= 2 THEN '2-4 horas'
                    ELSE '< 2 horas'
                END as faixa_horas,
                COUNT(*) as quantidade
            FROM drivers_data
            WHERE data_type = 'performance'
                AND additional_data->>'Online Hours' IS NOT NULL
                AND additional_data->>'Online Hours' != ''
            GROUP BY faixa_horas
            ORDER BY faixa_horas DESC;
        """
        
        cursor.execute(hours_dist_query)
        hours_dist = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "data": {
                "summary": {
                    "total_success_rides": int(result[0]) if result[0] else 0,
                    "total_rejected_rides": int(result[1]) if result[1] else 0,
                    "total_missed_rides": int(result[2]) if result[2] else 0,
                    "total_user_cancelled": int(result[3]) if result[3] else 0,
                    "total_driver_cancelled": int(result[4]) if result[4] else 0,
                    "total_online_hours": round(float(result[5]), 2) if result[5] else 0,
                    "avg_online_hours": round(float(result[6]), 2) if result[6] else 0,
                    "total_drivers": result[7]
                },
                "online_hours_distribution": [
                    {
                        "faixa": row[0],
                        "quantidade": row[1]
                    }
                    for row in hours_dist
                ]
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================================
# 6. ATIVIDADE ONLINE (Active Drivers - Last Login)
# ===================================================================
@router.get("/analytics/online-activity")
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
@router.get("/analytics/activity-comparison")
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
'''

# Escrever o arquivo
arquivo = r"c:\Users\arcti\OneDrive\Área de Trabalho\GAYBERT\dashboard-mobilidade-urbana-main-dashboard-executivo-styling\dashboard-mobilidade-urbana-main-dashboard-executivo-styling\backend\app\api\drivers_analytics.py"

with open(arquivo, 'w', encoding='utf-8') as f:
    f.write(NEW_CONTENT)

print("✅ Arquivo reescrito com sucesso!")
print("🔧 Todos os 7 endpoints agora usam psycopg2 síncrono")
