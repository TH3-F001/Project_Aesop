import json

class JsonConverter:
    """
    A static service class for handling JSON operations.
    """

    @staticmethod
    def dict_to_json(data_dict: dict) -> str:
        """
        Converts a dictionary to a JSON string.

        Args:
            data_dict (dict): The dictionary to convert.

        Returns:
            str: The JSON string representation of the dictionary.
        """
        try:
            return json.dumps(data_dict, indent=4)
        except TypeError as e:
            raise ValueError(f"Error converting dictionary to JSON: {e}")

    @staticmethod
    def json_to_dict(json_string: str) -> dict:
        """
        Converts a JSON string to a dictionary.

        Args:
            json_string (str): The JSON string to convert.

        Returns:
            dict: The dictionary representation of the JSON string.
        """
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON to dictionary: {e}")

    @staticmethod
    def json_to_string(json_obj: dict) -> str:
        """
        Converts a JSON object (dictionary) to a stringified JSON format.
        Args:
            json_obj (dict): The JSON object to stringify.
        Returns:
            str: The string representation of the JSON object.
        """
        try:
            return json.dumps(json_obj, indent=4)
        except TypeError as e:
            raise ValueError(f"Error stringifying JSON object: {e}")
