import logging
from pathlib import Path
from tempfile import TemporaryDirectory

import geopandas as gpd
import requests
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)

def get_cadastre_url(code_territoire:str, couche:str) -> str:
    """Construct the URL for downloading cadastral data from cadastre.data.gouv.fr"""

    assert couche in {'communes', 'sections', 'feuilles', 'parcelles', 'batiments'}, "Invalid layer name. Must be one of 'communes', 'sections', 'feuilles', 'parcelles', or 'batiments'."

    if len(code_territoire) == 2:
        return f"https://cadastre.data.gouv.fr/bundler/cadastre-etalab/departements/{code_territoire}/shp/{couche}"
    elif len(code_territoire) == 5: 
        return f"https://cadastre.data.gouv.fr/bundler/cadastre-etalab/communes/{code_territoire}/shp/{couche}"
    else:
        raise ValueError("Invalid code_territoire. Must be a 2-digit department code or a 5-digit commune code.")

def download_cadastre_data(code_territoire: str, couche: str) -> None:
    """
    Downloading a ZIP file containing cadastral data from cadastre.data.gouv.fr

    cadastre doc : https://www.data.gouv.fr/dataservices/api-cadastre
    """

    url = get_cadastre_url(code_territoire, couche)
    with TemporaryDirectory() as tmpdirname:
        destination_file = Path(tmpdirname) / f"cadastre-{code_territoire}-{couche}.zip"

        logger.debug(f"Download from : {url}")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(destination_file, "wb") as f:
                f.writelines(response.iter_content(chunk_size=8192))
            logger.debug(f"File saved successfully : {destination_file}")
        else:
            logger.error(f"Error during download. Status code : {response.status_code}")

        logger.debug("Reading the geographic file (GeoPandas)...")
        gdf = gpd.read_file(destination_file)

        logger.debug("Inserting data into the PostgreSQL database...")
        engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5433/cadastral_data")
        gdf.to_postgis(couche, schema="raw_data", con=engine, if_exists="replace", index=False)


# ██████╗ ███████╗██████╗ ██╗   ██╗ ██████╗ 
# ██╔══██╗██╔════╝██╔══██╗██║   ██║██╔════╝ 
# ██║  ██║█████╗  ██████╔╝██║   ██║██║  ███╗
# ██║  ██║██╔══╝  ██╔══██╗██║   ██║██║   ██║
# ██████╔╝███████╗██████╔╝╚██████╔╝╚██████╔╝
# ╚═════╝ ╚══════╝╚═════╝  ╚═════╝  ╚═════╝                                         

if __name__ == "__main__":
    for couche in ['communes', 'sections', 'feuilles', 'parcelles', 'batiments']:
        download_cadastre_data("38080", couche)
    

