import os
import dotenv

class Environment:
    VALID_VARIABLES = [
        "SECRETS_DIR", "OUTPUT_DIR", "LOG_DIR", "DATA_DIR", "TEMP_DIR",
        "VENV_DIR", "SRC_DIR", "TESTS_DIR", "INSTALL_DIR" "ASSETS_DIR",
        "USR_OUTPUT_DIR", "USR_LOG_DIR", "USR_DATA_DIR" "SERVICE_USERGROUP",
        "PYTHON_BINARY", "OPENAI_API_KEY",
    ]
    #region Getters

    @staticmethod
    def load_environment():
        dotenv.load_dotenv('.env')

    @staticmethod
    def check_variable_name(variable_name: str):
        normalized_var_name = variable_name.upper().replace(' ', '_').replace('-', '_')
        if normalized_var_name not in Environment.VALID_VARIABLES:
            raise ValueError(
                f"Invalid variable name: '{variable_name}'. Must be one of {', '.join(Environment.VALID_VARIABLES)}")

    @staticmethod
    def get_environment_variable(variable_name: str) -> str:
        Environment.check_variable_name(variable_name)
        Environment.load_environment()
        return os.getenv(variable_name)

    @staticmethod
    def set_environment_variable(variable_name: str, value: str):
        Environment.check_variable_name(variable_name)
        dotenv.set_key('.env', variable_name, value)
        Environment.load_environment()
