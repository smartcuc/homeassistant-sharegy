robocopy "c:\Users\Public\Dev\eswes" "\\tsclient\C\temp\dev-pc\eswes" *.py /S /XD venv .git frontend
robocopy "c:\Users\Public\Dev\eswes" "\\tsclient\C\temp\dev-pc\eswes" .env*
robocopy "c:\Users\Public\Dev\eswes\frontend" "\\tsclient\C\temp\dev-pc\eswes\frontend" *.*
robocopy "c:\Users\Public\Dev\eswes\frontend\src" "\\tsclient\C\temp\dev-pc\eswes\frontend\public" *.* /S 
robocopy "c:\Users\Public\Dev\eswes\frontend\src" "\\tsclient\C\temp\dev-pc\eswes\frontend\src" *.* /S 
tree > projekt.txt
