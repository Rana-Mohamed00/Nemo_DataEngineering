import logging
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

from ApacheBeam.config import TAG_CLEAN, TAG_DEAD_LETTER
from ApacheBeam.validation import ValidateAndCleanF1DoFn

from Database.database import insert_cleansed_data, insert_dead_letter


def run_pipeline(input_file_path):
    pipeline_options = PipelineOptions()

    with beam.Pipeline(options=pipeline_options) as pipeline:
        raw_lines = (
            pipeline
            | 'Read CSV File' >> beam.io.ReadFromText(input_file_path)
        )

        validated_results = (
            raw_lines
            | 'Validate F1 Data' >> beam.ParDo(
                ValidateAndCleanF1DoFn()
            ).with_outputs(
                TAG_CLEAN,
                TAG_DEAD_LETTER
            )
        )

        clean_stream = validated_results[TAG_CLEAN]
        dlq_stream = validated_results[TAG_DEAD_LETTER]

        (
            clean_stream
            | 'Batch Clean Records' >> beam.BatchElements(min_batch_size=500, max_batch_size=2000)
            | 'Save Clean Records to DB' >> beam.Map(insert_cleansed_data)
        )

        (
            dlq_stream
            | 'Batch DLQ Records' >> beam.BatchElements(min_batch_size=500, max_batch_size=2000)
            | 'Save DLQ Records to DB' >> beam.Map(insert_dead_letter)
        )