"""Onionr - Private P2P Communication.

This file implements logic for performing requests to Onionr peers
"""
import streamedrequests
import logger
from onionrutils import epoch, basicrequests
from coredb import keydb
from . import onlinepeers
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


def peer_action(comm_inst, peer, action,
                returnHeaders=False, max_resp_size=5242880):
    """Perform a get request to a peer."""
    penalty_score = -10
    if len(peer) == 0:
        return False
    url = 'http://%s/%s' % (peer, action)

    try:
        ret_data = basicrequests.do_get_request(url, port=comm_inst.proxyPort,
                                                max_size=max_resp_size)
    except streamedrequests.exceptions.ResponseLimitReached:
        logger.warn(
            'Request failed due to max response size being overflowed',
            terminal=True)
        ret_data = False
        penalty_score = -100
    # if request failed, (error), mark peer offline
    if ret_data is False:
        try:
            comm_inst.getPeerProfileInstance(peer).addScore(penalty_score)
            onlinepeers.remove_online_peer(comm_inst, peer)
            keydb.transportinfo.set_address_info(
                peer, 'lastConnectAttempt', epoch.get_epoch())
            if action != 'ping' and not comm_inst.shutdown:
                logger.warn(f'Lost connection to {peer}', terminal=True)
                # Will only add a new peer to pool if needed
                onlinepeers.get_online_peers(comm_inst)
        except ValueError:
            pass
    else:
        peer_profile = comm_inst.getPeerProfileInstance(peer)
        peer_profile.update_connect_time()
        peer_profile.addScore(1)
    # If returnHeaders, returns tuple of data, headers.
    # If not, just data string
    return ret_data
