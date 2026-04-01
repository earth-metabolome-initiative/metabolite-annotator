from pathlib import Path
import click

from .config import Config, IonMode, config, PrecursorMZToleranceType
from .run import _run_cfmid, _run_gnps


@click.group()
@click.argument("input_mgf", type=click.Path(exists=True))
@click.option("--root", type=click.Path(), default=".", help="Project root directory")
@click.option(
    "--results-dir",
    type=click.Path(),
    default="results",
    help="The directory where results will be stored.",
)
@click.option(
    "--cache-dir",
    type=click.Path(),
    default=None,
    help="The directory where cache will be stored. If not set, it will default to ~/.cache/metabolite-annotator",
)
@click.option(
    "--ion-mode",
    type=click.Choice(IonMode, case_sensitive=False),
    default=IonMode.POS,
    help="Ionization mode for the annotation",
)
@click.pass_context
def main(
    ctx,
    input_mgf: Path,
    root: Path,
    results_dir: Path,
    cache_dir: Path | None,
    ion_mode: IonMode,
):
    ctx.ensure_object(dict)
    config = Config(
        project_root=Path(root).resolve(),
        results_dir=Path(results_dir),
        ionization_mode=ion_mode,
    )
    config.cache_dir = Path(cache_dir).resolve() if cache_dir is not None else None
    ctx.obj["config"] = config
    ctx.obj["input_mgf"] = Path(input_mgf).resolve()
    ctx.obj["ion_mode"] = ion_mode


# Reusable decorator for the shared precursor options
def precursor_options(f):
    f = click.option(
        "--precursor-mz-tolerance-type",
        type=click.Choice(PrecursorMZToleranceType, case_sensitive=False),
        default=PrecursorMZToleranceType.PPM,
        help="Tolerance type for the precursor m/z matching",
    )(f)
    f = click.option(
        "--precursor-mz-tolerance",
        type=click.FloatRange(min=0.0, min_open=True),
        default=20.0,
        help="Tolerance value for the precursor m/z matching (in ppm or Da, depending on the precursor_mz_tolerance_type)",
    )(f)
    return f


@main.command()
@precursor_options
@click.pass_context
def cfmid(
    ctx,
    precursor_mz_tolerance_type: PrecursorMZToleranceType,
    precursor_mz_tolerance: float,
):
    config: Config = ctx.obj["config"]
    config.precursor_mz_tolerance_type = precursor_mz_tolerance_type
    config.precursor_mz_tolerance = precursor_mz_tolerance
    _run_cfmid(config, ctx.obj["input_mgf"])


@main.command()
@precursor_options
@click.pass_context
def gnps(
    ctx,
    precursor_mz_tolerance_type: PrecursorMZToleranceType,
    precursor_mz_tolerance: float,
):
    config: Config = ctx.obj["config"]
    config.precursor_mz_tolerance_type = precursor_mz_tolerance_type
    config.precursor_mz_tolerance = precursor_mz_tolerance
    _run_gnps(config, ctx.obj["input_mgf"])


@main.command()
@precursor_options
@click.pass_context
def all(
    ctx,
    precursor_mz_tolerance_type: PrecursorMZToleranceType,
    precursor_mz_tolerance: float,
):
    """Run all annotation tools (CFM-ID and GNPS) sequentially."""
    config: Config = ctx.obj["config"]
    config.precursor_mz_tolerance_type = precursor_mz_tolerance_type
    config.precursor_mz_tolerance = precursor_mz_tolerance

    click.echo("Running CFM-ID annotation...")
    _run_cfmid(config, ctx.obj["input_mgf"])
    click.echo("CFM-ID done.")

    click.echo("Running GNPS annotation...")
    _run_gnps(config, ctx.obj["input_mgf"])
    click.echo("GNPS done.")

    click.echo("All annotations complete.")
