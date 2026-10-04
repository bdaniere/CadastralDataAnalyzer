import json
import logging
from pathlib import Path

from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection

from src.utils import get_engine

# ██╗   ██╗████████╗██╗██╗     ███████╗
# ██║   ██║╚══██╔══╝██║██║     ██╔════╝
# ██║   ██║   ██║   ██║██║     ███████╗
# ██║   ██║   ██║   ██║██║     ╚════██║
# ╚██████╔╝   ██║   ██║███████╗███████║
#  ╚═════╝    ╚═╝   ╚═╝╚══════╝╚══════╝

logger = logging.getLogger(__name__)

CHECK_REQUEST_PATH = Path(__file__).resolve().parents[1] / "sql" / "raw_data_checks"


def load_sql_templates() -> dict[str, str]:
    """Load all SQL files into memory once, preserving a deterministic order."""

    templates: dict[str, str] = {}
    for sql_file in sorted(CHECK_REQUEST_PATH.rglob("*.sql")):
        key = sql_file.stem
        templates[key] = sql_file.read_text(encoding="utf-8")
    return templates


def get_tables_with_geometry(
    connection: Connection, schema: str = "raw_data"
) -> set[str]:
    """Return all tables that contain a geometry column in the target schema."""

    query = text(
        """
        SELECT DISTINCT f_table_name
        FROM geometry_columns
        WHERE f_table_schema = :schema
        """
    )
    result = connection.execute(query, {"schema": schema})
    return {row[0] for row in result}


# ████████╗ █████╗ ██████╗ ██╗     ███████╗    ███████╗ ██████╗ ██╗          ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗
# ╚══██╔══╝██╔══██╗██╔══██╗██║     ██╔════╝    ██╔════╝██╔═══██╗██║         ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗
#    ██║   ███████║██████╔╝██║     █████╗      ███████╗██║   ██║██║         ██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝
#    ██║   ██╔══██║██╔══██╗██║     ██╔══╝      ╚════██║██║▄▄ ██║██║         ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗
#    ██║   ██║  ██║██████╔╝███████╗███████╗    ███████║╚██████╔╝███████╗    ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║
#    ╚═╝   ╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝    ╚══════╝ ╚══▀▀═╝ ╚══════╝     ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝


class TableSQLChecker:
    """Execute one SQL validation on a specific table and format the result."""

    def __init__(self, sql_request: str, table_name: str, connection):
        self.sql_request = sql_request
        self.connection = connection
        self.table_name = table_name
        self.geometry_field = "geometry"
        self.schema_name = "raw_data"

    def execute_sql(self, additional_format_data: dict | None = None) -> dict:
        """Execute the SQL check and return a normalized result dictionary."""

        format_data = {
            "schema_name": self.schema_name,
            "table_name": self.table_name,
            "geometry_field": self.geometry_field,
        }
        if additional_format_data:
            format_data.update(additional_format_data)

        sql_request = self.sql_request.format(**format_data)
        result = self.connection.execute(text(sql_request))
        return self.format_result(result)

    @staticmethod
    def format_result(result) -> dict:
        """Normalize a DB result into a dict, even when the query returns no row."""

        row = result.fetchone()
        if row is None:
            return {
                "control_name": None,
                "success": False,
                "numeric_value": None,
            }

        return {
            "control_name": row[0],
            "success": bool(row[1]),
            "numeric_value": row[2] if len(row) > 2 else None,
        }


# ███╗   ███╗ █████╗ ██╗███╗   ██╗
# ████╗ ████║██╔══██╗██║████╗  ██║
# ██╔████╔██║███████║██║██╔██╗ ██║
# ██║╚██╔╝██║██╔══██║██║██║╚██╗██║
# ██║ ╚═╝ ██║██║  ██║██║██║ ╚████║
# ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝


def run_all_checks_on_tables(engine) -> dict:
    """Run all SQL checks on the tables in the raw_data schema."""

    table_results: dict[str, list[dict]] = {}
    sql_templates = load_sql_templates()

    with open(CHECK_REQUEST_PATH / "raw_data_checks.json", encoding="utf-8") as f:
        checks_by_table_and_field = json.load(f)

    with engine.connect() as connection:
        inspector = inspect(connection)
        tables_with_geometry = get_tables_with_geometry(connection)

        for raw_data_table_name in inspector.get_table_names(schema="raw_data"):
            if not inspector.has_table(raw_data_table_name, schema="raw_data"):
                continue

            checks_sql = get_generic_checks_set(
                sql_templates, raw_data_table_name, tables_with_geometry
            )
            table_results[raw_data_table_name] = [
                TableSQLChecker(
                    sql_request, raw_data_table_name, connection
                ).execute_sql()
                for sql_request in checks_sql
            ]

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
                                    "max_length": check_fields.get("varchar_length"),
                                }
                            )
                        )

    return table_results


def get_generic_checks_set(sql_templates, raw_data_table_name, tables_with_geometry):
    """Return the generic A/G SQL checks in deterministic order for a table."""

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
    engine = get_engine()
    results = run_all_checks_on_tables(engine)

    for table_name, values in results.items():
        for item in values:
            if item["success"] is False:
                print((table_name, item))
