from pathlib import Path

import click

from .config import Config, config


@click.group()
@click.option("--root", type=click.Path(), default=".", help="Project root directory")
@click.pass_context
def main(ctx, root):
    global config
    ctx.ensure_object(dict)
    config = Config(project_root=Path(root).resolve())
    ctx.obj["config"] = config
