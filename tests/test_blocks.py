#!/usr/bin/env python3
import sys, os
sys.path.append(".")
sys.path.append("src/")
import unittest, uuid, hashlib

TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
print("Test directory:", TEST_DIR)
os.environ["ONIONR_HOME"] = TEST_DIR

import onionrblocks
import onionrstorage
from utils import createdirs
from onionrutils import bytesconverter
import onionrcrypto
from onionrblocks import onionrblockapi

def setup_test():
    TEST_DIR = 'testdata/%s-%s' % (uuid.uuid4(), os.path.basename(__file__)) + '/'
    print("Test directory:", TEST_DIR)
    os.environ["ONIONR_HOME"] = TEST_DIR
    createdirs.create_dirs()

class OnionrBlockTests(unittest.TestCase):
    def test_plaintext_insert(self):
        setup_test()
        message = 'hello world'
        bl = onionrblocks.insert(message)
        self.assertTrue(bl.startswith('0'))
        self.assertIn(bytesconverter.str_to_bytes(message), onionrstorage.getData(bl))

    def test_encrypted_insert(self):
        setup_test()
        message = 'hello world2'
        bl = onionrblocks.insert(message, asymPeer=onionrcrypto.pub_key)
        self.assertIn(bytesconverter.str_to_bytes(message), onionrblockapi.Block(bl, decrypt=True).bcontent)

unittest.main()
