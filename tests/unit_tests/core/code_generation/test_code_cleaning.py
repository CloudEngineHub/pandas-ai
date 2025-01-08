import ast
import unittest
from unittest.mock import MagicMock

from pandasai.agent.state import AgentState
from pandasai.core.code_generation.code_cleaning import CodeCleaner
from pandasai.dataframe.base import DataFrame
from pandasai.exceptions import BadImportError, MaliciousQueryError


class TestCodeCleaner(unittest.TestCase):
    def setUp(self):
        # Setup a mock context for CodeCleaner
        self.context = MagicMock(spec=AgentState)
        self.cleaner = CodeCleaner(self.context)
        self.sample_df = DataFrame(
            {
                "country": ["United States", "United Kingdom", "Japan", "China"],
                "gdp": [
                    19294482071552,
                    2891615567872,
                    4380756541440,
                    14631844184064,
                ],
                "happiness_index": [6.94, 7.22, 5.87, 5.12],
            }
        )

    def test_check_imports_valid(self):
        node = ast.Import(names=[ast.alias(name="pandas", asname=None)])
        result = self.cleaner._check_imports(node)
        self.assertIsNone(result)

    def test_check_imports_invalid(self):
        node = ast.Import(names=[ast.alias(name="numpy", asname=None)])
        with self.assertRaises(BadImportError):
            self.cleaner._check_imports(node)

    def test_check_is_df_declaration_true(self):
        node = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="pd", ctx=ast.Load()),
                attr="DataFrame",
                ctx=ast.Load(),
            ),
            args=[],
            keywords=[],
        )
        node_ast = MagicMock()
        node_ast.value = node
        result = self.cleaner._check_is_df_declaration(node_ast)
        self.assertTrue(result)

    def test_check_is_df_declaration_false(self):
        node = ast.Call(func=ast.Name(id="list", ctx=ast.Load()), args=[], keywords=[])
        node_ast = MagicMock()
        node_ast.value = node
        result = self.cleaner._check_is_df_declaration(node_ast)
        self.assertFalse(result)

    def test_get_target_names_single(self):
        node = ast.Assign(
            targets=[ast.Name(id="df", ctx=ast.Store())],
            value=ast.Name(id="pd", ctx=ast.Load()),
        )
        target_names, is_slice, target = self.cleaner._get_target_names(node.targets)
        self.assertEqual(target_names, ["df"])
        self.assertFalse(is_slice)

    def test_check_direct_sql_func_def_exists_true(self):
        self.context.config.direct_sql = True
        node = ast.FunctionDef(
            name="execute_sql_query",
            args=ast.arguments(
                args=[],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[],
            ),
            body=[],
            decorator_list=[],
            returns=None,
        )
        result = self.cleaner._check_direct_sql_func_def_exists(node)
        self.assertTrue(result)

    def test_check_direct_sql_func_def_exists_false(self):
        self.context.config.direct_sql = False
        node = ast.FunctionDef(
            name="execute_sql_query",
            args=ast.arguments(
                args=[],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[],
            ),
            body=[],
            decorator_list=[],
            returns=None,
        )
        result = self.cleaner._check_direct_sql_func_def_exists(node)
        self.assertFalse(result)

    def test_replace_table_names_valid(self):
        sql_query = "SELECT * FROM my_table;"
        table_names = ["my_table"]
        allowed_table_names = {"my_table": "my_table"}
        result = self.cleaner._replace_table_names(
            sql_query, table_names, allowed_table_names
        )
        self.assertEqual(result, "SELECT * FROM my_table;")

    def test_replace_table_names_invalid(self):
        sql_query = "SELECT * FROM my_table;"
        table_names = ["my_table"]
        allowed_table_names = {}
        with self.assertRaises(MaliciousQueryError):
            self.cleaner._replace_table_names(
                sql_query, table_names, allowed_table_names
            )

    def test_clean_sql_query(self):
        sql_query = "SELECT * FROM my_table;"
        mock_dataframe = MagicMock(spec=object)
        mock_dataframe.name = "my_table"
        self.cleaner.context.dfs = [mock_dataframe]
        result = self.cleaner._clean_sql_query(sql_query)
        self.assertEqual(result, "SELECT * FROM my_table")

    def test_validate_and_make_table_name_case_sensitive(self):
        node = ast.Assign(
            targets=[ast.Name(id="query", ctx=ast.Store())],
            value=ast.Constant(value="SELECT * FROM my_table"),
        )
        mock_dataframe = MagicMock(spec=object)
        mock_dataframe.name = "my_table"
        self.cleaner.context.dfs = [mock_dataframe]
        updated_node = self.cleaner._validate_and_make_table_name_case_sensitive(node)
        self.assertEqual(updated_node.value.value, "SELECT * FROM my_table")

    def test_extract_fix_dataframe_redeclarations(self):
        node = ast.Assign(
            targets=[ast.Name(id="df", ctx=ast.Store())],
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="pd", ctx=ast.Load()),
                    attr="DataFrame",
                    ctx=ast.Load(),
                ),
                args=[],
                keywords=[],
            ),
        )
        self.cleaner.context.dfs = [self.sample_df]
        code_lines = [
            """df = pd.DataFrame({
                "country": ["United States", "United Kingdom", "Japan", "China"],
                "gdp": [
                    19294482071552,
                    2891615567872,
                    4380756541440,
                    14631844184064,
                ],
                "happiness_index": [6.94, 7.22, 5.87, 5.12],
            })"""
        ]
        additional_deps = []
        updated_node = self.cleaner.extract_fix_dataframe_redeclarations(
            node, code_lines, additional_deps
        )
        self.assertIsInstance(updated_node, ast.AST)


if __name__ == "__main__":
    unittest.main()
