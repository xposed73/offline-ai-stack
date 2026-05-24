@echo off
setlocal
echo.
echo Building Kokoro German ONNX image (kokoro-german-onnx:latest)
echo.

if exist "app\docker\kokoro_german_onnx\onnx-docker\Dockerfile" (
    pushd "app\docker\kokoro_german_onnx\onnx-docker"
    echo Found Dockerfile, building image...
    docker build -t kokoro-german-onnx:latest .
    set BUILD_CODE=%ERRORLEVEL%
    popd
) else (
    echo ERROR: Dockerfile not found at app\docker\kokoro_german_onnx\onnx-docker\Dockerfile
    echo Ensure the repository includes the Kokoro build tree or set KOKORO_IMAGE in your .env to a different tag.
    exit /b 2
)

if %BUILD_CODE% neq 0 (
    echo Docker build failed with exit code %BUILD_CODE%.
    exit /b %BUILD_CODE%
)

echo Successfully built kokoro-german-onnx:latest

if /I "%1"=="start" (
    echo Restarting the stack now...
    call .venv\Scripts\offline-ai start
)

endlocal
exit /b 0
