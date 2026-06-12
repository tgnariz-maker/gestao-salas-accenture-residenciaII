import logging
from celery import shared_task
from django.core.cache import cache

logger = logging.getLogger('workspace')

LAYOUT_CACHE_PREFIX = 'layout_preview'
LAYOUT_CACHE_TTL = 3600


@shared_task(bind=True, max_retries=3)
def processar_planta_baixa_task(self, imagem_bytes_hex, sala_id):
    from workspace.services import processar_planta_baixa
    from workspace.serializers import PostoDeTrabalhoSerializer

    cache_key = f'{LAYOUT_CACHE_PREFIX}:{sala_id}'

    try:
        cache.set(cache_key, {'status': 'processing'}, LAYOUT_CACHE_TTL)

        imagem_bytes = bytes.fromhex(imagem_bytes_hex)
        resultado = processar_planta_baixa(imagem_bytes, sala_id)

        serializer = PostoDeTrabalhoSerializer(resultado['postos_criados'], many=True)

        payload = {
            'status': 'completed',
            'postos': serializer.data,
            'total_detectado': resultado['total_detectado'],
            'confianca_media': resultado['confianca_media'],
            'alerta_revisao': resultado['alerta_revisao'],
        }

        cache.set(cache_key, payload, LAYOUT_CACHE_TTL)
        logger.info('Task concluída para sala %s: %d postos', sala_id, resultado['total_detectado'])

    except Exception as exc:
        cache.set(cache_key, {'status': 'failed', 'erro': str(exc)}, LAYOUT_CACHE_TTL)
        logger.error('Falha na task de mapeamento para sala %s: %s', sala_id, exc)
        raise self.retry(exc=exc, countdown=10)