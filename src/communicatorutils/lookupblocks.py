"""Onionr - Private P2P Communication.

Lookup new blocks with the communicator using a random connected peer
"""
from gevent import time

import logger
import onionrproofs
from onionrutils import stringvalidators, epoch
from communicator import peeraction, onlinepeers
from coredb.blockmetadb import get_block_list
from utils import reconstructhash
from onionrblocks import onionrblacklist
import onionrexceptions
import config
from etc import onionrvalues
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

blacklist = onionrblacklist.OnionrBlackList()


def lookup_blocks_from_communicator(comm_inst):
    logger.info('Looking up new blocks')
    tryAmount = 2
    newBlocks = ''
    # List of existing saved blocks
    existingBlocks = get_block_list()
    triedPeers = []  # list of peers we've tried this time around
    # Max amount of *new* block hashes to have in queue
    maxBacklog = 1560
    lastLookupTime = 0  # Last time we looked up a particular peer's list
    new_block_count = 0
    for i in range(tryAmount):
        # Defined here to reset it each time, time offset is added later
        listLookupCommand = 'getblocklist'
        if len(comm_inst.blockQueue) >= maxBacklog:
            break
        if not comm_inst.isOnline:
            break
        # check if disk allocation is used
        if comm_inst.storage_counter.is_full():
            logger.debug(
                'Not looking up new blocks due to maximum amount of disk used')
            break
        try:
            # select random online peer
            peer = onlinepeers.pick_online_peer(comm_inst)
        except onionrexceptions.OnlinePeerNeeded:
            time.sleep(1)
            continue
        # if we've already tried all the online peers this time around, stop
        if peer in triedPeers:
            if len(comm_inst.onlinePeers) == len(triedPeers):
                break
            else:
                continue
        triedPeers.append(peer)

        # Get the last time we looked up a peer's stamp,
        # to only fetch blocks since then.
        # Saved in memory only for privacy reasons
        try:
            lastLookupTime = comm_inst.dbTimestamps[peer]
        except KeyError:
            lastLookupTime = epoch.get_epoch() - \
                config.get("general.max_block_age",
                           onionrvalues.DEFAULT_EXPIRE)
        listLookupCommand += '?date=%s' % (lastLookupTime,)
        try:
            newBlocks = peeraction.peer_action(
                comm_inst,
                peer, listLookupCommand)  # get list of new block hashes
        except Exception as error:
            logger.warn(
                f'Could not get new blocks from {peer}.',
                error=error)
            newBlocks = False

        if newBlocks != False:  # noqa
            # if request was a success
            for i in newBlocks.split('\n'):
                if stringvalidators.validate_hash(i):
                    i = reconstructhash.reconstruct_hash(i)
                    # if newline seperated string is valid hash

                    # if block does not exist on disk + is not already in queue
                    if i not in existingBlocks:
                        if i not in comm_inst.blockQueue:
                            if onionrproofs.hashMeetsDifficulty(i) and \
                                 not blacklist.inBlacklist(i):
                                if len(comm_inst.blockQueue) <= 1000000:
                                    # add blocks to download queue
                                    comm_inst.blockQueue[i] = [peer]
                                    new_block_count += 1
                                    comm_inst.dbTimestamps[peer] = \
                                        epoch.get_rounded_epoch(roundS=60)
                        else:
                            if peer not in comm_inst.blockQueue[i]:
                                if len(comm_inst.blockQueue[i]) < 10:
                                    comm_inst.blockQueue[i].append(peer)
    if new_block_count > 0:
        block_string = ""
        if new_block_count > 1:
            block_string = "s"
        logger.info(
            f'Discovered {new_block_count} new block{block_string}',
            terminal=True)
        comm_inst.download_blocks_timer.count = \
            int(comm_inst.download_blocks_timer.frequency * 0.99)
    comm_inst.decrementThreadCount('lookup_blocks_from_communicator')
