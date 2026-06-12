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
                'MIICmzCCAYMCBgGeuXjnhTANBgkqhkiG9w0BAQsFADARMQ8wDQYDVQQDDAZncm93'
                'dXAwHhcNMjYwNjEyMDEzNDI5WhcNMzYwNjEyMDEzNjA5WjARMQ8wDQYDVQQDDAZn'
                'cm93dXAwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCkaM6epl40y5FA'
                'MqcnYlh1n4SvnEmTCshyyjj+J1Ck4XMq8X10gq1Q4B/BAB1IKn+/fKSak6Z6ZGp'
                'DNzzpSS5TXSBkrloy6LtczxUgn2MPe8yAkDJBuUvu7MxzBAVkI6m4MjEJN3V/a6'
                'mN6AL0qwb9t8CTpF9q7B1R6Tq95qWds4lucQYQWWk1vfKZVuMh6IaDkwcgpG8li'
                'ORG2wCdHdnm3zggBs+0A+1qG2Xt0ey3R/+Q7U8YeHzkxNov/1V1JtvzT5kKTsQ'
                'Dg9rALjTopvhFPpKgsMGBOeY/bxsrWUGkVn/XlkSF1k1cs6xC6Di95cvklODVPW'
                'vWcTUg+n6ie2MjAgMBAAEwDQYJKoZIhvcNAQELBQADggEBAKQ4Hdf/w8gEntgqX'
                'q7hwEwUuc+aWkcrR9ex67b8ddPXgu1bPK8PbQQb1fOgfVu8s01jRFEw08GYhAxW'
                'IRvC3nd2Ce3sz57Cu7wzsSm25OCqvQB9LXjTf9Ohi7wFtNykOyLYr2xUZZPVc7R'
                'yiwLDu2wvl+5n4uYKtjwgkkvMJzUC7XJXFaWuKQ2DRwNKoJWjdSTztzJJrs4PX'
                '7wRjGIKf1+qrZbbo7ICUaJGjd7kKxfrVf9E3P8qphCk6UoO6si1ErUHr81KK4x'
                'KKiIKX3I7B5cJ1FA2cfWDIvmSGF3vNezXwNzrGpxbPfx/Dx6VPpsDcIyuGidb6'
                'G9sSQmSp2H7ckA='
            ),
        },
    }