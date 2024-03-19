import os
from urllib.parse import urlencode, urljoin


def build_url(base_url, params=[], path=""):
    if  params:
        url_with_params = base_url + "?" + urlencode(params)
        return url_with_params
    elif path:
        # Construire l'URL complète
        full_url = urljoin(base_url, path)
        return full_url

    return base_url
