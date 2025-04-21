import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %z",
)

logger = logging.getLogger(__name__)
