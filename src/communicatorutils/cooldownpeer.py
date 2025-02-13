"""Onionr - Private P2P Communication.

Select random online peer in a communicator instance and have them "cool down"
"""
from onionrutils import epoch
from communicator import onlinepeers
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


def cooldown_peer(comm_inst):
    """Randomly add an online peer to cooldown, so we can connect a new one."""
    config = comm_inst.config
    online_peer_amount = len(comm_inst.onlinePeers)
    minTime = 300
    cooldown_time = 600
    to_cool = ''
    tempConnectTimes = dict(comm_inst.connectTimes)

    # Remove peers from cooldown that have been there long enough
    tempCooldown = dict(comm_inst.cooldownPeer)
    for peer in tempCooldown:
        if (epoch.get_epoch() - tempCooldown[peer]) >= cooldown_time:
            del comm_inst.cooldownPeer[peer]

    # Cool down a peer, if we have max connections alive for long enough
    if online_peer_amount >= config.get('peers.max_connect', 10, save=True):
        finding = True

        while finding:
            try:
                to_cool = min(tempConnectTimes, key=tempConnectTimes.get)
                if (epoch.get_epoch() - tempConnectTimes[to_cool]) < minTime:
                    del tempConnectTimes[to_cool]
                else:
                    finding = False
            except ValueError:
                break
        else:
            onlinepeers.remove_online_peer(comm_inst, to_cool)
            comm_inst.cooldownPeer[to_cool] = epoch.get_epoch()

    comm_inst.decrementThreadCount('cooldown_peer')
