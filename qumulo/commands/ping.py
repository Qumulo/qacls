# Copyright (c) 2013 Qumulo, Inc.
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

import qumulo.lib.auth
import qumulo.lib.opts
import qumulo.rest.ping as ping

class PingDisablePostCommand(qumulo.lib.opts.Subcommand):
    NAME = "ping_disable"
    DESCRIPTION = "Disable pings and ping timeouts"

    @staticmethod
    def main(conninfo, credentials, _args):
        ping.disable_ping(conninfo, credentials)
