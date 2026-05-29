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
                'MIICmzCCAYMCBgGecZwcBDANBgkqhkiG9w0BAQsFADARMQ8wDQYDVQQDDAZncm93'
                'dXAwHhcNMjYwNTI5MDI0MDE2WhcNMzYwNTI5MDI0MTU2WjARMQ8wDQYDVQQDDAZn'
                'cm93dXAwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC0OxtWIyDra+IW'
                'p9p9O/aWhr8gv2InrEaR4hw2iDlwe67+zku1sUnCYFTyCyNvf/gvC9hN5U1H15CN'
                'xM9N05OgFiTiU08fvosqDYKa3JLjseHzg/JUtHxM9I1T5QiUnLjK/yXPirgUxTE'
                'gRXPvLP2MMygawgoAFuBd0ZVP4cj9SIvyz4+XWN83Alczn8dvcIDPfa9I+5jzdhG'
                'BZHTehvZnDmMVXxwPbJtGjvNjtfCCA0wzcIIzHte44IClhxlFIy2jPmG+58tchZ3'
                'yqeQExdIzI5d+JY933jO1B8iL9o2Qczb1TmEh/bFiND9D3pj9NzThG8D4SqBpP3'
                'jr/KrKyIHJAgMBAAEwDQYJKoZIhvcNAQELBQADggEBAElk0oyf6Cbop3ybidGodj'
                '0MhTjurhpsuY4I6Ln/ffJvvPYZluEKn/VQGZMKP3c67K6vLXyA+rXMBkuD8M2IG'
                'eUeKbHN8Rmrn4IkuKdkrchPFuL1ZJIjQobqkX6Ie+CUZGgIB1zhG2yHS+wmDMFw'
                'DC5o5Ijd8edterkS+numyymfi3WDZtbkUBasOt3nguxZwp5Q5r9VoglLe0FsWJAR/'
                'I9cox0UhjhKFapixEYVzw4gosnnF3+HXKZ6pA8JAgPUNiVku8ft8cCHBER8NSPiY'
                'E4vLMd/iUztM05iNN9MdUKNA+/BGY2pQ+V8+D4KonLkwI1bh0WXIhrVPlQ9ATCb'
                '65k='
            ),
        },
    }