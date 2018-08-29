import base64
import logging
import io

import requests
from fints.parser import FinTS3Parser
from fints.utils import Password

from .message import FinTSInstituteMessage, FinTSMessage
from .exceptions import *

logger = logging.getLogger(__name__)


class FinTSHTTPSConnection:
    def __init__(self, url):
        self.url = url

    def send(self, msg: FinTSMessage):
        log_out = io.StringIO()
        with Password.protect():
            msg.print_nested(stream=log_out, prefix="\t")
            logger.debug("Sending >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n{}\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n".format(log_out.getvalue()))
            log_out.truncate(0)

        r = requests.post(
            self.url, data=base64.b64encode(msg.render_bytes()),
        )

        if r.status_code < 200 or r.status_code > 299:
            raise FinTSConnectionError('Bad status code {}'.format(r.status_code))

        response = base64.b64decode(r.content.decode('iso-8859-1'))
        retval = FinTSInstituteMessage(segments=response)

        with Password.protect():
            retval.print_nested(stream=log_out, prefix="\t")
            logger.debug("Received <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n{}\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n".format(log_out.getvalue()))
        return retval
