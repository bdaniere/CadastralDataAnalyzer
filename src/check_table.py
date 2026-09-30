import json
import logging
from glob import glob
from pathlib import Path

from geoalchemy2 import Geometry
from sqlalchemy import inspect, text

from utils import get_engine

engine = get_engine()
logger = logging.getLogger(__name__)


CHECK_REQUEST_PATH = Path(__file__).resolve().parents[1] / "sql" / "raw_data_checks"
RAW_DATA_TABLES = [
    "communes",
    "parcelles",
    "batiments",
    "base_adresse_nationale",
]


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

    def execute_sql(self, additional_format_data: dict | None = None) -> dict:
        """
        Execute the SQL check on the table.

        :return: Formatted result of the SQL check.
        """

        additional_format_data = additional_format_data or {}
        with open(self.sql_file, "r") as file:
            sql_request = file.read().format(
                schema_name="raw_data",
                table_name=self.table_name,
                geometry_field=self.geometry_field,
                **additional_format_data,
            )

        result = self.connection.execute(text(sql_request))
        return self.format_result(result)

    @staticmethod
    def format_result(result) -> dict:
        """
        Format the result of the SQL check into a dictionary.

        :return: Dictionary containing the check name, status, value, and message.
        """

        row = result.fetchone()
        return {
            "control_name": row[0],
            "success": row[1],
            "numeric_value": row[2],
        }


def run_all_checks_on_tables(engine) -> dict:
    """
    Run all SQL checks on all raw data tables.

    :param engine: SQLAlchemy database engine.
    :return: List of results for all tables and checks.
    """

    table_results = {}
    inspector = inspect(engine)

    with open(CHECK_REQUEST_PATH / "raw_data_checks.json") as f:
        raw_data_check_by_table = json.load(f)

    with engine.connect() as connection:
        for raw_data_table_name in RAW_DATA_TABLES:
            if inspector.has_table(raw_data_table_name, schema="raw_data"):
                columns = inspector.get_columns(raw_data_table_name, schema="raw_data")
                has_geometry = any(isinstance(col["type"], Geometry) for col in columns)

                check_sql_files = glob(
                    str(CHECK_REQUEST_PATH / "attribute_checks" / "*.sql")
                )
                if has_geometry:
                    check_sql_files.extend(
                        glob(str(CHECK_REQUEST_PATH / "geometry_checks" / "*.sql"))
                    )

                table_results[raw_data_table_name] = [
                    TableSQLChecker(
                        check_sql_file, raw_data_table_name, connection
                    ).execute_sql()
                    for check_sql_file in check_sql_files
                ]

                # Checks from raw_data_checks.json
                for check_data in raw_data_check_by_table[raw_data_table_name]:
                    for check_nickname in check_data["checks"]:
                        sql_request_path = (
                            CHECK_REQUEST_PATH
                            / "table_checks"
                            / raw_data_check_by_table["check_path"][check_nickname]
                        )

                        table_results[raw_data_table_name].append(
                            TableSQLChecker(
                                sql_request_path,
                                raw_data_table_name,
                                connection,
                            ).execute_sql(
                                {
                                    "table_field": check_data["field"],
                                    "max_length": check_data.get(
                                        "varchar_lenght", None
                                    ),
                                }
                            )
                        )

            else:
                raise ValueError(
                    f"Table {raw_data_table_name} does not exist in schema 'raw_data'"
                )

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
