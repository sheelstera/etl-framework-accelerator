from pyspark.sql import DataFrame

# Source Connector Interface
class SourceConnector:
    def __init__(self, config: dict):
        self.config = config

    def read(self, spark) -> DataFrame:
        """Reads data from the source and returns a Spark DataFrame"""
        raise NotImplementedError("The 'read' method must be implemented by subclasses")

# Sink Connector Interface
class SinkConnector:
    def __init__(self, config: dict):
        self.config = config

    def write(self, df: DataFrame):
        """Writes the DataFrame to the sink"""
        raise NotImplementedError("The 'write' method must be implemented by subclasses")
