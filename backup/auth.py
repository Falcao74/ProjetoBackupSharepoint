import msal

# Comentários em Português do Brasil
# Este módulo lida com autenticação no Microsoft Graph usando MSAL.


def obter_token(tenant_id: str, client_id: str, client_secret: str) -> str:
    """Obtém um token de acesso do Microsoft Graph via fluxo de aplicativo confidencial.

    Utiliza o escopo '.default' que corresponde às permissões concedidas ao app.
    """
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = msal.ConfidentialClientApplication(
        client_id=client_id,
        authority=authority,
        client_credential=client_secret,
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" not in result:
        raise RuntimeError(f"Falha ao obter token: {result}")
    return result["access_token"]