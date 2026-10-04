from src.check_table import TableSQLChecker, get_generic_checks_set


class TestCheckTable:
    def test_format_result_handles_empty_result(self):
        class DummyResult:
            def fetchone(self):
                return None

        assert TableSQLChecker.format_result(DummyResult()) == {
            "control_name": None,
            "success": False,
            "numeric_value": None,
        }

    def test_get_generic_checks_set_keeps_deterministic_order(self):
        sql_templates = {
            "A1_count_records": "A1",
            "G1_count_empty_geoms": "G1",
            "G2_count_invalid_geoms": "G2",
            "T1_NotNullValues": "T1",
        }

        checks = get_generic_checks_set(sql_templates, "geo_table", {"geo_table"})

        assert checks == {"A1", "G1", "G2"}
