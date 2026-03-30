from pathlib import Path

import click

from .config import Config, IonMode, config


@click.group()
@click.option("--root", type=click.Path(), default=".", help="Project root directory")
@click.option(
    "--ion-mode",
    type=click.Choice(IonMode, case_sensitive=False),
    default=IonMode.POS,
    help="Ionization mode for the annotation",
)
@click.pass_context
def main(ctx, root: Path, ion_mode: IonMode):
    global config
    ctx.ensure_object(dict)
    config = Config(project_root=Path(root).resolve(), ionization_mode=ion_mode)
    ctx.obj["config"] = config
