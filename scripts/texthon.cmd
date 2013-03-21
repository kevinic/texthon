@echo off
setlocal
rem so we can find texthon from the executing directory if setup.py was
rem not run
set PYTHONPATH=%PYTHONPATH%;%CD%
set PYTHONEXE=python
rem set PYTHONEXE=c:\Python27\python
%PYTHONEXE% %~dp0\texthon %*
