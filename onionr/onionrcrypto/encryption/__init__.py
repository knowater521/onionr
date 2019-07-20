import nacl.encoding, nacl.public, nacl.signing
from .. import getourkeypair
import unpaddedbase32
pair = getourkeypair.get_keypair()
our_pub_key = pair[0]
our_priv_key = pair[1]

def pub_key_encrypt(data, pubkey, encodedData=False):
    '''Encrypt to a public key (Curve25519, taken from base32 Ed25519 pubkey)'''
    pubkey = unpaddedbase32.repad(bytesconverter.str_to_bytes(pubkey))
    retVal = ''
    box = None
    data = bytesconverter.str_to_bytes(data)
    
    pubkey = nacl.signing.VerifyKey(pubkey, encoder=nacl.encoding.Base32Encoder()).to_curve25519_public_key()

    if encodedData:
        encoding = nacl.encoding.Base64Encoder
    else:
        encoding = nacl.encoding.RawEncoder
    
    box = nacl.public.SealedBox(pubkey)
    retVal = box.encrypt(data, encoder=encoding)

    return retVal

def pub_key_decrypt(data, pubkey='', privkey='', encodedData=False):
    '''pubkey decrypt (Curve25519, taken from Ed25519 pubkey)'''
    decrypted = False
    if encodedData:
        encoding = nacl.encoding.Base64Encoder
    else:
        encoding = nacl.encoding.RawEncoder
    if privkey == '':
        privkey = our_priv_key
    ownKey = nacl.signing.SigningKey(seed=privkey, encoder=nacl.encoding.Base32Encoder()).to_curve25519_private_key()

    if stringvalidators.validate_pub_key(privkey):
        privkey = nacl.signing.SigningKey(seed=privkey, encoder=nacl.encoding.Base32Encoder()).to_curve25519_private_key()
        anonBox = nacl.public.SealedBox(privkey)
    else:
        anonBox = nacl.public.SealedBox(ownKey)
    decrypted = anonBox.decrypt(data, encoder=encoding)
    return decrypted