"""Onionr - Private P2P Communication.

Serialize various node information
"""
from gevent import sleep

from psutil import Process, WINDOWS
import ujson as json

from coredb import blockmetadb
from utils.sizeutils import size, human_size
from utils.identifyhome import identify_home
import communicator
"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


class SerializedData:
    def __init__(self):
        """
        Serialized data is in JSON format:
        {
            'success': bool,
            'foo': 'bar',
            etc
        }
        """

    def get_stats(self):
        """Return statistics about our node"""
        stats = {}
        proc = Process()

        def get_open_files():
            if WINDOWS: return proc.num_handles()
            return proc.num_fds()

        try:
            self._too_many
        except AttributeError:
            sleep(1)
        comm_inst = self._too_many.get(communicator.OnionrCommunicatorDaemon, args=(self._too_many,))
        connected = []
        [connected.append(x) for x in comm_inst.onlinePeers if x not in connected]
        stats['uptime'] = comm_inst.getUptime()
        stats['connectedNodes'] = '\n'.join(connected)
        stats['blockCount'] = len(blockmetadb.get_block_list())
        stats['blockQueueCount'] = len(comm_inst.blockQueue)
        stats['threads'] = proc.num_threads()
        stats['ramPercent'] = proc.memory_percent()
        stats['fd'] = get_open_files()
        stats['diskUsage'] = human_size(size(identify_home()))
        return json.dumps(stats)
