@echo off
echo Running script to create documentation

echo installing latest libtaxii
cd ..
call python setup.py install
cd docs
echo done installing latest libtaxii

echo Starting apidoc.bat
call apidoc.bat
echo apidoc.bat done

echo Starting make.bat
call make.bat html
echo make.bat done

echo complete