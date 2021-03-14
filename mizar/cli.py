"""
add cli tasks here

executed like $ mizar TASK_NAME ARGS KWARGS

using click so see docs @ https://click.palletsprojects.com/en/7.x/
"""
import click


@click.group()
def cli():
    """cli tool"""
    pass


@cli.command()
def hello():
    click.echo("hello this is our first command")
