#############################################################################
#
# Project Makefile
#
# (c) R2D2-leads 2020
#
# This file is in the public domain.
# 
#############################################################################

MODULE_NAME			= ATP
SERIAL_PORT 		= /dev/ttyACM0
												#/dev/tty.usbmodem146201
												#COM4

PLATFORM			= due						#native
												#due


CONSOLE_BAUDRATE	= 115200

export 
include $(HU_ENV_ROOT_DRIVE)$(HU_ENV_ROOT_DIR)/modules/Makefile.module