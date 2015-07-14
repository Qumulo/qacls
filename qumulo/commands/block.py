# Copyright (c) 2015 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import qumulo.lib.opts
import qumulo.lib.util
import qumulo.rest.block as block

class GetBlockSettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = "block_settings_get"
    DESCRIPTION = "Return block settings for a node."

    @staticmethod
    def main(conninfo, credentials, _args):
        print block.get_block_settings(conninfo, credentials)

class SetBlockSettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = "block_settings_set"
    DESCRIPTION = "Set block settings for a node."

    @staticmethod
    def options(parser):
        parser.add_argument("--expiration-pct",
            help="Expiration percentage value.", type=int)
        parser.add_argument("--max-checkpoints",
            help="Maximum number of checkpoints per virtual disk.", type=int)
        parser.add_argument("--max-expires",
            help="Maximum number of expires per virtual disk.", type=int)
        parser.add_argument("--wants-checkpoint-after", type=int,
            help="WAL length after which a bstore wants a checkpoint.")
        parser.add_argument("--needs-checkpoint-after", type=int,
            help="WAL length after which a bstore needs a checkpoint.")

    @staticmethod
    def main(conninfo, credentials, args):
        config = {}

        for field in ['expiration_pct', 'max_checkpoints', 'max_expires',
                      'wants_checkpoint_after', 'needs_checkpoint_after']:
            value = getattr(args, field)
            if value is not None:
                config[field] = value

        if not config:
            raise ValueError('No options supplied')

        print block.set_block_settings(conninfo, credentials, **config)
