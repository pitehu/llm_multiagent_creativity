# base_model_service.py
class BaseModelService:
    """
    Abstract base class for model services.
    All model services must implement the `generate_response` method.
    """
    def generate_response(self, messages, model=None, temperature=0.7):
        """
        Generates a response using the corresponding model.
        This method must be implemented in subclasses.
        """
        raise NotImplementedError("Subclasses must implement generate_response method")

    def parse_response(self, messages, model=None, response_model=None):
        """
        Parses a response (if applicable). Default implementation returns None.
        """
        return None
