import importlib

def get_connector(module_name, class_name, config):
    """Dynamically load the connector class based on module and class name"""
    module = importlib.import_module(module_name)
    connector_class = getattr(module, class_name)
    return connector_class(config)
