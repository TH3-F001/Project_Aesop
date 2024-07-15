from src.domain.interfaces.i_uri_validator import IUriValidator
from urllib.parse import urlparse
import re


class UrlParseUriValidator(IUriValidator):
    @staticmethod
    def validate(value: str) -> bool:
        try:
            result = urlparse(value)

            if not all([result.scheme, result.netloc]):
                return False

            # Ensure Netloc doesnt have double dots, or leading or trailing -'s or .'s
            if re.search(r"^-|-$|\.\.|^-|\.-|-$", result.netloc):
                return False

            # Split the netloc into parts (for handling subdomains)
            parts = result.netloc.split('.')
            # Check each part of the domain for leading or trailing -'s
            for part in parts:
                if part == "" or part.startswith('-') or part.endswith('-'):
                    return False

            return True
        except ValueError:
            return False
