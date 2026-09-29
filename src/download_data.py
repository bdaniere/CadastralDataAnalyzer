import logging
from pathlib import Path
from tempfile import TemporaryDirectory

import geopandas as gpd
import pandas as pd
import requests

from utils import get_engine

logger = logging.getLogger(__name__)
engine = get_engine()

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
        "Accept": "application/gzip, application/octet-stream, */*"
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
        return code_territoire[:2], code_territoire   # Commune
    else:
        raise ValueError("Le code du territoire doit être soit un code départemental (2 chiffres) soit un code communal (5 chiffres).")

def download_and_format_ban_data(code_territoire: str) -> None:
    """
    Downloads the National Address Database for a municipality or department and formats it.
    """

    dep_code, code_insee = formate_code_territoire(code_territoire)
    url = f"https://adresse.data.gouv.fr/data/ban/adresses/latest/csv/adresses-{dep_code}.csv.gz"

    with TemporaryDirectory() as tmpdirname:
        output_file_path = Path(tmpdirname) / f"adresses_{dep_code}.csv.gz"
        download_file(url, output_file_path)
        
        if output_file_path.exists():
            if code_insee:
                chunks_filtres = []
                for chunk in pd.read_csv(output_file_path, sep=';', compression='gzip', chunksize=50000, dtype=str):
                    chunk_filtre = chunk[chunk['code_insee'] == code_insee]
                    if not chunk_filtre.empty:
                        chunks_filtres.append(chunk_filtre)

                if chunks_filtres:
                    df_address = pd.concat(chunks_filtres, ignore_index=True)
                else : 
                    raise ValueError("No matching address found for the given code postal.")
            else : 
                df_address = pd.read_csv(output_file_path, sep=';', compression='gzip', dtype=str)

            # Split multiple cad_parcelle values
            df_address["cad_parcelles"] = df_address["cad_parcelles"].str.split("|")
            df_final = df_address.explode("cad_parcelles", ignore_index=True)

            gdf = gpd.GeoDataFrame(df_final, geometry=gpd.points_from_xy(df_final['x'], df_final['y']), crs="EPSG:2154")
            gdf.to_postgis("base_adresse_nationale", schema="raw_data", con=engine, if_exists="replace", index=False)   

        else:
            raise ValueError(f"No addresses were found for INSEE code {code_insee} in this department.")


def download_and_format_cadastre_data(code_territoire: str, couche: str) -> None:
    """
    Downloads cadastral data for a municipality or department and formats it.
    """

    url = get_cadastre_url(code_territoire, couche)
    with TemporaryDirectory() as tmpdirname:
        output_file_path = Path(tmpdirname) / f"cadastre-{code_territoire}-{couche}.zip"

        download_file(url, output_file_path)
        gdf = gpd.read_file(output_file_path)

        if "id" not in gdf.columns:
            gdf["id"] = range(len(gdf))

        logger.debug("Inserting data into the PostgreSQL database...")
        gdf.to_postgis(couche, schema="raw_data", con=engine, if_exists="replace", index=False)


#  ██████╗ █████╗ ██████╗  █████╗ ███████╗████████╗██████╗  █████╗ ██╗         ██████╗  █████╗ ████████╗ █████╗ 
# ██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██║         ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗
# ██║     ███████║██║  ██║███████║███████╗   ██║   ██████╔╝███████║██║         ██║  ██║███████║   ██║   ███████║
# ██║     ██╔══██║██║  ██║██╔══██║╚════██║   ██║   ██╔══██╗██╔══██║██║         ██║  ██║██╔══██║   ██║   ██╔══██║
# ╚██████╗██║  ██║██████╔╝██║  ██║███████║   ██║   ██║  ██║██║  ██║███████╗    ██████╔╝██║  ██║   ██║   ██║  ██║
#  ╚═════╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝
                                                                                                              

def get_cadastre_url(code_territoire: str, couche: str) -> str:
    """
    Constructs the URL for downloading cadastral data from cadastre.data.gouv.fr.
    """
    
    assert couche in {'communes', 'parcelles', 'batiments'}, "Invalid layer name. Must be one of 'communes', 'parcelles', or 'batiments'."

    if len(code_territoire) == 2:
        return f"https://cadastre.data.gouv.fr/bundler/cadastre-etalab/departements/{code_territoire}/shp/{couche}"
    elif len(code_territoire) == 5: 
        return f"https://cadastre.data.gouv.fr/bundler/cadastre-etalab/communes/{code_territoire}/shp/{couche}"
    else:
        raise ValueError("Invalid code_territoire. Must be a 2-digit department code or a 5-digit commune code.")


# ██████╗ ███████╗██████╗ ██╗   ██╗ ██████╗ 
# ██╔══██╗██╔════╝██╔══██╗██║   ██║██╔════╝ 
# ██║  ██║█████╗  ██████╔╝██║   ██║██║  ███╗
# ██║  ██║██╔══╝  ██╔══██╗██║   ██║██║   ██║
# ██████╔╝███████╗██████╔╝╚██████╔╝╚██████╔╝
# ╚═════╝ ╚══════╝╚═════╝  ╚═════╝  ╚═════╝                                         

if __name__ == "__main__":
    # for couche in ['communes', 'parcelles', 'batiments']:
    #     get_cadastre_url("38080", couche)
    download_and_format_ban_data("38")
