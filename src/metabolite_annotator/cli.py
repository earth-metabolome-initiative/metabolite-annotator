from pathlib import Path
import click

from .config import Config, IonMode, PrecursorMZToleranceType, FBMNSimilarityType
from .tools.sirius.instrument import InstrumentType

from .run import _run_cfmid, _run_gnps, _run_sirius, _run_fbmn


@click.group()
@click.argument("input_mgf", type=click.Path(exists=True))
@click.option("--root", type=click.Path(), default=".", help="Project root directory")
@click.option(
    "--output_dir",
    "-o",
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
    input_mgf: str,
    root: str,
    output_dir: str,
    cache_dir: str | None,
    ion_mode: IonMode,
):
    ctx.ensure_object(dict)
    config = Config(
        project_root=Path(root).resolve(),
        results_dir=Path(output_dir),
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
    """Compare your input MGF to all spectra in ISDB and returns the results as a CSV."""
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
    """Compare your input MGF to all spectra in GNPS and returns the results as a CSV."""
    config: Config = ctx.obj["config"]
    config.precursor_mz_tolerance_type = precursor_mz_tolerance_type
    config.precursor_mz_tolerance = precursor_mz_tolerance
    _run_gnps(config, ctx.obj["input_mgf"])


def sirius_options(f):
    f = click.option(
        "--instrument-type",
        type=click.Choice(InstrumentType, case_sensitive=False),
        default=InstrumentType.Orbitrap,
        help="Instrument type setting for SIRIUS.",
    )(f)
    f = click.option(
        "--project-name",
        type=str,
        default="sirius_results",
        help="Name of the SIRIUS project.",
    )(f)
    f = click.option(
        "--ms2-only",
        is_flag=True,
        help="If set, only MS2 spectra will be imported into SIRIUS. This is NOT recommended as SIRIUS uses MS1 for better annotation. This option defaults to False.",
    )(f)
    return f


@main.command()
@sirius_options
@click.pass_context
def sirius(ctx, instrument_type: InstrumentType, project_name: str, ms2_only: bool):
    """Run Sirius with default parameters with eiter Orbitrap or QTOF depending on your instrumnet."""
    config: Config = ctx.obj["config"]
    config.sirius_instrument_type = instrument_type
    _run_sirius(
        config=config,
        input_mgf=ctx.obj["input_mgf"],
        project_name=project_name,
        ms2_only=ms2_only,
    )


def fbmn_options(f):
    f = click.option(
        "--similarity-metric",
        "-m",
        type=click.Choice(FBMNSimilarityType),
        default=FBMNSimilarityType.COSINE,
        help="The metrc to use for similarity between spectra.",
    )(f)
    f = click.option(
        "--knn-neighbours",
        type=click.IntRange(min=1),
        default=5,
        help="The number of neighbours in the k-NN",
    )(f)
    f = click.option(
        "--threshold",
        type=click.FloatRange(min=0.0, max=1.0),
        default=0.7,
        help="The threshold were the edges will be removed.",
    )(f)
    return f


@main.command()
@fbmn_options
@click.pass_context
def fbmn(
    ctx,
    similarity_metric: FBMNSimilarityType,
    knn_neighbours: int,
    threshold: float,
):
    config: Config = ctx.obj["config"]
    config.fbmn_similarity_type = similarity_metric
    config.fbmn_sim_threshold = threshold
    config.knn_neighbours = knn_neighbours
    _run_fbmn(config=config, input_file=ctx.obj["input_mgf"])


@main.command()
@precursor_options
@sirius_options
@fbmn_options
@click.pass_context
def all(
    ctx,
    precursor_mz_tolerance_type: PrecursorMZToleranceType,
    precursor_mz_tolerance: float,
    instrument_type: InstrumentType,
    project_name: str,
    ms2_only: bool,
    similarity_metric: FBMNSimilarityType,
    knn_neighbours: int,
    threshold: float,
):
    """Run all annotation tools (CFM-ID, GNPS, Sirius and create a Molecular Network) sequentially."""
    config: Config = ctx.obj["config"]
    config.precursor_mz_tolerance_type = precursor_mz_tolerance_type
    config.precursor_mz_tolerance = precursor_mz_tolerance
    config.sirius_instrument_type = instrument_type
    config.fbmn_similarity_type = similarity_metric
    config.fbmn_sim_threshold = threshold
    config.knn_neighbours = knn_neighbours

    click.echo("Running CFM-ID annotation...")
    _run_cfmid(config, ctx.obj["input_mgf"])
    click.echo("CFM-ID done.")

    click.echo("Running GNPS annotation...")
    _run_gnps(config, ctx.obj["input_mgf"])
    click.echo("GNPS done.")

    click.echo("Running Sirius annotations...")
    _run_sirius(
        config=config,
        input_mgf=ctx.obj["input_mgf"],
        project_name=project_name,
        ms2_only=ms2_only,
    )
    click.echo("Sirius done.")

    click.echo("Running Feature Based Molecular Network (FBMN) ")
    _run_fbmn(config=config, input_file=ctx.obj["input_mgf"])
    click.echo("FBMN done.")

    click.echo("All annotations complete.")
