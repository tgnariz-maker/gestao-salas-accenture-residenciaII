import logging
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import login
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from onelogin.saml2.auth import OneLogin_Saml2_Auth

from .models import Usuario
from .saml_utils import preparar_request_saml, carregar_configuracao_saml

logger = logging.getLogger('workspace')


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

        usuario, _ = Usuario.objects.get_or_create(
            username=username,
            defaults={'email': username},
        )

        login(request, usuario, backend='django.contrib.auth.backends.ModelBackend')

        request.session['saml_authenticated'] = True
        request.session['saml_username'] = username

        return Response({'mensagem': 'Login realizado com sucesso.', 'usuario': username})