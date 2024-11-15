# connectors/postgres_connector.py
from pyspark.sql import DataFrame
from connector_interfaces import SourceConnector, SinkConnector
from decorators.logger_decorator import log_method
from utils.logging_util import setup_logger

class PostgreSQLSource(SourceConnector):
    def __init__(self, config):
        super().__init__(config)
        self.logger = setup_logger(self.__class__.__name__)

    @log_method
    def read(self, spark) -> DataFrame:
        url = f"jdbc:postgresql://{self.config['host']}:{self.config['port']}/{self.config['database']}"
        properties = {
            "user": self.config['username'],
            "password": self.config['password']
        }

        self.logger.info(f"Reading from PostgreSQL database: {self.config['database']}")
        return spark.read.jdbc(url=url, table=self.config['database'], properties=properties)

class PostgreSQLSink(SinkConnector):
    def __init__(self, config):
        super().__init__(config)
        self.logger = setup_logger(self.__class__.__name__)

    @log_method
    def write(self, df: DataFrame):
        url = f"jdbc:postgresql://{self.config['host']}:{self.config['port']}/{self.config['database']}"
        properties = {
            "user": self.config['username'],
            "password": self.config['password']
        }

        self.logger.info(f"Writing to PostgreSQL database: {self.config['database']}")
        df.write.jdbc(url=url, table=self.config['database'], mode="overwrite", properties=properties)
