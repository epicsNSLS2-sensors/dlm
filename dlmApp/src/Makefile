TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================

# For Kate Feng's implementation of devScaler.c, which uses Till
# Straumann's basicIoOps.h to bridge any mismatch between endianness
# of Joerger scaler hardware and endianness of processor.
#USR_CFLAGS += -DHAS_IOOPS_H

#=============================
# build an ioc application

PROD_IOC = dlm

# Note that the order in which .dbd files and libraries are added to a list
# variable is important.  For .dbd files, things must be defined before they
# are referenced by a later .dbd file.  For libraries, things must be referenced
# before they are searched for; otherwise they won't be included.

# Custom stuff in development

dlm_SRCS += dlm.c
dlm_Common_DBD += dlm.dbd

##################################################################
# First, define dlm_Common_DBD and dlm_Common_LIBS from the modules
# defined in RELEASE
##################################################################
DBD += dlm_Common.dbd
dlm_Common_DBD += base.dbd


ifdef TDS3000
	dlm_Common_DBD += devTDS3000.dbd
	dlm_Common_LIBS := devTDS3000 $(dlm_Common_LIBS)
endif

#ifdef CAPUTLOG
#	dlm_Common_DBD += caPutLog.dbd
#	dlm_Common_LIBS := caPutLog $(dlm_Common_LIBS)
#endif

ifdef CAPUTRECORDER
	dlm_Common_DBD += caputRecorder.dbd
	dlm_Common_LIBS := caputRecorder $(dlm_Common_LIBS)
endif

ifdef SNCSEQ
	ifeq (seq-2-1, $(findstring seq-2-1, $(SNCSEQ)))
		dlm_Common_DBD += devSequencer.dbd
		dlm_Common_LIBS := seqDev seq pv $(dlm_Common_LIBS)
	else ifeq (seq-2.1, $(findstring seq-2.1, $(SNCSEQ)))
		dlm_Common_DBD += devSequencer.dbd
		dlm_Common_LIBS := seqDev seq pv $(dlm_Common_LIBS)
	else
		# seq 2.2.
		dlm_Common_LIBS := seq pv $(dlm_Common_LIBS)
	endif
endif

ifdef ASYN
	dlm_Common_DBD += asyn.dbd drvAsynSerialPort.dbd
	dlm_Common_DBD += drvAsynIPPort.dbd drvVxi11.dbd devGpib.dbd
	dlm_Common_LIBS := asyn $(dlm_Common_LIBS)
endif

ifdef STD
	dlm_Common_DBD += stdSupport.dbd
	dlm_Common_LIBS := std $(dlm_Common_LIBS)
endif

ifdef CALC
	dlm_Common_DBD += calcSupport.dbd
	dlm_Common_LIBS := calc $(dlm_Common_LIBS)
endif

ifdef BUSY
	dlm_Common_DBD += busySupport.dbd
	dlm_Common_LIBS := busy $(dlm_Common_LIBS)
endif

ifdef SSCAN
	dlm_Common_DBD += sscanSupport.dbd
	dlm_Common_LIBS := sscan $(dlm_Common_LIBS)
	ifdef SNCSEQ
		dlm_Common_DBD += sscanProgressSupport.dbd
		dlm_Common_LIBS := scanProgress $(dlm_Common_LIBS)
	endif
endif

ifdef AUTOSAVE
	dlm_Common_DBD += asSupport.dbd
	dlm_Common_LIBS := autosave $(dlm_Common_LIBS)
endif

ifdef OPTICS
	dlm_Common_DBD += opticsSupport.dbd
	dlm_Common_LIBS := optics $(dlm_Common_LIBS)
endif

ifdef MCA
	dlm_Common_DBD += mcaSupport.dbd
	dlm_Common_LIBS := mca $(dlm_Common_LIBS)
endif

ifdef IP
	dlm_Common_DBD += ipSupport.dbd
	dlm_Common_LIBS := ip $(dlm_Common_LIBS)
