"""Onionr - Private P2P Communication.

Create blocks with the client api server
"""
import ujson as json
import threading

from flask import Blueprint, Response, request, g
import onionrblocks
from onionrcrypto import hashers
from onionrutils import bytesconverter
from onionrutils import mnemonickeys
from onionrtypes import JSONSerializable

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
ib = Blueprint('insertblock', __name__)


@ib.route('/insertblock', methods=['POST'])
def client_api_insert_block():
    encrypt: bool = False
    insert_data: JSONSerializable = request.get_json(force=True)
    message = insert_data['message']
    message_hash = bytesconverter.bytes_to_str(hashers.sha3_hash(message))

    # Detect if message (block body) is not specified
    if type(message) is None:
        return 'failure due to unspecified message', 400

    # Detect if block with same message is already being inserted
    if message_hash in g.too_many.get_by_string(
            "OnionrCommunicatorDaemon").generating_blocks:
        return 'failure due to duplicate insert', 400
    else:
        g.too_many.get_by_string(
            "OnionrCommunicatorDaemon").generating_blocks.append(message_hash)

    encrypt_type = ''
    sign = True
    meta = {}
    to = ''
    try:
        if insert_data['encrypt']:
            to = insert_data['to'].strip()
            if "-" in to:
                to = mnemonickeys.get_base32(to)
            encrypt_type = 'asym'
    except KeyError:
        pass
    try:
        if not insert_data['sign']:
            sign = False
    except KeyError:
        pass
    try:
        bType = insert_data['type']
    except KeyError:
        bType = 'bin'
    try:
        meta = json.loads(insert_data['meta'])
    except KeyError:
        pass

    try:
        # The setting in the UI is for if forward secrecy is enabled, not disabled
        disable_forward_secrecy = not insert_data['forward']
    except KeyError:
        disable_forward_secrecy = False

    threading.Thread(
        target=onionrblocks.insert, args=(message,),
        kwargs={'header': bType, 'encryptType': encrypt_type,
                'sign': sign, 'asymPeer': to, 'meta': meta,
                'disableForward': disable_forward_secrecy}).start()
    return Response('success')
