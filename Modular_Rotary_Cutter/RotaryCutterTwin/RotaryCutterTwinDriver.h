///////////////////////////////////////////////////////////////////////////////
// RotaryCutterTwinDriver.h

#ifndef __ROTARYCUTTERTWINDRIVER_H__
#define __ROTARYCUTTERTWINDRIVER_H__

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

#include "TcBase.h"

#define ROTARYCUTTERTWINDRV_NAME        "ROTARYCUTTERTWIN"
#define ROTARYCUTTERTWINDRV_Major       1
#define ROTARYCUTTERTWINDRV_Minor       0

#define DEVICE_CLASS CRotaryCutterTwinDriver

#include "ObjDriver.h"

class CRotaryCutterTwinDriver : public CObjDriver
{
public:
	virtual IOSTATUS	OnLoad();
	virtual VOID		OnUnLoad();

	//////////////////////////////////////////////////////
	// VxD-Services exported by this driver
	static unsigned long	_cdecl ROTARYCUTTERTWINDRV_GetVersion();
	//////////////////////////////////////////////////////
	
};

Begin_VxD_Service_Table(ROTARYCUTTERTWINDRV)
	VxD_Service( ROTARYCUTTERTWINDRV_GetVersion )
End_VxD_Service_Table


#endif // ifndef __ROTARYCUTTERTWINDRIVER_H__