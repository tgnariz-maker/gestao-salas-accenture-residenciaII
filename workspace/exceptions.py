from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('workspace')


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            'erro': _formatar_erros(response.data),
            'status': response.status_code,
        }
        return response

    logger.error('Erro não tratado: %s', exc, exc_info=True)
    return Response(
        {'erro': 'Erro interno do servidor.', 'status': 500},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def _formatar_erros(data):
    if isinstance(data, list):
        return data[0] if len(data) == 1 else data

    if isinstance(data, dict):
        erros = {}
        for campo, mensagens in data.items():
            if campo == 'detail':
                return mensagens if isinstance(mensagens, str) else str(mensagens)
            erros[campo] = mensagens[0] if isinstance(mensagens, list) and len(mensagens) == 1 else mensagens
        return erros

    return str(data)