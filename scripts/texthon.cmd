@echo off
setlocal
rem so we can find texthon from the executing directory if setup.py was
rem not run
set PYTHONPATH=%PYTHONPATH%;%CD%
python %~dp0\texthon %*
