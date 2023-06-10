# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A workflow that writes to a BigQuery table with nested and repeated fields.

Demonstrates how to build a bigquery.TableSchema object with nested and repeated
fields. Also, shows how to generate data to be written to a BigQuery table with
nested and repeated fields.
"""

from __future__ import absolute_import

import argparse
import logging

import google.cloud.dataflow as df


def run(argv=None):
  """Run the workflow."""
  parser = argparse.ArgumentParser()

  parser.add_argument(
      '--output',
      required=True,
      help=
      ('Output BigQuery table for results specified as: PROJECT:DATASET.TABLE '
       'or DATASET.TABLE.'))
  known_args, pipeline_args = parser.parse_known_args(argv)

  p = df.Pipeline(argv=pipeline_args)

  from google.cloud.dataflow.internal.clients import bigquery  # pylint: disable=g-import-not-at-top

  table_schema = bigquery.TableSchema()

  # Fields that use standard types.
  kind_schema = bigquery.TableFieldSchema()
  kind_schema.name = 'kind'
  kind_schema.type = 'string'
  kind_schema.mode = 'nullable'
  table_schema.fields.append(kind_schema)

  full_name_schema = bigquery.TableFieldSchema()
  full_name_schema.name = 'fullName'
  full_name_schema.type = 'string'
  full_name_schema.mode = 'required'
  table_schema.fields.append(full_name_schema)

  age_schema = bigquery.TableFieldSchema()
  age_schema.name = 'age'
  age_schema.type = 'integer'
  age_schema.mode = 'nullable'
  table_schema.fields.append(age_schema)

  gender_schema = bigquery.TableFieldSchema()
  gender_schema.name = 'gender'
  gender_schema.type = 'string'
  gender_schema.mode = 'nullable'
  table_schema.fields.append(gender_schema)

  # A nested field
  phone_number_schema = bigquery.TableFieldSchema()
  phone_number_schema.name = 'phoneNumber'
  phone_number_schema.type = 'record'
  phone_number_schema.mode = 'nullable'

  area_code = bigquery.TableFieldSchema()
  area_code.name = 'areaCode'
  area_code.type = 'integer'
  area_code.mode = 'nullable'
  phone_number_schema.fields.append(area_code)

  number = bigquery.TableFieldSchema()
  number.name = 'number'
  number.type = 'integer'
  number.mode = 'nullable'
  phone_number_schema.fields.append(number)
  table_schema.fields.append(phone_number_schema)

  # A repeated field.
  children_schema = bigquery.TableFieldSchema()
  children_schema.name = 'children'
  children_schema.type = 'string'
  children_schema.mode = 'repeated'
  table_schema.fields.append(children_schema)

  def create_random_record(record_id):
    return {'kind': 'kind' + record_id, 'fullName': 'fullName'+record_id,
            'age': int(record_id) * 10, 'gender': 'male',
            'phoneNumber': {
                'areaCode': int(record_id) * 100,
                'number': int(record_id) * 100000},
            'children': ['child' + record_id + '1',
                         'child' + record_id + '2',
                         'child' + record_id + '3']
           }

  # pylint: disable=expression-not-assigned
  record_ids = p | df.Create('CreateIDs', ['1', '2', '3', '4', '5'])
  records = record_ids | df.Map('CreateRecords', create_random_record)
  records | df.io.Write(
      'write',
      df.io.BigQuerySink(
          known_args.output,
          schema=table_schema,
          create_disposition=df.io.BigQueryDisposition.CREATE_IF_NEEDED,
          write_disposition=df.io.BigQueryDisposition.WRITE_TRUNCATE))

  # Run the pipeline (all operations are deferred until run() is called).
  p.run()


if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()
