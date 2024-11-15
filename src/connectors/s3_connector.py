from pyspark.sql import DataFrame
from connector_interfaces import SourceConnector, SinkConnector
from decorators.logger_decorator import log_method  # Import logger decorator
from utils.logging_util import setup_logger

class S3Source(SourceConnector):
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
        bucket = self.config['bucket']
        file_path = self.config['file_path']
        access_key_id = self.config['access_key_id']
        secret_access_key = self.config['secret_access_key']
        region = self.config['region']

        self.logger.info(f"Reading from S3 bucket: {bucket}, file path: {file_path}, format: {self.file_format}")
        spark._jsc.hadoopConfiguration().set("fs.s3a.access.key", access_key_id)
        spark._jsc.hadoopConfiguration().set("fs.s3a.secret.key", secret_access_key)
        spark._jsc.hadoopConfiguration().set("fs.s3a.endpoint", f"s3.{region}.amazonaws.com")

        # Use the mapped read function based on the file format
        read_func = self.read_functions.get(self.file_format)
        if not read_func:
            raise ValueError(f"Unsupported file format: {self.file_format}")

        return read_func(f"s3a://{bucket}/{file_path}")

class S3Sink(SinkConnector):
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
        bucket = self.config['bucket']
        file_path = self.config['file_path']
        access_key_id = self.config['access_key_id']
        secret_access_key = self.config['secret_access_key']
        region = self.config['region']

        self.logger.info(f"Writing to S3 bucket: {bucket}, file path: {file_path}, format: {self.file_format}")
        spark._jsc.hadoopConfiguration().set("fs.s3a.access.key", access_key_id)
        spark._jsc.hadoopConfiguration().set("fs.s3a.secret.key", secret_access_key)
        spark._jsc.hadoopConfiguration().set("fs.s3a.endpoint", f"s3.{region}.amazonaws.com")

        # Use the mapped write function based on the file format
        write_func = self.write_functions.get(self.file_format)
        if not write_func:
            raise ValueError(f"Unsupported file format: {self.file_format}")

        write_func(df, f"s3a://{bucket}/{file_path}")
