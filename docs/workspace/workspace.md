# Workspace

Workspace provides a way to chat with your dataset seamless without the need to create dataframes again and again. You need PandasAI key to use Workspace. You can create an api key by following below steps:

1. Go to https://domer.ai and sign up
2. From settings go to API keys and copy the api key
3. Set environment variable like os.environ['PANDASAI_API_KEY'] = '$2a$10$flb7....'

## Example

```python
import os

from pandasai.workspace import Workspace


os.environ["PANDASAI_API_KEY"] = (
    "$2a$10$/4x9CVetluLt2R***************"
)


workspace = Workspace("employees-data")

workspace.push(employees_df, "employees")

workspace.chat("return number or employees")
```
