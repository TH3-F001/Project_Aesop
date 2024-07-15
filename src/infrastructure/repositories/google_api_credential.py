from typing import List
from src.domain.interfaces.i_uri_validator import IUriValidator


class GoogleApiCredential:
    def __init__(self, client_id: str, client_secret: str, auth_uri: str, token_uri: str, validator: IUriValidator, redirect_uris: List[str] = None):
        self._validator = validator
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uris = redirect_uris if redirect_uris is not None else []
        self.auth_uri = auth_uri
        self.token_uri = token_uri


    # Client ID
    @property
    def client_id(self) -> str:
        """Getter for client_id"""
        return self._client_id

    @client_id.setter
    def client_id(self, value: str):
        """Setter for client_id"""
        self._client_id = value

    # Client Secret
    @property
    def client_secret(self) -> str:
        """Getter for client_secret"""
        return self._client_secret

    @client_secret.setter
    def client_secret(self, value: str):
        """Setter for client_secret"""
        self._client_secret = value

    # Redirect URIs
    @property
    def redirect_uris(self) -> List[str]:
        """Getter for redirect_uris"""
        return self._redirect_uris

    @redirect_uris.setter
    def redirect_uris(self, uris: List[str]):
        """Setter for redirect_uris"""
        if not isinstance(uris, list):
            raise ValueError('redirect_uris must be a list.')

        for uri in uris:
            if not self._validator.validate(uri):
                raise ValueError(f'Redirect URI is not a valid URI: {uri}')

        self._redirect_uris = uris

    # Auth URI
    @property
    def auth_uri(self) -> str:
        """Getter for auth_uri"""
        return self._auth_uri

    @auth_uri.setter
    def auth_uri(self, uri):
        """Setter for auth_uri"""
        if not self._validator.validate(uri):
            raise ValueError(f'Auth URI is not a valid URI: {uri}')
        self._auth_uri = uri

    # Token URI
    @property
    def token_uri(self) -> str:
        """Getter for token_uri"""
        return self._token_uri

    @token_uri.setter
    def token_uri(self, uri):
        """setter for token_uri"""
        if not self._validator.validate(uri):
            raise ValueError(f'Auth URI is not a valid URI: {uri}')
        self._token_uri = uri
