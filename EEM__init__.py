[guestshell@guestshell eem]$ cat __init__.py

'''
------------------------------------------------------------------
            __init__.py -- EEM Python Package init routines

            December 2016, Anbalagan V

            Copyright (c) 2016-2020 by Cisco Systems, Inc.
            All rights reserved.
------------------------------------------------------------------
'''

__version__ = '1.0.0'

from ._eem  import action_syslog
from ._eem  import action_snmp_trap
from ._eem  import action_reload
from ._eem  import action_switch
from ._eem  import action_track_read
from ._eem  import action_track_set
from ._eem  import action_export_to_telemetry

from ._eem  import cli_open
from ._eem  import cli_close
from ._eem  import cli_run
from ._eem  import cli_exec
from ._eem  import cli_read
from ._eem  import cli_read_line
from ._eem  import cli_read_drain
from ._eem  import cli_read_pattern
from ._eem  import cli_write
from ._eem  import cli_run_interactive
from ._eem  import cli_get_ttyname

from ._eem  import event_publish

from ._eem  import event_reqinfo
from ._eem  import event_reqinfo_multi
from ._eem  import env_reqinfo
from ._eem  import get_env_var
from ._eem  import get_event_var

try :
     env_reqinfo()

except :
     print ("Please note, this package[eem] is ONLY for EEM Python Scripts")
