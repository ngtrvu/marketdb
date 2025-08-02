import click

from utils.logger import logger


@click.command()
def commands():
    logger.info("ETF: 0.0.1")
