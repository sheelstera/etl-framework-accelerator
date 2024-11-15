# connectors/mongo_connector.py
from pyspark.sql import DataFrame
from connector_interfaces import SourceConnector, SinkConnector
from decorators.logger_decorator import log_method
from utils.logging_util import setup_logger

class MongoDBSource(SourceConnector):
    def __init__(self, config):
        super().__init__(config)
        self.logger = setup_logger(self.__class__.__name__)

    @log_method
    def read(self, spark) -> DataFrame:
        uri = self.config['uri']
        database = self.config['database']
        collection = self.config.get('collection', database)

        self.logger.info(f"Reading from MongoDB collection: {collection}")
        return spark.read.format("mongo").option("uri", uri).option("database", database).option("collection", collection).load()

class MongoDBSink(SinkConnector):
    def __init__(self, config):
        super().__init__(config)
        self.logger = setup_logger(self.__class__.__name__)

    @log_method
    def write(self, df: DataFrame):
        uri = self.config['uri']
        database = self.config['database']
        collection = self.config.get('collection', database)

        self.logger.info(f"Writing to MongoDB collection: {collection}")
        df.write.format("mongo").option("uri", uri).option("database", database).option("collection", collection).mode("overwrite").save()
