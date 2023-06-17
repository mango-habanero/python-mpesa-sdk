# standard imports
import json
from typing import Dict, Optional

# external imports
from requests import Request, Response

# local imports

# test imports


def build_response(content: Optional[Dict], encoding: str, reason: str, status_code: int):
    response = Response()
    response._content = json.dumps(content).encode()
    response.encoding = encoding
    response.reason = reason
    response.status_code = status_code
    return response
