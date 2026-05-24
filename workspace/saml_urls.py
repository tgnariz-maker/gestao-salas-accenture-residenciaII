from django.urls import path
from .saml_views import SAMLLoginView, SAMLACSView

urlpatterns = [
    path('login/', SAMLLoginView.as_view(), name='saml-login'),
    path('acs/', SAMLACSView.as_view(), name='saml-acs'),
]