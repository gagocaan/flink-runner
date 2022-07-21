import logging

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions


def run():
    pipeline_options = PipelineOptions(
        runner="FlinkRunner",
        flink_master="localhost:8081",
        environment_type="EXTERNAL",
        environment_config="localhost:50000",
    )

    with beam.Pipeline(options=pipeline_options) as pipeline:
        _ = pipeline | "Create" >> beam.Create(["Esto es un texto de prueba."])
        _ | "Write" >> beam.io.WriteToText(
            file_path_prefix="output_file",
            file_name_suffix=".txt",
            num_shards=1,
            shard_name_template="",
        )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    run()
