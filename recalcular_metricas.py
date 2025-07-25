#!/usr/bin/env python3
from backend import create_app
from backend.services.sync_service import DataSyncService
from backend.models import MetricaDiaria

app = create_app()
with app.app_context():
    print('🔄 Recalculando métricas diárias...')
    sync_service = DataSyncService()
    sync_service.recalculate_daily_metrics()
    print('✅ Métricas recalculadas!')
    
    # Verificar métricas
    metricas = MetricaDiaria.query.order_by(MetricaDiaria.data.desc()).limit(5).all()
    print(f'\n📊 Métricas geradas: {len(metricas)}')
    for m in metricas:
        receita = m.receita_total or 0
        print(f'  📅 {m.data} - 🏙️ {m.municipio} - 🚗 {m.total_corridas} corridas - 💰 R$ {receita:.2f}')