endif

ifdef MODBUS
	dlm_Common_DBD += modbusSupport.dbd
	dlm_Common_LIBS := modbus $(dlm_Common_LIBS)
endif

ifdef MOTOR
	dlm_Common_DBD += motorSupport.dbd devAcsMotor.dbd devAerotech.dbd
	dlm_Common_DBD += devAttocube.dbd devFaulhaberMotor.dbd devImsMotor.dbd
	dlm_Common_DBD += devKohzuMotor.dbd devMclennanMotor.dbd devMicos.dbd
	dlm_Common_DBD += devMicroMo.dbd devNewFocus.dbd devNewport.dbd
  ifdef SNCSEQ
	#dlm_Common_DBD += devAerotechSeq.dbd devNewportSeq.dbd
  endif
	dlm_Common_DBD += devOriel.dbd devPC6K.dbd devPIJena.dbd devPIMotor.dbd
	dlm_Common_DBD += devSPiiPlus.dbd devSmartMotorMotor.dbd devSoftMotor.dbd
	dlm_Common_DBD += devThorLabs.dbd motorSimSupport.dbd

	dlm_Common_LIBS := motor $(dlm_Common_LIBS)
	dlm_Common_LIBS := Acs acsTech80 Aerotech Attocube Faulhaber Ims KohzuMotor $(dlm_Common_LIBS)
	dlm_Common_LIBS := Mclennan Micos MicroMo NewFocus Newport Oriel PI PIJena $(dlm_Common_LIBS)
	dlm_Common_LIBS := Parker SmartMotor ThorLabs softMotor motorSimSupport $(dlm_Common_LIBS)
endif

ifdef STREAM
	dlm_Common_DBD += stream.dbd streamSynApps.dbd
	dlm_Common_LIBS := stream streamSynApps $(dlm_Common_LIBS)
endif

ifdef DEVIOCSTATS
	dlm_Common_DBD += devIocStats.dbd iocAdmin.dbd
	dlm_Common_LIBS := devIocStats $(dlm_Common_LIBS)
endif

ifdef ETHERIP
	dlm_Common_DBD += ether_ip.dbd
	dlm_Common_LIBS := ether_ip $(dlm_Common_LIBS)
endif

ifdef ALIVE
	dlm_Common_DBD += aliveSupport.dbd
	dlm_Common_LIBS := alive $(dlm_Common_LIBS)
endif

ifdef DELAYGEN
	dlm_Common_DBD += delaygenSupport.dbd
	dlm_Common_LIBS := delaygen $(dlm_Common_LIBS)
endif

ifdef VAC
	dlm_Common_DBD += vacSupport.dbd
	dlm_Common_LIBS := vac $(dlm_Common_LIBS)
endif

dlm_Common_LIBS := $(dlm_Common_LIBS) $(EPICS_BASE_IOC_LIBS)

##################################################################


ifeq (win32-x86,$(findstring win32-x86, $(T_A)))

	DBD  += iocdlmWin32.dbd
	iocdlmWin32_DBD += dlm_Common.dbd

	ifdef MCA
		# If your host supports libpcap and libnet and you want to build
		# Canberra network support uncomment the following lines
		#iocdlmWin32_DBD += mcaCanberraSupport.dbd
		#dlm_LIBS_WIN32 += mcaCanberra
		#dlm_LIBS_WIN32 += wpcap Packet
	endif

	ifdef DXP
		# If you want to build parallel port or USB interfaces to Saturn and/or
		# xMAP DXP, then uncomment the following lines
		iocdlmWin32_DBD += dxpSupport.dbd
		dlm_LIBS_WIN32 += dxp handel
		dlm_LIBS_WIN32 += DLPORTIO PlxApi
		dlm_SYS_LIBS_WIN32 += setupapi
	endif

	ifdef AREA_DETECTOR
		# areaDetector provides a Makefile for things it needs and supplies
		PROD_NAME = AD
		-include $(ADCORE)/ADApp/commonDriverMakefile
		iocdlmWin32_DBD += ADSupport.dbd NDPluginSupport.dbd
		dlm_LIBS_WIN32 += $(AD_LIBS)
		ifdef ADEXAMPLE
			# To add the simDetector uncomment the following lines
			iocdlmLinux_DBD += simDetectorSupport.dbd
			dlm_LIBS_WIN32 += simDetector
		endif
	endif
