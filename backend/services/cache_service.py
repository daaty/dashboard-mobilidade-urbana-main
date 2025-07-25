#!/usr/bin/env python3
"""
Serviço de Cache Redis - Performance Otimizada
Implementa cache inteligente para dados frequentes do dashboard
"""

import redis
import json
import os
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
import hashlib

class CacheService:
    """Serviço de cache Redis para otimização de performance"""
    
    def __init__(self):
        """Inicializa conexão com Redis"""
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Testar conexão
            self.redis_client.ping()
            print("✅ Cache Redis conectado com sucesso")
        except Exception as e:
            print(f"Redis não disponível, usando cache em memória: {e}")
            self.redis_client = None
            self._memory_cache = {}
    
    def _get_cache_key(self, prefix: str, params: Dict[str, Any]) -> str:
        """Gera chave única de cache baseada nos parâmetros"""
        params_str = json.dumps(params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        return f"dashboard:{prefix}:{params_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Recupera valor do cache"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                # Fallback para cache em memória
                cache_item = self._memory_cache.get(key)
                if cache_item and cache_item['expires'] > datetime.now():
                    return cache_item['data']
                elif cache_item:
                    del self._memory_cache[key]
            return None
        except Exception as e:
            print(f"Erro ao recuperar cache {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Armazena valor no cache com TTL (Time To Live)"""
        try:
            if self.redis_client:
                return self.redis_client.setex(
                    key, 
                    ttl, 
                    json.dumps(value, default=str)
                )
            else:
                # Fallback para cache em memória
                self._memory_cache[key] = {
                    'data': value,
                    'expires': datetime.now() + timedelta(seconds=ttl)
                }
                return True
        except Exception as e:
            print(f"Erro ao armazenar cache {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                if key in self._memory_cache:
                    del self._memory_cache[key]
                    return True
            return False
        except Exception as e:
            print(f"Erro ao deletar cache {key}: {e}")
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalida múltiplas chaves por padrão"""
        try:
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
            else:
                # Fallback para cache em memória
                keys_to_delete = [k for k in self._memory_cache.keys() if pattern.replace('*', '') in k]
                for key in keys_to_delete:
                    del self._memory_cache[key]
                return len(keys_to_delete)
            return 0
        except Exception as e:
            print(f"Erro ao invalidar padrão {pattern}: {e}")
            return 0
    
    # Métodos específicos para o dashboard
    
    def get_dashboard_overview(self, params: Dict[str, Any]) -> Optional[Dict]:
        """Cache para overview do dashboard"""
        key = self._get_cache_key("overview", params)
        return self.get(key)
    
    def set_dashboard_overview(self, params: Dict[str, Any], data: Dict, ttl: int = 300) -> bool:
        """Armazena overview no cache (5 minutos padrão)"""
        key = self._get_cache_key("overview", params)
        return self.set(key, data, ttl)
    
    def get_metricas_diarias(self, params: Dict[str, Any]) -> Optional[Dict]:
        """Cache para métricas diárias"""
        key = self._get_cache_key("metricas", params)
        return self.get(key)
    
    def set_metricas_diarias(self, params: Dict[str, Any], data: Dict, ttl: int = 600) -> bool:
        """Armazena métricas no cache (10 minutos padrão)"""
        key = self._get_cache_key("metricas", params)
        return self.set(key, data, ttl)
    
    def get_municipios(self) -> Optional[list]:
        """Cache para lista de municípios"""
        return self.get("dashboard:municipios")
    
    def set_municipios(self, data: list, ttl: int = 3600) -> bool:
        """Armazena municípios no cache (1 hora)"""
        return self.set("dashboard:municipios", data, ttl)
    
    def invalidate_dashboard_cache(self) -> int:
        """Invalida todo cache do dashboard"""
        return self.invalidate_pattern("dashboard:*")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Estatísticas do cache"""
        try:
            if self.redis_client:
                info = self.redis_client.info()
                return {
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory': info.get('used_memory_human', '0B'),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                    'hit_rate': self._calculate_hit_rate(info)
                }
            else:
                return {
                    'cache_type': 'memory',
                    'cached_keys': len(self._memory_cache),
                    'memory_usage': 'N/A'
                }
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """Calcula taxa de acerto do cache"""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        return round((hits / total * 100) if total > 0 else 0, 2)

# Instância global do cache
cache_service = CacheService()
