import logging


def setup_logging() -> None:
    """Konfiguruje system logowania aplikacji."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename="pipeline.log",
    )