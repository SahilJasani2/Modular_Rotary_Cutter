///////////////////////////////////////////////////////////////////////////////
// RotaryCutterTwinDriver.cpp
#include "TcPch.h"
#pragma hdrstop

#include "RotaryCutterTwinDriver.h"
#include "RotaryCutterTwinClassFactory.h"

DECLARE_GENERIC_DEVICE(ROTARYCUTTERTWINDRV)

IOSTATUS CRotaryCutterTwinDriver::OnLoad( )
{
	TRACE(_T("CObjClassFactory::OnLoad()\n") );
	m_pObjClassFactory = new CRotaryCutterTwinClassFactory();

	return IOSTATUS_SUCCESS;
}

VOID CRotaryCutterTwinDriver::OnUnLoad( )
{
	delete m_pObjClassFactory;
}

unsigned long _cdecl CRotaryCutterTwinDriver::ROTARYCUTTERTWINDRV_GetVersion( )
{
	return( (ROTARYCUTTERTWINDRV_Major << 8) | ROTARYCUTTERTWINDRV_Minor );
}

