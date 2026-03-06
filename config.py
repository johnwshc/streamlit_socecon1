import os
from pathlib import Path
from dotenv import load_dotenv


class Config:


    basedir = os.path.abspath(os.path.dirname(__file__))
    GIT_REPO = "https://github.com/johnwshc/st_soc"

    JSON_DIR = Path(basedir).joinpath('json').as_posix()
    DATA_DIR = Path(f"{basedir}/data").as_posix()
    DATA_SAINC = Path(f"{DATA_DIR}/income/SAINC").as_posix()
    POP_DATA_DIR = Path(f"{DATA_DIR}/population").as_posix()
    MARKDOWN_DIR = Path(f"{basedir}/markdown").as_posix()