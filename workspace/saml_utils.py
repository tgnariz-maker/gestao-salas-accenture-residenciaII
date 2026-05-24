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
        'strict': False,
        'debug': True,
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
            'x509cert': (
                'MIICmzCCAYMCBgGeUizr8zANBgkqhkiG9w0BAQsFADARMQ8wDQYDVQQDDAZncm93'
                'dXAwHhcNMjYwNTIzMDAxMDM2WhcNMzYwNTIzMDAxMjE2WjARMQ8wDQYDVQQDDAZn'
                'cm93dXAwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDENPiGLRmnocTO'
                'dUjUDLshPnd/0tHDidoFZPoYn6DFnE1edikZrUcmla1K0QpZHQvfMt0JA+D6A2VR'
                'VUpOcGkcFXB1Bm1CnU4AhbpK8vhPYFinbh0lCuPWVFRPXAI43vdOUDJGpQ4tRc/X'
                'lfiXPHKdSw1RSeWf0+qgLHXjE4nfJFtbc6wJqgxzz/sSD2Ld9ZdGROSwImpwlKs0'
                'QSlppIM4t7Mt8Hucz2XF7YFdUp12TXxSxe1H4epcMTMJxnKkALNegx9A7N8+rSbN'
                'zyDaZUT6hmnU2bQwHjlVvGEE3nQmoLIB3p3hUXDTDClf/7+p8L4Rx/Ws7VQIb8F9'
                'fS7U/8VzAgMBAAEwDQYJKoZIhvcNAQELBQADggEBAE9Yo7ItAjy7PkLQVWPc2/Rp'
                'ZP4JcHj84h8BCr6RP3BRC6XC6b4uaBbE+ZNgLwDG6acN1e8K1qyoenbkXtCIGmZA'
                'mMcUPsQcU+tJwe2vxpqyhe7rbAbeya8nIUmI0oVLQvuTZc9D8+IRSljqLbWzGf6J'
                '0tIegeM/tIlTuQnZPlJvDGZZJGgEmV9Vl+iPiIiq18YtCzQpxcBByXpiU+2nohUJ'
                'e56JHwVBie9UinuYT87OLgcb2cY6ibTnn+Wn3AOUTZs2jkFvStYN9AJIsXxfUhct'
                '3GzL7HcV5dTukKNKCZr6U9QFhD2NAx5zj+rFX3/gLxOh3hS27lpugdpKIn1GWJA='
            ),
        },
    }