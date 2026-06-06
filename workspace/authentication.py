import logging
import jwt
import requests
from jwt.algorithms import RSAAlgorithm
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.core.cache import cache
from .models import Usuario

logger = logging.getLogger('workspace')

JWKS_CACHE_KEY = 'keycloak_jwks'
JWKS_CACHE_TTL = 3600


def _obter_jwks():
    jwks = cache.get(JWKS_CACHE_KEY)
    if jwks:
        return jwks

    try:
        response = requests.get(settings.KEYCLOAK_JWKS_URL_INTERNAL, timeout=5)
        response.raise_for_status()
        jwks = response.json()
        cache.set(JWKS_CACHE_KEY, jwks, JWKS_CACHE_TTL)
        return jwks
    except requests.RequestException as exc:
        logger.error('Falha ao buscar JWKS do Keycloak: %s', exc)
        raise AuthenticationFailed('Serviço de autenticação indisponível.')


def _obter_chave_publica(token):
    header = jwt.get_unverified_header(token)
    kid = header.get('kid')

    jwks = _obter_jwks()
    for chave in jwks.get('keys', []):
        if chave.get('kid') == kid:
            return RSAAlgorithm.from_jwk(chave)

    cache.delete(JWKS_CACHE_KEY)
    jwks = _obter_jwks()
    for chave in jwks.get('keys', []):
        if chave.get('kid') == kid:
            return RSAAlgorithm.from_jwk(chave)

    raise AuthenticationFailed('Chave de assinatura não encontrada.')


class KeycloakBearerAuthentication(BaseAuthentication):

    def authenticate(self, request):
        header = request.META.get('HTTP_AUTHORIZATION', '')
        if not header.startswith('Bearer '):
            return None

        token = header.split(' ', 1)[1].strip()
        if not token:
            return None

        return self._validar_token(token)

    def _validar_token(self, token):
        try:
            chave_publica = _obter_chave_publica(token)
            payload = jwt.decode(
                token,
                chave_publica,
                algorithms=['RS256'],
                options={'verify_aud': False},
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expirado.')
        except jwt.InvalidTokenError as exc:
            logger.warning('Token inválido: %s', exc)
            raise AuthenticationFailed('Token inválido.')

        preferred_username = payload.get('preferred_username')
        email = payload.get('email')

        if not preferred_username and not email:
            raise AuthenticationFailed('Token sem identificação de usuário.')

        usuario = None
        for campo in [preferred_username, email]:
            if not campo:
                continue
            try:
                usuario = Usuario.objects.select_related('perfil_profissional').get(username=campo)
                break
            except Usuario.DoesNotExist:
                continue

        if not usuario:
            raise AuthenticationFailed('Usuário não encontrado.')

        return (usuario, token)

    def authenticate_header(self, request):
        return 'Bearer realm="growup"'