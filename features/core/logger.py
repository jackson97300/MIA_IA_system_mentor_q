#!/usr/bin/env python3
"""
core/logger.py - Module logger simple pour features
"""

import logging

def get_logger(name: str):
    """Retourne un logger configuré"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logging.basicConfig(
            level=logging.INFO, 
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    return logger