endif

ifeq (windows-x64,$(findstring windows-x64, $(T_A)))
	DBD  += iocdlmWin64.dbd
	iocdlmWin64_DBD += dlm_Common.dbd

	ifdef MCA
		# If your host supports libpcap and libnet and you want to build Canberra network
		# support uncomment the following line
		iocdlmWin64_DBD += mcaCanberraSupport.dbd
		dlm_LIBS_WIN32 += mcaCanberra
		dlm_LIBS_WIN32 += wpcap Packet
	endif

	ifdef AREA_DETECTOR
		# areaDetector provides a Makefile for things it needs and supplies
		PROD_NAME = AD
		-include $(ADCORE)/ADApp/commonDriverMakefile
		iocdlmWin64_DBD += ADSupport.dbd NDPluginSupport.dbd
		dlm_LIBS_WIN32 += $(AD_LIBS)
		# To add the simDetector uncomment the following lines
		iocdlmLinux_DBD += simDetectorSupport.dbd
		dlm_LIBS_WIN32 += simDetector
	endif
endif

ifeq ($(EPICS_HOST_ARCH), cygwin-x86)
	DBD  += iocdlmCygwin.dbd
	iocdlmCygwin_DBD += dlm_Common.dbd

	ifdef DXP
		# If you want to build parallel port or USB interfaces to Saturn and/or
		# xMAP DXP,then uncomment the following lines
		#iocdlmCygwin_DBD += dxpSupport.dbd
		#dlm_LIBS_cygwin32 += dxp handel
		#dlm_SYS_LIBS_cygwin32 += DLPORTIO PlxApi setupapi
	endif

	dlm_SYS_LIBS_cygwin32 += $(CYGWIN_RPC_LIB)

endif

ifeq (vxWorks,$(findstring vxWorks, $(T_A)))
	DBD  += iocdlmVX.dbd
	iocdlmVX_DBD += dlm_Common.dbd

	ifdef ALLEN_BRADLEY
		dlm_LIBS_vxWorks += allenBradley
	endif

	ifdef QUADEM
		iocdlmVX_DBD += drvAHxxx.dbd
		iocdlmVX_DBD += drvAPS_EM.dbd
		dlm_LIBS_vxWorks += quadEM
	endif

	ifdef AREA_DETECTOR
		# areaDetector provides a Makefile for things it needs and supplies
		PROD_NAME = AD
		-include $(ADCORE)/ADApp/commonDriverMakefile
		iocdlmVX_DBD += ADSupport.dbd NDPluginSupport.dbd
		dlm_LIBS_vxWorks += $(AD_LIBS)
		# To add the simDetector uncomment the following lines
		iocdlmVX_DBD += simDetectorSupport.dbd
		dlm_LIBS_vxWorks += simDetector
	endif

	ifdef VME
		iocdlmVX_DBD += vmeVXSupport.dbd
		dlm_LIBS_vxWorks += vme
	endif

	ifdef STD
		iocdlmVX_DBD += stdVXSupport.dbd
	endif

	ifdef IP
		iocdlmVX_DBD += ipVXSupport.dbd
	endif

	ifdef MCA
		iocdlmVX_DBD += SIS38XXSupport.dbd
		iocdlmVX_DBD += mcaCanberraSupport.dbd
		dlm_LIBS_vxWorks += SIS38XX
		dlm_LIBS_vxWorks += mcaCanberra
	endif

	ifdef IPUNIDIG
		iocdlmVX_DBD += ipUnidigSupport.dbd
		dlm_LIBS_vxWorks += ipUnidig
	endif

	ifdef DAC128V
		iocdlmVX_DBD += dac128VSupport.dbd
		dlm_LIBS_vxWorks += dac128V
	endif

	ifdef IP330
		iocdlmVX_DBD += ip330Support.dbd
		dlm_LIBS_vxWorks += ip330
	endif

	ifdef CAMAC
		iocdlmVX_DBD += camacSupport.dbd
		iocdlmVX_DBD += devCamacSupport.dbd
		dlm_LIBS_vxWorks += camac devCamac
	endif

	ifdef ALLEN_BRADLEY
		iocdlmVX_DBD += allenBradley.dbd
	endif

	ifdef LOVE
		iocdlmVX_DBD += devLove.dbd
		dlm_LIBS_vxWorks += love
	endif

	ifdef IPAC
		iocdlmVX_DBD += tyGSOctal.dbd
		iocdlmVX_DBD += drvIpac.dbd
		dlm_LIBS_vxWorks += TyGSOctal Ipac
	endif

	ifdef ASYN
		iocdlmVX_DBD += drvGsIP488.dbd
	endif

	ifdef SOFTGLUE
		iocdlmVX_DBD += softGlueSupport.dbd
		dlm_LIBS_vxWorks += softGlue
	endif

	ifdef MOTOR
		iocdlmVX_DBD += devDeltaTau.dbd
		iocdlmVX_DBD += devOms.dbd
		dlm_LIBS_vxWorks += oms DeltaTau
	endif

	ifdef DEVIOCSTATS
		iocdlmVX_DBD += devVxStats.dbd
	endif
