'''Autogenerated by xml_generate script, do not edit!'''
from OpenGL import platform as _p, arrays
# Code generation uses this
from OpenGL.raw.WGL import _types as _cs
# End users want this...
from OpenGL.raw.WGL._types import *
from OpenGL.raw.WGL import _errors
from OpenGL.constant import Constant as _C

import ctypes
_EXTENSION_NAME = 'WGL_NV_present_video'
def _f( function ):
    return _p.createFunction( function,_p.PLATFORM.WGL,'WGL_NV_present_video',error_checker=_errors._error_checker)
WGL_NUM_VIDEO_SLOTS_NV=_C('WGL_NUM_VIDEO_SLOTS_NV',0x20F0)
@_f
@_p.types(_cs.BOOL,_cs.HDC,_cs.c_uint,_cs.HVIDEOOUTPUTDEVICENV,ctypes.POINTER(_cs.c_int))
def wglBindVideoDeviceNV(hDc,uVideoSlot,hVideoDevice,piAttribList):pass
@_f
@_p.types(_cs.c_int,_cs.HDC,ctypes.POINTER(_cs.HVIDEOOUTPUTDEVICENV))
def wglEnumerateVideoDevicesNV(hDc,phDeviceList):pass
@_f
@_p.types(_cs.BOOL,_cs.c_int,ctypes.POINTER(_cs.c_int))
def wglQueryCurrentContextNV(iAttribute,piValue):pass
