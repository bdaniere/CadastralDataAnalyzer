import logging
from glob import glob
from pathlib import Path

from geoalchemy2 import Geometry
from sqlalchemy import inspect, text

from utils import get_engine

engine = get_engine()
logger = logging.getLogger(__name__)


CHECK_REQUEST_PATH = Path(__file__).resolve().parents[1] / 'sql' / 'raw_data_checks'

class TableSQLChecker:
    """
    Class to check SQL conditions on a specific table.
    It reads SQL files, executes them, and formats the results.
    """

    def __init__(self, sql_file: str, table_name: str, connection):
        """
        Initialize the TableSQLChecker with the SQL file, table name, and database connection.

        :param sql_file: Path to the SQL file containing the check.
        :param table_name: Name of the table to check.
        :param connection: SQLAlchemy database connection.
        """

        self.sql_file = sql_file
        self.connection = connection

        self.table_name = table_name
        self.geometry_field = "geometry"

    def execute_sql(self) -> dict:
        """
        Execute the SQL check on the table.

        :return: Formatted result of the SQL check.
        """

        with open(self.sql_file, 'r') as file:
            sql_request = file.read().format(schema_name="raw_data", table_name=self.table_name, geometry_field=self.geometry_field)

        self.result = self.connection.execute(text(sql_request))
        return self.format_result()


    def format_result(self) -> dict:
        """
        TO DO : revoir le fonctionnement : pour le moment c'est OK // mais pas stable
        """

        result_fetchall = self.result.fetchall()
        if isinstance(result_fetchall, list) and not result_fetchall:
            value = 0
        else:
            value = result_fetchall[0][0]

        return {"check" : Path(self.sql_file).stem, "status" : None, "value" : value}


def run_all_checks_on_tables(engine) -> list:
    """
    Run all SQL checks on all raw data tables.

    :param engine: SQLAlchemy database engine.
    :return: List of results for all tables and checks.
    """

    table_results = []
    inspector = inspect(engine)

    for raw_data_table_name in ['communes', 'sections', 'feuilles', 'parcelles', 'batiments', 'base_adresse_nationale']:
        results = []
        if inspector.has_table(raw_data_table_name, schema="raw_data"):
            columns = inspector.get_columns(raw_data_table_name, schema="raw_data")
            has_geometry = any(isinstance(col["type"], Geometry) for col in columns)

            sql_request_filepaths = glob(str(CHECK_REQUEST_PATH / "attribute_checks" / '*.sql'))
            if has_geometry:
                sql_request_filepaths.extend(glob(str(CHECK_REQUEST_PATH / "geometry_checks" / '*.sql')))
            
            with engine.connect() as connection:
                table_results.extend(
                    TableSQLChecker(sql_request_filepath, raw_data_table_name, connection).execute_sql()
                    for sql_request_filepath in sql_request_filepaths
                )

                
        else :
            logger.error(f"Table {raw_data_table_name} does not exist in schema 'raw_data'")
            results.append({"check" : "table_exists", "status" : "error", "value" : f"Table {raw_data_table_name} does not exist in schema 'raw_data'"})

        table_results.extend(results)

    return table_results



# ██████╗ ███████╗██████╗ ██╗   ██╗ ██████╗ 
# ██╔══██╗██╔════╝██╔══██╗██║   ██║██╔════╝ 
# ██║  ██║█████╗  ██████╔╝██║   ██║██║  ███╗
# ██║  ██║██╔══╝  ██╔══██╗██║   ██║██║   ██║
# ██████╔╝███████╗██████╔╝╚██████╔╝╚██████╔╝
# ╚═════╝ ╚══════╝╚═════╝  ╚═════╝  ╚═════╝                                         

if __name__ == "__main__":
    
        results = run_all_checks_on_tables(engine)
        print(results)