endif

ifneq (,$(findstring linux, $(T_A)))
	DBD  += iocdlmLinux.dbd
	iocdlmLinux_DBD += dlm_Common.dbd

ifeq ($(HAVE_HDF5), YES)
ifeq ($(HAVE_SZIP), YES)

	ifdef QUADEM
		iocdlmLinux_DBD += drvAHxxx.dbd
		dlm_LIBS_Linux += quadEM
	endif

	ifdef AREA_DETECTOR
		# areaDetector provides a Makefile for things it needs and supplies
		PROD_NAME = AD
		-include $(ADCORE)/ADApp/commonDriverMakefile
		iocdlmLinux_DBD += ADSupport.dbd NDPluginSupport.dbd
		dlm_LIBS_Linux += $(AD_LIBS)
		# To add the simDetector uncomment the following lines
		iocdlmLinux_DBD += simDetectorSupport.dbd
		dlm_LIBS_Linux += simDetector
	endif

	ifdef DXP
		# If your host supports parallel port or USB interfaces to Saturn DXP, set
		# LINUX_USB_INSTALLED to YES in <synApps>/configure/CONFIG_SITE.
		ifeq ($(LINUX_USB_INSTALLED), YES)
			iocdlmLinux_DBD += dxpSupport.dbd
			dlm_LIBS_Linux  += dxp handel
			dlm_SYS_LIBS_Linux += usb
		endif
	endif

endif
endif

	ifdef MCA
		# If your host supports libpcap and libnet and you want to build Canberra network
		# support, set LINUX_NET_INSTALLED to YES in <synApps>/configure/CONFIG_SITE.
		ifeq ($(LINUX_NET_INSTALLED), YES)
			iocdlmLinux_DBD += mcaCanberraSupport.dbd
			dlm_LIBS_Linux += mcaCanberra
			dlm_SYS_LIBS_Linux += net pcap
		endif
	endif

	ifdef IPAC
		iocdlmLinux_DBD += drvIpac.dbd
		dlm_LIBS_Linux += Ipac
	endif

	ifdef SOFTGLUE
		iocdlmLinux_DBD += softGlueSupport.dbd
		dlm_LIBS_Linux += softGlue
	endif
endif

ifeq ($(OS_CLASS), Darwin)
	DBD  += iocdlmDarwin.dbd
	iocdlmDarwin_DBD += dlm_Common.dbd
