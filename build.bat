@echo off

set "{{=setlocal enableDelayedExpansion&for %%a in (" & set "}}="::end::" ) do if "%%~a" neq "::end::" (set command=!command! %%a) else (call !command! & endlocal)"

%{{%
    python C:\Python39\Lib\site-packages\pyarmor/pyarmor.py pack
    -x " --advanced 2 --bootstrap 2 --enable-suffix --exclude helheim"
    -e "
	    --icon 'deployment/resources/Logo.ico'
        --add-data 'c:/Python39/lib/site-packages/helheim^;helheim'
        --add-data 'resources/bifrost.dll^;bifrost.dll'
        --add-binary 'c:/Python39/lib/site-packages/helheim/pytransform_vax_000061.pyd^;helheim'
        --add-data 'c:/Python39/lib/site-packages/cloudscraper^;cloudscraper'
        -c
        --onefile
        --hidden-import helheim
        --hidden-import cloudscraper
        --hidden-import cryptography
        --hidden-import polling2
        --hidden-import PIL
        --hidden-import PIL.Image
    "
    --name SourceRaffles
    srcs/__main__.py
%}}%
