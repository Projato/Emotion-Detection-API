from loguru import logger
import sys


def setup_logger() -> None:
    logger.remove() #Clear existing logger outputs

    logger.add( #adding a new log output destination
        sys.stdout,
        level="INFO", #info + warnig + error
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss} </green> | "
            "<level>{level}</level> | "
            "{message}"
    ), 
    backtrace=False,
    diagnose=False,
    )