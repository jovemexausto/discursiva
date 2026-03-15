from __future__ import annotations

import logging
from typing import Any

from ..utils import response

log = logging.getLogger(__name__)

def handler(event: dict, context: Any) -> dict:
    return response(200, { "status": "ok" })
