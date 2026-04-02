# Metabolite Annotator

## Installation

```bash
uv tool install git+https://github.com/earth-metabolome-initiative/metabolite-annotator
```

## Example usage
```bash
uvx metabolite-annotator --help
````

```bash
Usage: metabolite-annotator [OPTIONS] COMMAND [ARGS]...

Options:
  -i, --input_mgf PATH   The input MGF to annotate.  [required]
  -o, --output_dir PATH  The directory where results will be stored.
  --ion-mode [pos|neg]   Ionization mode for the annotation
  --root PATH            Project root directory
  --cache-dir PATH       The directory where cache will be stored. If not set,
                         it will default to ~/.cache/metabolite-annotator
  --help                 Show this message and exit.

Commands:
  all     Run all annotation tools (CFM-ID, GNPS, Sirius and create a...
  cfmid   Compare your input MGF to all spectra in ISDB and returns the...
  fbmn    Create a Molecular Network and save as a graphml file
  gnps    Compare your input MGF to all spectra in GNPS and returns the...
  sirius  Run Sirius with default parameters with eiter Orbitrap or QTOF...
```