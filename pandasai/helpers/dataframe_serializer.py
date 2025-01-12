import json
from enum import Enum

import pandas as pd


class DataframeSerializerType(Enum):
    JSON = 1
    YML = 2
    CSV = 3
    SQL = 4


class DataframeSerializer:
    def __init__(self) -> None:
        pass

    def serialize(
        self,
        df: pd.DataFrame,
        extras: dict = None,
        type_: DataframeSerializerType = DataframeSerializerType.YML,
    ) -> str:
        if type_ == DataframeSerializerType.YML:
            return self.convert_df_to_yml(df, extras)
        elif type_ == DataframeSerializerType.JSON:
            return self.convert_df_to_json_str(df, extras)
        elif type_ == DataframeSerializerType.SQL:
            return self.convert_df_sql_connector_to_str(df, extras)
        else:
            return self.convert_df_to_csv(df, extras)

    def convert_df_to_csv(self, df: pd.DataFrame, extras: dict) -> str:
        """
        Convert df to csv like format where csv is wrapped inside <dataframe></dataframe>
        Args:
            df (pd.DataFrame): PandaAI dataframe or dataframe
            extras (dict, optional): expect index to exists

        Returns:
            str: dataframe stringify
        """
        dataframe_info = "<dataframe"

        # Add name attribute if available
        if df.name is not None:
            dataframe_info += f' name="{df.name}"'

        # Add description attribute if available
        if df.description is not None:
            dataframe_info += f' description="{df.description}"'

        dataframe_info += ">"

        # Add dataframe details
        dataframe_info += f"\ndfs[{extras['index']}]:{df.rows_count}x{df.columns_count}\n{df.head().to_csv(index=False)}"

        # Close the dataframe tag
        dataframe_info += "</dataframe>\n"

        return dataframe_info

    def convert_df_sql_connector_to_str(
        self, df: pd.DataFrame, extras: dict = None
    ) -> str:
        """
        Convert df to csv like format where csv is wrapped inside <table></table>
        Args:
            df (pd.DataFrame): PandaAI dataframe or dataframe
            extras (dict, optional): expect index to exists

        Returns:
            str: dataframe stringify
        """
        table_description_tag = (
            f' description="{df.description}"' if df.description is not None else ""
        )
        table_head_tag = f'<table name="{df.name}"{table_description_tag}>'
        return f"{table_head_tag}\n{df.get_head().to_csv()}\n</table>"

    def convert_df_to_json(self, df: pd.DataFrame, extras: dict) -> dict:
        """
        Convert df to json dictionary and return json
        Args:
            df (pd.DataFrame): PandaAI dataframe or dataframe
            extras (dict, optional): expect index to exists

        Returns:
            str: dataframe json
        """

        # Create a dictionary representing the data structure
        df_info = {
            "name": df.name,
            "description": None,
            "type": df.type,
        }
        # Add DataFrame details to the result
        data = {
            "rows": df.rows_count,
            "columns": df.columns_count,
            "schema": {"fields": []},
        }

        # Iterate over DataFrame columns
        df_head = df.get_head()
        for col_name, col_dtype in df_head.dtypes.items():
            col_info = {
                "name": col_name,
                "type": str(col_dtype),
            }

            data["schema"]["fields"].append(col_info)

        result = df_info | data

        return result

    def convert_df_to_json_str(self, df: pd.DataFrame, extras: dict) -> str:
        """
        Convert df to json and return it as string
        Args:
            df (pd.DataFrame): PandaAI dataframe or dataframe
            extras (dict, optional): expect index to exists

        Returns:
            str: dataframe stringify
        """
        return json.dumps(self.convert_df_to_json(df, extras))

    def convert_df_to_yml(self, df: pd.DataFrame, extras: dict) -> str:
        json_df = self.convert_df_to_json(df, extras)

        import yaml

        yml_str = yaml.dump(json_df, sort_keys=False, allow_unicode=True)
        return f"<table>\n{yml_str}\n</table>\n"
