import logging
import re
from pathlib import Path
from tempfile import TemporaryDirectory

import geopandas as gpd
import pandas as pd
import requests

from utils import get_engine

logger = logging.getLogger(__name__)


# ██╗   ██╗████████╗██╗██╗     ███████╗
# ██║   ██║╚══██╔══╝██║██║     ██╔════╝
# ██║   ██║   ██║   ██║██║     ███████╗
# ██║   ██║   ██║   ██║██║     ╚════██║
# ╚██████╔╝   ██║   ██║███████╗███████║
#  ╚═════╝    ╚═╝   ╚═╝╚══════╝╚══════╝


def download_file(url: str, dest_file_path: Path) -> Path:
    """
    Downloads a file from a URL and saves it to the specified location.
    Uses a User-Agent to avoid timeout issues.
    """

    # Cheat for avoid timeout
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/gzip, application/octet-stream, */*",
    }

    try:
        with requests.get(url, headers=headers, stream=True, timeout=60) as response:
            response.raise_for_status()
            with open(dest_file_path, "wb") as f:
                f.writelines(response.iter_content(chunk_size=8192))
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download {url}: {e}")
        raise

    return dest_file_path


def get_cadastre_url(code_territoire: str, couche: str) -> str:
    """
    Constructs the URL for downloading cadastral data from cadastre.data.gouv.fr.
    """

    assert couche in {"communes", "parcelles", "batiments"}, (
        "Invalid layer name. Must be one of 'communes', 'parcelles', or 'batiments'."
    )

    if len(code_territoire) == 2:
        return f"https://cadastre.data.gouv.fr/bundler/cadastre-etalab/departements/{code_territoire}/shp/{couche}"
    elif len(code_territoire) == 5:
        return f"https://cadastre.data.gouv.fr/bundler/cadastre-etalab/communes/{code_territoire}/shp/{couche}"
    else:
        raise ValueError(
            "Invalid code_territoire. Must be a 2-digit department code or a 5-digit commune code."
        )


# ██████╗  █████╗ ███╗   ██╗    ██████╗  █████╗ ████████╗ █████╗
# ██╔══██╗██╔══██╗████╗  ██║    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗
# ██████╔╝███████║██╔██╗ ██║    ██║  ██║███████║   ██║   ███████║
# ██╔══██╗██╔══██║██║╚██╗██║    ██║  ██║██╔══██║   ██║   ██╔══██║
# ██████╔╝██║  ██║██║ ╚████║    ██████╔╝██║  ██║   ██║   ██║  ██║
# ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝


def formate_code_territoire(code_territoire: str) -> tuple[str, str | None]:
    """
    Formats the territory code to determine whether it is a department or a municipality.
    Returns a tuple (territory_code, department_code) where department_code is None for a department.
    """

    if len(code_territoire) == 2:
        return code_territoire, None  # Département
    elif len(code_territoire) == 5:
        return code_territoire[:2], code_territoire  # Commune
    else:
        raise ValueError(
            "Le code du territoire doit être soit un code départemental (2 chiffres) soit un code communal (5 chiffres)."
        )


def download_and_format_ban_data(code_territoire: str) -> None:
    """
    Downloads the National Address Database for a municipality or department and formats it.
    """

    dep_code, code_commune = formate_code_territoire(code_territoire)
    url = f"https://adresse.data.gouv.fr/data/ban/adresses/latest/csv/adresses-{dep_code}.csv.gz"

    with TemporaryDirectory() as tmpdirname:
        output_file_path = Path(tmpdirname) / f"adresses_{dep_code}.csv.gz"
        download_file(url, output_file_path)

        if output_file_path.exists():
            if code_commune:
                chunks_filtres = []
                for chunk in pd.read_csv(
                    output_file_path,
                    sep=";",
                    compression="gzip",
                    chunksize=50000,
                    dtype=str,
                ):
                    chunk_filtre = chunk[chunk["code_postal"] == code_commune]
                    if not chunk_filtre.empty:
                        chunks_filtres.append(chunk_filtre)

                if chunks_filtres:
                    df_final = pd.concat(chunks_filtres, ignore_index=True)
                    df_final.to_sql(
                        "base_adresse_nationale",
                        schema="raw_data",
                        con=engine,
                        if_exists="replace",
                        index=False,
                    )

                else:
                    logger.warning(
                        f"No addresses were found for INSEE code {code_commune} in this department."
                    )
            else:
                df_final = pd.read_csv(
                    output_file_path, sep=";", compression="gzip", dtype=str
                )
                df_final.to_sql(
                    "base_adresse_nationale",
                    schema="raw_data",
                    con=engine,
                    if_exists="replace",
                    index=False,
                )


#  ██████╗ ██╗███████╗    ██████╗  █████╗ ████████╗ █████╗
# ██╔════╝ ██║██╔════╝    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗
# ██║  ███╗██║███████╗    ██║  ██║███████║   ██║   ███████║
# ██║   ██║██║╚════██║    ██║  ██║██╔══██║   ██║   ██╔══██║
# ╚██████╔╝██║███████║    ██████╔╝██║  ██║   ██║   ██║  ██║
#  ╚═════╝ ╚═╝╚══════╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝


class GeospatialDatasetImporter:
    def __init__(self, engine, url: str, name: str, extention: str):
        """

        Initializes a new instance of the DataDownloader class.

        Parameters:
            engine --TODO--
            url (str): The URL from which to download the file.
            name (str): The name of the file to be saved.
            extention (str): The extension of the file.
        """

        self.url = url
        self.name = re.sub(r"[^a-zA-Z0-9_]", "_", name.lower())
        self.extention = extention

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/gzip, application/octet-stream, */*",
            }
        )

    def download_and_send_to_db(self):
        """
        Downloads the file from the specified URL and sends it to the database.
        """
        with TemporaryDirectory() as tmpdirname:
            output_file_path = Path(tmpdirname) / self.filename

            self.download(output_file_path)
            gdf = self.load_geodataframe(output_file_path)

            logger.info("Inserting %s into PostGIS", self.name)
            gdf.to_postgis(
                self.name,
                schema="raw_data",
                con=engine,
                if_exists="replace",
                index=False,
            )

    def load_geodataframe(self, dest_file_path: Path):
        """
        Loads a GeoPandas GeoDataFrame from a file path and saves it to the database.
        """

        logger.info("Reading file with GeoPandas")
        gdf = gpd.read_file(dest_file_path)
        if gdf.crs != "EPSG:2154":
            gdf = gdf.to_crs("EPSG:2154")

        return gdf

    def download(self, dest_file_path: Path):
        """
        Downloads a file from a URL and saves it to the specified location.
        Uses a User-Agent to avoid timeout issues.

        Parameters:
            dest_file_path (Path): The path where the file will be saved.
        """

        logger.info("Downloading %s", self.url)
        try:
            with self.session.get(self.url, stream=True, timeout=60) as response:
                response.raise_for_status()
                with open(dest_file_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            logger.info("Saved to %s", dest_file_path)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download {self.url}: {e}")
            raise

        if dest_file_path.stat().st_size == 0:
            raise ValueError("Downloaded file is empty")

    @property
    def filename(self):
        return f"{self.name}.{self.extention}"


# ██████╗ ███████╗██████╗ ██╗   ██╗ ██████╗
# ██╔══██╗██╔════╝██╔══██╗██║   ██║██╔════╝
# ██║  ██║█████╗  ██████╔╝██║   ██║██║  ███╗
# ██║  ██║██╔══╝  ██╔══██╗██║   ██║██║   ██║
# ██████╔╝███████╗██████╔╝╚██████╔╝╚██████╔╝
# ╚═════╝ ╚══════╝╚═════╝  ╚═════╝  ╚═════╝

if __name__ == "__main__":
    engine = get_engine()

    # Récupération des données cadastrales
    for couche in ["communes", "parcelles", "batiments"]:
        cadastral_data_url = get_cadastre_url("95", couche)

        cadastral_dataset = GeospatialDatasetImporter(
            engine, cadastral_data_url, couche, ".zip"
        )
        cadastral_dataset.download_and_send_to_db()

    # récupération du reseau d'assainissement : https://www.data.gouv.fr/datasets/canalisations-capv-opendata-4
    reseau_dataset = GeospatialDatasetImporter(
        engine,
        "https://www.data.gouv.fr/api/1/datasets/r/bf1a6317-b6f7-4126-9c8c-86307e91362e",
        "reseau_assainissement",
        ".geojson",
    )
    reseau_dataset.download_and_send_to_db()

    # Récupération des données adresse
    download_and_format_ban_data("95")
