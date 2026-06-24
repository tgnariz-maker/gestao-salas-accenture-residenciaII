import logging
import requests
from django.http import HttpResponseRedirect, HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from django.conf import settings

from .models import Usuario, PerfilProfissional
from .saml_utils import preparar_request_saml, carregar_configuracao_saml

logger = logging.getLogger('workspace')


def _obter_token_keycloak(username):
    token_url = f'{settings.KEYCLOAK_INTERNAL_URL}/protocol/openid-connect/token'

    response = requests.post(
        token_url,
        data={
            'client_id': settings.KEYCLOAK_OIDC_CLIENT_ID,
            'client_secret': settings.KEYCLOAK_OIDC_CLIENT_SECRET,
            'grant_type': 'password',
            'username': username,
            'password': settings.KEYCLOAK_USERS_PASSWORD,
            'scope': 'openid profile email',
        },
        timeout=10,
    )

    if response.status_code != 200:
        logger.error(
            'Falha ao obter token para "%s": %s — %s',
            username,
            response.status_code,
            response.text,
        )
        return None

    return response.json()


class SAMLLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        req = preparar_request_saml(request)
        config = carregar_configuracao_saml()
        auth = OneLogin_Saml2_Auth(req, config)
        login_url = auth.login()
        return HttpResponseRedirect(login_url)


class SAMLACSView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        req = preparar_request_saml(request)
        config = carregar_configuracao_saml()
        auth = OneLogin_Saml2_Auth(req, config)
        auth.process_response()

        erros = auth.get_errors()
        if erros:
            logger.error('Erro SAML: %s — %s', erros, auth.get_last_error_reason())
            return HttpResponse('Erro na autenticação SAML.', status=400)

        if not auth.is_authenticated():
            return HttpResponse('Autenticação SAML falhou.', status=401)

        username = auth.get_nameid()
        atributos = auth.get_attributes()

        usuario, _ = Usuario.objects.get_or_create(
            username=username,
            defaults={'email': username},
        )

        if not usuario.perfil_profissional:
            job_title = None
            for chave in ['job_title', 'jobTitle', 'cargo', 'position']:
                valores = atributos.get(chave, [])
                if valores:
                    job_title = valores[0]
                    break

            if job_title:
                try:
                    perfil = PerfilProfissional.objects.get(nome__iexact=job_title)
                    usuario.perfil_profissional = perfil
                    usuario.save(update_fields=['perfil_profissional'])
                    logger.info('Perfil "%s" vinculado ao usuário "%s"', perfil.nome, username)
                except PerfilProfissional.DoesNotExist:
                    logger.warning(
                        'Perfil "%s" não encontrado para o usuário "%s". Vincule manualmente.',
                        job_title, username,
                    )

        token_data = _obter_token_keycloak(username)

        if not token_data:
            logger.error('Não foi possível emitir token para "%s".', username)
            return Response(
                {'erro': 'Login SAML realizado, mas falha ao emitir token de acesso.'},
                status=502,
            )

        logger.info('Login SAML concluído para "%s"', username)
        frontend_url = f'{settings.FRONTEND_URL}?token={token_data.get("access_token")}'
        return HttpResponseRedirect(frontend_url)