#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Created on 18.10.2018
#
# @author: Dirk Osswald
'''
Perform a cycle of outside gripping, releasing, inside gripping releasing with a BKS gripper (like EGI/EGU/EGK)|n
|n
Example usage:|n
-  %(prog)s -H 10.49.57.13
'''


import os.path
import pyschunk.tools.mylogger
from bkstools.bks_lib.bks_base import keep_communication_alive_sleep
from bkstools.bks_lib.bks_module import BKSModule
from bkstools.bks_lib.debug import Print, Var, ApplicationError, g_logmethod  # @UnusedImport


logger = pyschunk.tools.mylogger.getLogger( "BKSTools.demo.demo_bks_grip_outside_inside" )
pyschunk.tools.mylogger.setupLogging()
g_logmethod = logger.info

from bkstools.bks_lib import bks_options


def main():
    if ( "__file__" in globals() ):
        prog = os.path.basename( globals()["__file__"] )
    else:
        # when runnging as an exe generated by py2exe then __file__ is not defined!
        prog = "demo_bks_grip_outside_inside.exe"

    parser = bks_options.cBKSTools_OptionParser( prog=prog,
                                                 description = __doc__,     # @UndefinedVariable
                                                 additional_arguments=[ "grip_velocity", "force" ] )

    args = parser.parse_args()

    if ( args.grip_velocity is None ):
        # BasicGrip: use default grip velocity stored in gripper:
        grip_velocity_ums = 0
    else:
        # SoftGrip: use the provided velocity:
        grip_velocity_ums = int( args.grip_velocity * 1000.0 )
    force_percent = args.force

    bks = BKSModule( args.host, debug=args.debug, repeater_timeout=args.repeat_timeout, repeater_nb_tries=args.repeat_nb_tries )

    def my_sleep( t ):
        '''alias
        '''
        return keep_communication_alive_sleep( bks, t )

    Print( "Acknowledging...")
    bks.MakeReady()

    sw = bks.plc_sync_input[0]

    bks.move_to_absolute_position( 30000, 25000 )


    def Check():
        sw = bks.plc_sync_input[0]
        r = ""
        sep = "    "
        if ( sw & bks.sw_success ):
            r += sep + "Success"
            sep = " "

        if ( sw & bks.sw_warning ):
            r += sep + "Warning"
            sep = " "

        if ( sw & bks.sw_error ):
            r += sep + "Error"
            sep = " "

            r += " 0x%04x (%s)" % (bks.err_code,bks.enums["err_code"].GetName(bks.err_code, "?" ))

            cw = bks.plc_sync_output[0]
            bks.plc_sync_output[0] = cw | 0x04000000
            my_sleep(0.5)
            bks.plc_sync_output[0] = cw

        if ( sw & bks.sw_not_feasible ):
            r += sep + "not_feasible"
            sep = " "

        if ( sw & bks.sw_gripped ):
            r += sep + "gripped"
            sep = " "

        if ( sw & bks.sw_no_workpiece_detected ):
            r += sep + "no_workpiece_detected"
            sep = " "

        Print( r )

    pause = 4.0
    pause_command = 0.1
    n  = 0
    while True:

        Print( "Loop %d..." % n)
        Print( "  Gripping workpiece from outside...")
        bks.grip_workpiece( bks.grip_from_outside, grip_velocity_ums, force_percent )
        my_sleep( pause_command )

        my_sleep( pause )
        Check()

        Print( "  Releasing workpiece...")
        bks.release_workpiece( )
        my_sleep( pause_command )

        my_sleep( pause )
        Check()


        Print( "  Gripping workpiece from inside...")
        #bks.plc_sync_output.control_dword    = 0x81000000  # whithout this line we get not feasible for firmware < B15005
        my_sleep( pause_command )
        bks.grip_workpiece( bks.grip_from_inside, grip_velocity_ums, force_percent )
        my_sleep( pause_command )

        my_sleep( pause )
        Check()

        Print( "  Releasing workpiece...")
        bks.release_workpiece( )
        my_sleep( pause_command )

        my_sleep( pause )
        Check()

        n += 1

if __name__ == '__main__':
    from pyschunk.tools import attach_to_debugger
    attach_to_debugger.AttachToDebugger( main )
    #main()
