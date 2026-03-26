from metabolite_annotator.constants.urls import ISDB_POS_FILENAME
from metabolite_annotator.download import default_cache_dir, download_isdb_pos


def test_download_isdb_pos():
    output = f"{default_cache_dir()}/libraries/{ISDB_POS_FILENAME}"
    download_isdb_pos(output)
