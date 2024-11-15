from pyspark.sql import DataFrame
from connector_interfaces import SourceConnector, SinkConnector
from decorators.logger_decorator import log_method  # Import logger decorator
from utils.logging_util import setup_logger

class AdlsSource(SourceConnector):
    def __init__(self, config):
        super().__init__(config)
        self.logger = setup_logger(self.__class__.__name__)
        self.file_format = config.get('format', 'csv')  # Default to CSV if not specified

        # Mapping of file formats to read functions
        self.read_functions = {
            'csv': lambda path: spark.read.csv(path, header=True),
            'tsv': lambda path: spark.read.csv(path, sep='\t', header=True),
            'parquet': lambda path: spark.read.parquet(path),
            'json': lambda path: spark.read.json(path)
        }

    @log_method
    def read(self, spark) -> DataFrame:
        abfss_path = self.config['abfss_path']
        access_key = self.config.get('access_key', '')

        self.logger.info(f"Reading from ADLS with path: {abfss_path}, format: {self.file_format}")
        spark.conf.set(f"fs.azure.account.key.{abfss_path.split('@')[1]}", access_key)

        # Use the mapped read function based on the file format
        read_func = self.read_functions.get(self.file_format)
        if not read_func:
            raise ValueError(f"Unsupported file format: {self.file_format}")

        return read_func(abfss_path)

class AdlsSink(SinkConnector):
    def __init__(self, config):
        super().__init__(config)
        self.logger = setup_logger(self.__class__.__name__)
        self.file_format = config.get('format', 'csv')  # Default to CSV if not specified

        # Mapping of file formats to write functions
        self.write_functions = {
            'csv': lambda df, path: df.write.csv(path, mode="overwrite", header=True),
            'tsv': lambda df, path: df.write.csv(path, mode="overwrite", sep='\t', header=True),
            'parquet': lambda df, path: df.write.parquet(path, mode="overwrite"),
            'json': lambda df, path: df.write.json(path, mode="overwrite")
        }

    @log_method
    def write(self, df: DataFrame):
        abfss_path = self.config['abfss_path']
        access_key = self.config.get('access_key', '')

        self.logger.info(f"Writing to ADLS with path: {abfss_path}, format: {self.file_format}")
        spark.conf.set(f"fs.azure.account.key.{abfss_path.split('@')[1]}", access_key)

        # Use the mapped write function based on the file format
        write_func = self.write_functions.get(self.file_format)
        if not write_func:
            raise ValueError(f"Unsupported file format: {self.file_format}")

        write_func(df, abfss_path)
