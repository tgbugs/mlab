//***********************************************************************************************
//
//    Copyright (c) 2004 Axon Instruments.
//    All rights reserved.
//
//***********************************************************************************************
// MODULE:  AXCLAMPEXMSG.HPP
// PURPOSE: Interface definition for AxClampexMsg.DLL
// AUTHOR:  GRB  Mar 2004
//

#ifndef INC_AXCLAMPEXMSG_HPP
#define INC_AXCLAMPEXMSG_HPP

#if _MSC_VER >= 1000
#pragma once
#endif // _MSC_VER >= 1000

// define the macro for exporting/importing the API entry points.
// N.B. the symbol below should only be defined when building this DLL.
#ifdef MAK_AXCLXMSG_DLL
   #define AXCLXMSG   __declspec(dllexport)
#else
   #define AXCLXMSG   __declspec(dllimport)
#endif

extern "C" {

// The handle type declaration.
DECLARE_HANDLE(HCLXMSG);

// API version number.
#define CLXMSG_APIVERSION       1,0,0,5
#define CLXMSG_APIVERSION_STR  "1.0.0.5"
 
// Windows Class name for the clampex msg handler hidden window.
#define CLXMSG_CLASSNAME "ClampexMessageHandlerClass"

//==============================================================================================
// DLL creation/destruction functions
//==============================================================================================

// Check on the version number of the API interface.
AXCLXMSG BOOL WINAPI CLXMSG_CheckAPIVersion(LPCSTR pszQueryVersion);

// Create the clampex message handler object.
AXCLXMSG HCLXMSG WINAPI CLXMSG_CreateObject(int *pnError);

// Destroy the clampex message handler object.
AXCLXMSG void  WINAPI CLXMSG_DestroyObject(HCLXMSG hClxmsg);

//==============================================================================================
// General functions
//==============================================================================================

// Set timeout in milliseconds for messages to Clampex.
AXCLXMSG BOOL WINAPI CLXMSG_SetTimeOut(HCLXMSG hClxmsg, UINT uTimeOutMS, int *pnError);

//==============================================================================================
// Acquisition functions
//==============================================================================================

// Request Clampex to load protocol.
AXCLXMSG BOOL  WINAPI CLXMSG_LoadProtocol(HCLXMSG hClxmsg, char *pszFilename, int *pnError);

// Request the Clampex status.
AXCLXMSG BOOL  WINAPI CLXMSG_GetStatus(HCLXMSG hClxmsg, UINT *puStatus, int *pnError);

// Initiate Clampex REPEAT.
AXCLXMSG BOOL  WINAPI CLXMSG_SetRepeat(HCLXMSG hClxmsg, BOOL bRepeat, int *pnError);

// Initiate Clampex VIEW, RECORD or RERECORD.
AXCLXMSG BOOL  WINAPI CLXMSG_StartAcquisition(HCLXMSG hClxmsg, UINT uMode, int *pnError);

// Initiate Clampex STOP.
AXCLXMSG BOOL  WINAPI CLXMSG_StopAcquisition(HCLXMSG hClxmsg, int *pnError);

//==============================================================================================
// Telegraph functions
//==============================================================================================

// Gets the specified telegraph value
AXCLXMSG BOOL  WINAPI CLXMSG_GetTelegraphValue(HCLXMSG hClxmsg, UINT uChan, UINT uTelItem, float *pfTelValue, int *pnError);

// Gets the specified telegraph instrument name
AXCLXMSG BOOL  WINAPI CLXMSG_GetTelegraphInstrument(HCLXMSG hClxmsg, UINT uChan, char *pszInstrument, UINT uSize, int *pnError);

//==============================================================================================
// Membrane Test functions
//==============================================================================================

// Start the Clampex membrane test.
AXCLXMSG BOOL  WINAPI CLXMSG_StartMembTest(HCLXMSG hClxmsg, UINT uOut, int *pnError);

// Close the Clampex membrane test.
AXCLXMSG BOOL  WINAPI CLXMSG_CloseMembTest(HCLXMSG hClxmsg, UINT uOut, int *pnError);

// Set the Clampex membrane test holding.
AXCLXMSG BOOL  WINAPI CLXMSG_SetMembTestHolding(HCLXMSG hClxmsg, double dHolding, int *pnError);

// Get the Clampex membrane test holding.
AXCLXMSG BOOL  WINAPI CLXMSG_GetMembTestHolding(HCLXMSG hClxmsg, double *pdHolding, int *pnError);

// Set the Clampex membrane test pulse height.
AXCLXMSG BOOL  WINAPI CLXMSG_SetMembTestPulseHeight(HCLXMSG hClxmsg, double dPulseHeight, int *pnError);

// Get the Clampex membrane test pulse height.
AXCLXMSG BOOL  WINAPI CLXMSG_GetMembTestPulseHeight(HCLXMSG hClxmsg, double *pdPulseHeight, int *pnError);

// Flush the membrane test cache.
AXCLXMSG BOOL  WINAPI CLXMSG_FlushMembTestCache(HCLXMSG hClxmsg, int *pnError);

// Get the current size of the membrane test cache.
AXCLXMSG BOOL  WINAPI CLXMSG_GetMembTestCacheSize(HCLXMSG hClxmsg, UINT *puSize, int *pnError);

// Set the maximum membrane test cache size.
AXCLXMSG BOOL  WINAPI CLXMSG_SetMembTestCacheMaxSize(HCLXMSG hClxmsg, UINT uMaxSize, int *pnError);

// Get the average membrane test cache data for the number of entries specified by *puCount
AXCLXMSG BOOL  WINAPI CLXMSG_GetMembTestCacheData(HCLXMSG hClxmsg, double *pdAvRt, double *pdAvCm, double *pdAvRm, double *pdAvRa, double *pdAvTau, double *pdAvHold, UINT *puCount, int *pnError);

// Scales the membrane test Y axis
AXCLXMSG BOOL  WINAPI CLXMSG_ScaleMembTestYAxis(HCLXMSG hClxmsg, UINT uScale, int *pnError);

// Set the membrane test update rate in Hertz
AXCLXMSG BOOL  WINAPI CLXMSG_SetMembTestRate(HCLXMSG hClxmsg, double dRate, int *pnError);

// Get the membrane test update rate in Hertz
AXCLXMSG BOOL  WINAPI CLXMSG_GetMembTestRate(HCLXMSG hClxmsg, double *pdRate, int *pnError);

// Set the membrane test averaging state and number of edges per average.
AXCLXMSG BOOL  WINAPI CLXMSG_SetMembTestAveraging(HCLXMSG hClxmsg, BOOL bAveraging, UINT uNumEdges, int *pnError);

// Get the membrane test averaging state and number of edges per average.
AXCLXMSG BOOL  WINAPI CLXMSG_GetMembTestAveraging(HCLXMSG hClxmsg, BOOL *pbAveraging, UINT *puNumEdges, int *pnError);

//==============================================================================================
// Seal Test functions
//==============================================================================================

// Get the current size of the seal test cache.
AXCLXMSG BOOL  WINAPI CLXMSG_GetSealTestCacheSize(HCLXMSG hClxmsg, UINT *puSize, int *pnError);

// Set the maximum seal test cache size.
AXCLXMSG BOOL  WINAPI CLXMSG_SetSealTestCacheMaxSize(HCLXMSG hClxmsg, UINT uMaxSize, int *pnError);

// Flush the seal test cache.
AXCLXMSG BOOL  WINAPI CLXMSG_FlushSealTestCache(HCLXMSG hClxmsg, int *pnError);

// Get the average seal test cache data for the number of entries specified by *puCount
AXCLXMSG BOOL  WINAPI CLXMSG_GetSealTestCacheData(HCLXMSG hClxmsg, double *pdAvRs, UINT *puCount, int *pnError);

// Set the Clampex seal test holding.
AXCLXMSG BOOL  WINAPI CLXMSG_SetSealTestHolding(HCLXMSG hClxmsg, double dHolding, int *pnError);

// Set the Clampex seal test pulse height.
AXCLXMSG BOOL  WINAPI CLXMSG_SetSealTestPulseHeight(HCLXMSG hClxmsg, double dPulseHeight, int *pnError);

//==============================================================================================
// Error functions
//==============================================================================================

// Errors etc.
AXCLXMSG BOOL  WINAPI CLXMSG_BuildErrorText(HCLXMSG hClxmsg, int nErrorNum, LPSTR sTxtBuf, UINT uMaxLen);

//==============================================================================================
// Error codes
//==============================================================================================

// General error codes.
const int CLXMSG_ERROR_NOERROR                         = 4000;
const int CLXMSG_ERROR_OUTOFMEMORY                     = 4001;
const int CLXMSG_ERROR_CLAMPEXNOTOPEN                  = 4002;
const int CLXMSG_ERROR_INVALIDDLLHANDLE                = 4003;
const int CLXMSG_ERROR_MSGTIMEOUT                      = 4004;
const int CLXMSG_ERROR_PROTOCOLPATHNOTSET              = 4005;
const int CLXMSG_ERROR_PROTOCOLCANNOTLOAD              = 4006;
const int CLXMSG_ERROR_PROTOCOLNOTVALID                = 4007;
const int CLXMSG_ERROR_PROTOCOLCANNOTLOADWHENRECORDING = 4008;
const int CLXMSG_ERROR_DIALOGOPEN                      = 4009;
const int CLXMSG_ERROR_STOPIGNOREDWHENIDLE             = 4010;
const int CLXMSG_ERROR_UNKNOWNACQMODE                  = 4011;
const int CLXMSG_ERROR_CACHEISEMPTY                    = 4012;
const int CLXMSG_ERROR_ZEROPOINTSSPECIFIED             = 4013;
const int CLXMSG_ERROR_INVALIDPARAMETER                = 4014;

// Membrane Test error codes.
const int CLXMSG_ERROR_MEMB_RESPONSECLIPPED            = 5000; 
const int CLXMSG_ERROR_MEMB_RESPONSERECTIFIED          = 5001;
const int CLXMSG_ERROR_MEMB_SLOWRISETIME               = 5002;
const int CLXMSG_ERROR_MEMB_NOPEAKFOUND                = 5003;
const int CLXMSG_ERROR_MEMB_BADRESPONSE                = 5004;
const int CLXMSG_ERROR_MEMB_TAUTOOFAST                 = 5005;
const int CLXMSG_ERROR_MEMB_TAUTOOSLOW                 = 5006;
const int CLXMSG_ERROR_MEMB_TOOFEWPOINTS               = 5007;
const int CLXMSG_ERROR_MEMB_NOPULSESPECIFIED           = 5008;
const int CLXMSG_ERROR_MEMB_HOLDINGOUTOFRANGE          = 5009;
const int CLXMSG_ERROR_MEMB_PULSEOUTOFRANGE            = 5010;
const int CLXMSG_ERROR_MEMB_CANNOTSTARTMORETHANONE     = 5011;
const int CLXMSG_ERROR_MEMB_ALREADYSTARTED             = 5012;
const int CLXMSG_ERROR_MEMB_ALREADYCLOSED              = 5013;
const int CLXMSG_ERROR_MEMB_INVALIDOUTPUTDAC           = 5014; 

//==============================================================================================
// Function parameters
//==============================================================================================

// Parameters for CLXMSG_GetStatus(HCLXMSG hClxmsg, UINT *puStatus, int *pnError);
// *puStatus filled out as:
const UINT CLXMSG_ACQ_STATUS_IDLE             = 100; // acquisition is not in progress.
const UINT CLXMSG_ACQ_STATUS_DIALOGOPEN       = 101; // dialog is open in Clampex.
const UINT CLXMSG_ACQ_STATUS_TRIGWAIT         = 102; // acquisition is pending waiting for a trigger.
const UINT CLXMSG_ACQ_STATUS_VIEWING          = 103; // view-only acquisition is in progress.
const UINT CLXMSG_ACQ_STATUS_RECORDING        = 104; // acquisition is currently recording to disk.
const UINT CLXMSG_ACQ_STATUS_PAUSEVIEW        = 105; // recording has been paused, but display is left running.
const UINT CLXMSG_ACQ_STATUS_PAUSED           = 106; // recording has been paused - display stopped.
const UINT CLXMSG_ACQ_STATUS_DISABLED         = 107; // acquisition has been disabled because of bad parameters.

// Parameters for CLXMSG_StartAcquisition(HCLXMSG hClxmsg, UINT uMode, int *pnError);
// uMode filled in as:
const UINT CLXMSG_ACQ_START_VIEW              = 108; // acquire data with current protocol but do not save to file.
const UINT CLXMSG_ACQ_START_RECORD            = 109; // acquire data with current protocol and save to file. 
const UINT CLXMSG_ACQ_START_RERECORD          = 110; // acquire data with current protocol and save over last file.  
const UINT CLXMSG_ACQ_START_RERECORD_PROMPT   = 111; // acquire data with current protocol and save over last file but prompt before overwriting.

// Parameters for CLXMSG_GetTelegraphValue(HCLXMSG hClxmsg, UINT uChan, UINT uTelItem, float *pfTelValue, int *pnError);
// uTelItem filled in as:
const UINT CLXMSG_TEL_CM                      = 112; // request the telegraphed whole cell capacitance.
const UINT CLXMSG_TEL_GAIN                    = 113; // request the telegraphed gain.
const UINT CLXMSG_TEL_MODE                    = 114; // request the telegraphed mode.
const UINT CLXMSG_TEL_FREQUENCY               = 115; // request the telegraphed low pass filter cutoff frequency.
const UINT CLXMSG_TEL_CMDSCALEFACTOR          = 116; // request the telegraphed command scale factor.
// *pfTelValue filled out as 
const UINT CLXMSG_TEL_MODE_VCLAMP             = 0;   // mode is voltage clamp.
const UINT CLXMSG_TEL_MODE_ICLAMP             = 1;   // mode is current clamp.
const UINT CLXMSG_TEL_MODE_ICLAMPZERO         = 2;   // mode I=0.

// Parameters for CLXMSG_StartMembTest(HCLXMSG hClxmsg, UINT uOut, int *pnError);
// uOut filled in as:
const UINT CLXMSG_MBT_OUT0                    = 120; // start/close Membrane Test OUT0.
const UINT CLXMSG_MBT_OUT1                    = 121; // start/close Membrane Test OUT1.

// Parameters for CLXMSG_ScaleMembTestYAxis(HCLXMSG hClxmsg, UINT uScale, int *pnError);
// uScale filled in as:
const UINT CLXMSG_MBT_AUTOSCALE               = 130; // autoscale the Membrane Test Y axis.
const UINT CLXMSG_MBT_FULLSCALE               = 131; // fullscale the Membrane Test Y axis.

// size of telegraph instrument name string
const UINT CLXMSG_TEL_INSTRU_NAMESIZE         = 260;

} // end of extern "C"

#endif // INC_AXCLAMEXMSG_HPP