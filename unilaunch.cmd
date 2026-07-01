@echo off

if "%1"=="-gs" (
    taskkill /FI "WINDOWTITLE eq Sector 8*" /F >nul 2>&1
    call se_env\Scripts\activate
    python shop.pyw
)
if "%1"=="-sg" (
    taskkill /FI "WINDOWTITLE eq Shop | Sector Eight*" /F >nul 2>&1
    call se_env\Scripts\activate
    python main.pyw
)
if "%1"=="-hs" (
    taskkill /FI "WINDOWTITLE eq Home | Sector 8*" /F >nul 2>&1
    call se_env\Scripts\activate
    python shop.pyw
)
if "%1"=="-sh" (
    taskkill /FI "WINDOWTITLE eq Shop | Sector 8*" /F >nul 2>&1
    call se_env\Scripts\activate
    python home.pyw
)
if "%1"=="-gh" (
    taskkill /FI "WINDOWTITLE eq Sector 8*" /F >nul 2>&1
    call se_env\Scripts\activate
    python home.pyw
)
if "%1"=="-hg" (
    taskkill /FI "WINDOWTITLE eq Home | Sector 8*" /F >nul 2>&1
    call se_env\Scripts\activate
    python main.pyw
)

