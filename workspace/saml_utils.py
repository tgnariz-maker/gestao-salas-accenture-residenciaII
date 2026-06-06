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
                'MIICmzCCAYMCBgGemgPwSTANBgkqhkiG9w0BAQsFADARMQ8wDQYDVQQDDAZncm93'
                'dXAwHhcNMjYwNjA1MjI1ODI5WhcNMzYwNjA1MjMwMDA5WjARMQ8wDQYDVQQDDAZn'
                'cm93dXAwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCvhG6KHNJyLmyd'
                '4uDcANvoLG1mpNjk/k9FDLm6djYORKmJnl/I/v/UkR8AtaPM3RTJvk8A971VXD8'
                'cGMUs/w+eUHcKBDvCksSSGt+NkC4y9iNjEX5Z3k+KSX+P6PAf6zpZCMqhk7IVbq'
                'S90TYCAU1g8xkKcYQh9CPf4bsRJlpTPVKL+7JAOlFeOgh5Ug5SREWFsjdEgfJxxt'
                'q6QVAD27pOXk22HGvxLmEYuieOr4CcYcM1SW6YiVyiclg9+Pe1htHFrobfI1J3sI'
                '5v6HLROd5YBw/U4k0Evo4YA30bN3aIlYjH7LpRxYj13/N6mJyvdCq27/xjd0WY8'
                '3/e1DYqnebxAgMBAAEwDQYJKoZIhvcNAQELBQADggEBAGyn2M17kQHpsSlK/WPIo'
                'uGVuob88lYkfrNrVjxlmxDcCD1QfyOXf4hZCHllPHy6dXdo7TO5WUafHFoakJHL+'
                'yM9sfK0XJVcmoXuGyWRzxc5MTY1MKgE3PX93mUNTvkxSrk0c31dsTE3lgk6hP+pU'
                'AlMc2sLKwIibgf+4ZqEExibJVpdB5KMlkls6GthTBNNnPa3/Y3eIfD/91tmXvOXv'
                'onSoELvUCzlOFT2R+9OQA4NQ/4FM+t/Pwyd1i44F70zHM+t/KGFGwZm5RaFJA48'
                'Ik/kWppVQrxLTx2ePmJp9lKje7Bm9GqldutzWIVlRq8fxftjGpoIT+4ERaPrAKBQlRM='
            ),
        },
    }