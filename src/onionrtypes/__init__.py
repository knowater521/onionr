from typing import NewType

UserID = NewType('UserID', str)
UserIDSecretKey = NewType('UserIDSecretKey', str)

LANIP = NewType('LANIP', 'str')

DeterministicKeyPassphrase = NewType('DeterministicKeyPassphrase', str)

BlockHash = NewType('BlockHash', str)

OnboardingConfig = NewType('OnboardingConfig', str)

# JSON serializable string. e.g. no raw bytes
JSONSerializable = NewType('JSONSerializable', str)

# Return value of some functions or methods, denoting operation success
# Do not use for new code
BooleanSuccessState = NewType('BooleanSuccessState', bool)

OnionAddressString = NewType('OnionAddressString', str)
