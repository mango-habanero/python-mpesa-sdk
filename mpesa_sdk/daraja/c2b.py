"""This module contains the C2B class that is used to make C2B requests to the Daraja API."""

# standard imports
import json
import logging
from typing import Dict, Union


class C2BCallbackParser:
    """This class is used to parse the callback request sent by Safaricom to the callback url."""

    def __init__(self, request: Dict[str, Union[str, int]]):
        self.request = request

    def parse(self):
        """This method parses the callback request.
        :return: parsed callback request.
        :rtype: dict
        """
        logging.info("Callback request: %s", json.dumps(self.request))
