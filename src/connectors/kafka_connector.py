# connectors/kafka_connector.py
from pyspark.sql import DataFrame
from connector_interfaces import SourceConnector, SinkConnector
from decorators.logger_decorator import log_method
from utils.logging_util import setup_logger

class KafkaSource(SourceConnector):
    def __init__(self, config):
        super().__init__(config)
        self.logger = setup_logger(self.__class__.__name__)

    @log_method
    def read(self, spark) -> DataFrame:
        kafka_options = {
            "kafka.bootstrap.servers": self.config['bootstrap_servers'],
            "subscribe": self.config['topic'],
            "startingOffsets": self.config['offset']
        }

        self.logger.info(f"Reading from Kafka topic: {self.config['topic']}")
        return spark.read.format("kafka").options(**kafka_options).load()

class KafkaSink(SinkConnector):
    def __init__(self, config):
        super().__init__(config)
        self.logger = setup_logger(self.__class__.__name__)

    @log_method
    def write(self, df: DataFrame):
        kafka_options = {
            "kafka.bootstrap.servers": self.config['bootstrap_servers'],
            "topic": self.config['topic']
        }

        self.logger.info(f"Writing to Kafka topic: {self.config['topic']}")
        df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
            .write \
            .format("kafka") \
            .options(**kafka_options) \
            .save()
