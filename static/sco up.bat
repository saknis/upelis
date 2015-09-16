C:\
cd "C:\Documents and Settings\nerijus\My Documents\kalvis\"
del all_sl.zip
del kalvis\static\all_sl.zip
rem c:\zip -r all_sl kalvis
7za.exe a all_sl.zip kalvis\
copy all_sl.zip "kalvis\static\all_sl.zip"
cd "C:\appengine131\"
appcfg.py --no_cookies --email=zzz@takas.lt update "C:\Documents and Settings\nerijus\My Documents\kalvis\kalvis"
pause