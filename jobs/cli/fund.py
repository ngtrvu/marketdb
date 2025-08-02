import click

from utils.logger import logger


@click.command()
def commands():
    logger.info("Fund: 0.0.1")