endif



# <name>_registerRecordDeviceDriver.cpp will be created from <name>.dbd
dlm_SRCS_vxWorks  += iocdlmVX_registerRecordDeviceDriver.cpp
dlm_SRCS_Linux    += iocdlmLinux_registerRecordDeviceDriver.cpp     dlmMain.cpp
ifeq (win32-x86,$(findstring win32-x86, $(T_A)))
	dlm_SRCS_WIN32    += iocdlmWin32_registerRecordDeviceDriver.cpp     dlmMain.cpp
endif
ifeq (windows-x64,$(findstring windows-x64, $(T_A)))
	dlm_SRCS_WIN32    += iocdlmWin64_registerRecordDeviceDriver.cpp     dlmMain.cpp
endif
dlm_SRCS_cygwin32 += iocdlmCygwin_registerRecordDeviceDriver.cpp    dlmMain.cpp
dlm_SRCS_solaris  += iocdlm_solaris_registerRecordDeviceDriver.cpp  dlmMain.cpp
dlm_SRCS_Darwin   += iocdlmDarwin_registerRecordDeviceDriver.cpp    dlmMain.cpp



#The following adds support from base/src/vxWorks
dlm_OBJS_vxWorks += $(EPICS_BASE_BIN)/vxComLibrary

dlm_LIBS_vxWorks  += $(dlm_Common_LIBS)
dlm_LIBS_Linux    += $(dlm_Common_LIBS)
dlm_LIBS_solaris  += $(dlm_Common_LIBS)
dlm_LIBS_cygwin32 += $(dlm_Common_LIBS)
dlm_LIBS_WIN32    += $(dlm_Common_LIBS)
dlm_LIBS_Darwin   += $(dlm_Common_LIBS)


#===========================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

$(COMMON_DIR)/iocdlmWin32Include.dbd: $(COMMON_DIR)/dlm_Common.dbd
$(COMMON_DIR)/iocdlmWin64Include.dbd: $(COMMON_DIR)/dlm_Common.dbd
$(COMMON_DIR)/iocdlmCygwinInclude.dbd: $(COMMON_DIR)/dlm_Common.dbd
$(COMMON_DIR)/iocdlmVXInclude.dbd: $(COMMON_DIR)/dlm_Common.dbd
$(COMMON_DIR)/iocdlmLinuxInclude.dbd: $(COMMON_DIR)/dlm_Common.dbd
$(COMMON_DIR)/iocdlmDarwinInclude.dbd: $(COMMON_DIR)/dlm_Common.dbd

$(COMMON_DIR)/iocdlmWin32.dbd: $(COMMON_DIR)/dlm_Common.dbd
$(COMMON_DIR)/iocdlmWin64.dbd: $(COMMON_DIR)/dlm_Common.dbd
$(COMMON_DIR)/iocdlmCygwin.dbd: $(COMMON_DIR)/dlm_Common.dbd
$(COMMON_DIR)/iocdlmVX.dbd: $(COMMON_DIR)/dlm_Common.dbd
$(COMMON_DIR)/iocdlmLinux.dbd: $(COMMON_DIR)/dlm_Common.dbd
$(COMMON_DIR)/iocdlmDarwin.dbd: $(COMMON_DIR)/dlm_Common.dbd

iocdlmWin32.dbd$(DEP): $(COMMON_DIR)/dlm_Common.dbd
iocdlmWin64.dbd$(DEP): $(COMMON_DIR)/dlm_Common.dbd
iocdlmCygwin.dbd$(DEP): $(COMMON_DIR)/dlm_Common.dbd
iocdlmVX.dbd$(DEP): $(COMMON_DIR)/dlm_Common.dbd
iocdlmLinux.dbd$(DEP): $(COMMON_DIR)/dlm_Common.dbd
iocdlmDarwin.dbd$(DEP): $(COMMON_DIR)/dlm_Common.dbd
