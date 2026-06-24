from django.conf import settings


def preparar_request_saml(request):
    return {
        'https': 'on' if request.is_secure() else 'off',
        'http_host': request.META.get('HTTP_HOST', 'localhost:8000'),
        'script_name': request.META.get('PATH_INFO', ''),
        'get_data': request.GET.copy(),
        'post_data': request.POST.copy(),
    }


def carregar_configuracao_saml():
    return {
        'strict': not settings.DEBUG,
        'debug': settings.DEBUG,
        'sp': {
            'entityId': str(settings.SAML_ENTITY_ID),
            'assertionConsumerService': {
                'url': str(settings.SAML_ACS_URL),
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
            },
            'NameIDFormat': 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress',
        },
        'idp': {
            'entityId': f'{settings.SAML_IDP_URL}',
            'singleSignOnService': {
                'url': f'{settings.SAML_IDP_URL}/protocol/saml',
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
            },
            'singleLogoutService': {
                'url': f'{settings.SAML_IDP_URL}/protocol/saml',
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
            },
            'x509cert': settings.SAML_X509_CERT,
        },
    }