"""
Onionr - Private P2P Communication.

Use a communicator instance to announce
our transport address to connected nodes
"""
import logger
from onionrutils import basicrequests
from utils import gettransports
from netcontroller import NetController
from communicator import onlinepeers
from coredb import keydb
import onionrexceptions
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


def announce_node(daemon):
    """Announce our node to our peers."""
    ret_data = False

    # Do not let announceCache get too large
    if len(daemon.announceCache) >= 10000:
        daemon.announceCache.popitem()

    if daemon.config.get('general.security_level', 0) == 0:
        # Announce to random online peers
        for i in daemon.onlinePeers:
            if i not in daemon.announceCache and\
                    i not in daemon.announceProgress:
                peer = i
                break
        else:
            try:
                peer = onlinepeers.pick_online_peer(daemon)
            except onionrexceptions.OnlinePeerNeeded:
                peer = ""

        try:
            ourID = gettransports.get()[0]
            if not peer:
                raise onionrexceptions.OnlinePeerNeeded
        except (IndexError, onionrexceptions.OnlinePeerNeeded):
            pass
        else:
            url = 'http://' + peer + '/announce'
            data = {'node': ourID}

            logger.info('Announcing node to ' + url)
            if basicrequests.do_post_request(
                    url,
                    data,
                    port=daemon.shared_state.get(NetController).socksPort)\
                    == 'Success':
                logger.info('Successfully introduced node to ' + peer,
                            terminal=True)
                ret_data = True
                keydb.transportinfo.set_address_info(peer, 'introduced', 1)

    daemon.decrementThreadCount('announce_node')
    return ret_data
