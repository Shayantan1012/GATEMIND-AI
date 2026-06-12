import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_file_logging(app):
    if not app.config.get("ENABLE_FILE_LOGGING", True):
        return

    log_folder = Path(app.config["LOG_FOLDER"])
    log_folder.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    application_handler = RotatingFileHandler(
        log_folder / "server.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    application_handler.setLevel(logging.INFO)
    application_handler.setFormatter(formatter)

    error_handler = RotatingFileHandler(
        log_folder / "server.err",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    for logger in (app.logger, logging.getLogger("werkzeug")):
        logger.setLevel(logging.INFO)
        logger.addHandler(application_handler)
        logger.addHandler(error_handler)
