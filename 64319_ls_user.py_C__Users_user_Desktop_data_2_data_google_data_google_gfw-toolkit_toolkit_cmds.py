#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
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

"""Simple ls (show) of a domain user.

Invoke with --long_list to view all user fields.

Tool to show usage of Admin SDK Directory APIs.

APIs Used:
  Admin SDK Directory API: user management
"""

import sys

# setup_path required to allow imports from component dirs (e.g. utils)
# and lib (where the OAuth and Google API Python Client modules reside).
import setup_path  # pylint: disable=unused-import,g-bad-import-order

from admin_sdk_directory_api import users_api
from plus_domains_api import people_api
from utils import admin_api_tool_errors
from utils import auth_helper
from utils import common_flags
from utils import log_utils
from utils import validators


def AddFlags(arg_parser):
  """Handle command line flags unique to this script.

  Args:
    arg_parser: object from argparse.ArgumentParser() to accumulate flags.
  """
  common_flags.DefineAppsDomainFlagWithDefault(arg_parser)
  common_flags.DefineVerboseFlagWithDefaultFalse(arg_parser)

  arg_parser.add_argument(
      '--long_list', '-l', action='store_true', default=False,
      help='Show more columns of output.')
  arg_parser.add_argument(
      '--plus_domains', '-p', action='store_true', default=False,
      help='Show output from Google Plus Domains Profile.')
  arg_parser.add_argument(
      '--user_email', '-u', required=True,
      help='User email address [REQUIRED].',
      type=validators.EmailValidatorType())


def main(argv):
  """A script to test Admin SDK Directory APIs: ls (show) user."""
  flags = common_flags.ParseFlags(argv, 'List info about a domain user.',
                                  AddFlags)
  http = auth_helper.GetAuthorizedHttp(flags)
  if flags.plus_domains:
    user_api = people_api.PlusDomains(http)
  else:
    user_api = users_api.UsersApiWrapper(http)
  try:
    user_api.PrintDomainUser(flags.user_email, flags.long_list)
  except admin_api_tool_errors.AdminAPIToolUserError as e:
    # Could not ls user. Details provided by api wrapper in the e string.
    log_utils.LogError('Unable to locate user %s.' % flags.user_email, e)
    sys.exit(1)


if __name__ == '__main__':
  main(sys.argv[1:])
