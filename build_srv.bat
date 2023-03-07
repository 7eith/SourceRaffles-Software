@echo off

set "{{=setlocal enableDelayedExpansion&for %%a in (" & set "}}="::end::" ) do if "%%~a" neq "::end::" (set command=!command! %%a) else (call !command! & endlocal)"

%{{%
    pyarmor pack
    -x " --advanced 2 --bootstrap 2 --enable-suffix --exclude helheim"
    --clean
    -e "
        --onefile
	    --icon 'deployment/resources/Logo.ico'
        --add-data 'C:/Users/Administrator/AppData/Local/Programs/Python/Python39/Lib/site-packages/helheim^;helheim'
        --add-data 'C:/Users/Administrator/AppData/Local/Programs/Python/Python39/Lib/site-packages/pyfiglet^;pyfiglet'
        --add-binary 'C:/Users/Administrator/AppData/Local/Programs/Python/Python39/Lib/site-packages/helheim/pytransform_vax_000061.pyd^;helheim'
        --add-data 'C:/Users/Administrator/AppData/Local/Programs/Python/Python39/Lib/site-packages/cloudscraper^;cloudscraper'

        -c
        --hidden-import helheim
        --hidden-import Cryptodome
        --hidden-import msgpack
        --hidden-import cloudscraper
        --hidden-import cryptography
        --hidden-import numpy
        --hidden-import polling2
        --hidden-import PIL
        --hidden-import PIL.Image
	--hidden-import threadpoolctl
        --hidden-import pyfiglet
    "
    --name SourceRaffles
    srcs/__main__.py
%}}%
