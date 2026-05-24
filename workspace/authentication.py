from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Usuario


class SAMLSessionAuthentication(BaseAuthentication):
    """
    Autentica o usuário via sessão Django criada após o fluxo SAML.
    Após o ACS validar a resposta do Keycloak, o usuário é salvo na sessão.
    Todas as requisições subsequentes usam essa sessão para identificar o usuário.
    """

    def authenticate(self, request):
        if not request.session.get('saml_authenticated'):
            return None

        username = request.session.get('saml_username')
        if not username:
            return None

        try:
            usuario = Usuario.objects.get(username=username)
        except Usuario.DoesNotExist:
            raise AuthenticationFailed('Usuário não encontrado.')

        return (usuario, None)