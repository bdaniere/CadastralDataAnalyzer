import json
import logging
from pathlib import Path

from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection

from utils import get_engine

engine = get_engine()
logger = logging.getLogger(__name__)


CHECK_REQUEST_PATH = Path(__file__).resolve().parents[1] / "sql" / "raw_data_checks"


def load_sql_templates() -> dict[Path, str]:
    """
    Load all SQL files into memory just once.
    """

    templates = {}
    for sql_file in CHECK_REQUEST_PATH.rglob("*.sql"):
        templates[sql_file.stem] = sql_file.read_text(encoding="utf-8")
    return templates


def get_tables_with_geometry(connection: Connection, schema: str = "raw_data") -> set:
    """
    Retrieves tables with a geometric column using the PostGIS view.

    :param connection: Database connection.
    :param schema: Schema name to search for geometric columns. Defaults to "raw_data".
    """

    query = text("""
        SELECT DISTINCT f_table_name 
        FROM geometry_columns 
        WHERE f_table_schema = :schema
    """)

    result = connection.execute(query, {"schema": schema})
    return {row[0] for row in result}


class TableSQLChecker:
    """
    Class to check SQL conditions on a specific table.
    It reads SQL files, executes them, and formats the results.
    """

    def __init__(self, sql_request: str, table_name: str, connection):
        """
        Initialize the TableSQLChecker with the SQL file, table name, and database connection.

        :param sql_file: Path to the SQL file containing the check.
        :param table_name: Name of the table to check.
        :param connection: SQLAlchemy database connection.
        """

        self.sql_request = sql_request
        self.connection = connection

        self.table_name = table_name
        self.geometry_field = "geometry"

    def execute_sql(self, additional_format_data: dict | None = None) -> dict:
        """
        Execute the SQL check on the table.

        :return: Formatted result of the SQL check.
        """

        additional_format_data = additional_format_data or {}
        sql_request = self.sql_request.format(
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

    sql_templates = load_sql_templates()

    with open(CHECK_REQUEST_PATH / "raw_data_checks.json") as f:
        checks_by_table_and_field = json.load(f)

    with engine.connect() as connection:
        tables_with_geometry = get_tables_with_geometry(connection)

        for raw_data_table_name in inspect(connection).get_table_names("raw_data"):
            if inspector.has_table(raw_data_table_name, schema="raw_data"):
                checks_sql = get_generic_checks_set(
                    sql_templates, raw_data_table_name, tables_with_geometry
                )

                table_results[raw_data_table_name] = [
                    TableSQLChecker(
                        sql_request, raw_data_table_name, connection
                    ).execute_sql()
                    for sql_request in checks_sql
                ]

                # Checks from raw_data_checks.json
                if raw_data_table_name in checks_by_table_and_field:
                    for check_fields in checks_by_table_and_field[raw_data_table_name]:
                        for sql_request_name in check_fields["checks"]:
                            table_results[raw_data_table_name].append(
                                TableSQLChecker(
                                    sql_templates[sql_request_name],
                                    raw_data_table_name,
                                    connection,
                                ).execute_sql(
                                    {
                                        "table_field": check_fields["field"],
                                        "max_length": check_fields.get(
                                            "varchar_length", None
                                        ),
                                    }
                                )
                            )

    return table_results


def get_generic_checks_set(sql_templates, raw_data_table_name, tables_with_geometry):
    """DOCSTRING TO DO"""

    checks_sql = {
        sql_content
        for sql_name, sql_content in sql_templates.items()
        if sql_name.startswith("A")
    }
    if raw_data_table_name in tables_with_geometry:
        checks_sql = checks_sql.union(
            sql_content
            for sql_name, sql_content in sql_templates.items()
            if sql_name.startswith("G")
        )

    return checks_sql


# ██████╗ ███████╗██████╗ ██╗   ██╗ ██████╗
# ██╔══██╗██╔════╝██╔══██╗██║   ██║██╔════╝
# ██║  ██║█████╗  ██████╔╝██║   ██║██║  ███╗
# ██║  ██║██╔══╝  ██╔══██╗██║   ██║██║   ██║
# ██████╔╝███████╗██████╔╝╚██████╔╝╚██████╔╝
# ╚═════╝ ╚══════╝╚═════╝  ╚═════╝  ╚═════╝

if __name__ == "__main__":
    results = run_all_checks_on_tables(engine)

    for not_pass in [
        (table_name, ii)
        for table_name, values in results.items()
        for ii in values
        if ii["success"] == False
    ]:
        print(not_pass)

    breakpoint()
