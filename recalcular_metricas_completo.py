#!/usr/bin/env python3
from backend import create_app
from backend.services.sync_service import DataSyncService
from backend.models import MetricaDiaria
from datetime import datetime

app = create_app()
with app.app_context():
    print('🔄 Recalculando métricas diárias para TODOS os dados...')
    sync_service = DataSyncService()
    
    # Forçar recálculo a partir de janeiro 2025 (data dos dados importados)
    start_date = datetime(2025, 1, 1)
    sync_service.recalculate_daily_metrics(start_date)
    print('✅ Métricas recalculadas!')
    
    # Verificar métricas
    metricas = MetricaDiaria.query.order_by(MetricaDiaria.data.desc()).limit(10).all()
    print(f'\n📊 Métricas geradas: {len(metricas)}')
    for m in metricas:
        receita = m.receita_total or 0
        print(f'  📅 {m.data} - 🏙️ {m.municipio} - 🚗 {m.total_corridas} corridas - 💰 R$ {receita:.2f}')
