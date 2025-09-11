'''
    __init__.py
    Enables to create the required depedencies of the library.
    To add a function or class tap the following line:
        from aerodiode.name_file import name_function/name_class
'''

#DO NOT MODIFY THIS PART
from aerodiode.aerodiode import Aerodiode
from aerodiode.aerodiode import Status
from aerodiode.aerodiode import StatusError
from aerodiode.aerodiode import ChecksumError
from aerodiode.aerodiode import ProtocolError
from aerodiode.aerodiode import ConnectionFailure
from aerodiode.aerodiode import ProtocolVersionNotSupported
#TO MODIFY according the client needs
from aerodiode.shaper import Shaper
from aerodiode.mmd  import Mmd
from aerodiode.pdmv3 import Pdmv3
from aerodiode.pdmv3_cw import Pdmv3_cw
from aerodiode.tombak import Tombak
from aerodiode.pdmv5 import Pdmv5
from aerodiode.pdmv5_cw import Pdmv5_cw
from aerodiode.central import Central
