"""
    Onionr - Private P2P Communication

    Prevent eval/exec and log it
"""
import base64

import logger
from utils import identifyhome
from onionrexceptions import ArbitraryCodeExec
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


def block_exec(event, info):
    """Prevent arbitrary code execution in eval/exec and log it"""
    # because libraries have stupid amounts of compile/exec/eval,
    # We have to use a whitelist where it can be tolerated
    whitelisted_code = [
                        'netrc.py',
                        '<werkzeug routing>',
                        'werkzeug/test.py',
                        'multiprocessing/popen_fork.py',
                        'multiprocessing/util.py',
                        'multiprocessing/connection.py',
                        'onionrutils/escapeansi.py'
                       ]
    home = identifyhome.identify_home()

    for source in whitelisted_code:
        if info[0].co_filename.endswith(source):
            return

    if info[0].co_filename.startswith(home + 'plugins/'):
        return

    code_b64 = base64.b64encode(info[0].co_code).decode()
    logger.warn('POSSIBLE EXPLOIT DETECTED, SEE LOGS', terminal=True)
    logger.warn('POSSIBLE EXPLOIT DETECTED: ' + info[0].co_filename)
    logger.warn('Prevented exec/eval. Report this with the sample below')
    logger.warn(f'{event} code in base64 format: {code_b64}')
    raise ArbitraryCodeExec("Arbitrary code (eval/exec) detected.")