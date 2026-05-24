Docker image & registry troubleshooting
=====================================

When a container image (for example `kokoro-german-onnx:latest`) cannot be pulled you can either authenticate to a private registry or build the image locally.

Common steps
------------

- Authenticate to a registry (if the image is private):

```powershell
docker login
```

- Re-run the stack start after login:

```powershell
.venv\Scripts\offline-ai start
```

Building the Kokoro German ONNX image locally
---------------------------------------------

If you prefer to build the `kokoro-german-onnx:latest` image locally (project includes a local build path), run these commands from the repository root:

```powershell
cd app\docker\kokoro_german_onnx\onnx-docker
docker build -t kokoro-german-onnx:latest .
# Then re-run the stack
.venv\Scripts\offline-ai start
```

If your Kokoro image lives at a different path in your setup, update `settings.KOKORO_IMAGE` in your configuration or set `KOKORO_IMAGE` in your `.env` file to the correct tag.

Adjusting language-specific behavior
-----------------------------------

The orchestrator will select the German ONNX image when `APP_LANGUAGE` is set to `de`. To force English/CPU image, set `APP_LANGUAGE=en` or set `KOKORO_IMAGE` to a different tag in `.env`.

Example `.env` entries:

```
APP_LANGUAGE=de
KOKORO_IMAGE=kokoro-german-onnx:latest
```

If you want the orchestrator to always use the CPU Kokoro image instead of ONNX/GPU variants, set `KOKORO_IMAGE` to a known CPU image tag (for example `ghcr.io/remsky/kokoro-fastapi-cpu:latest`).

When to open an issue
---------------------

- If building the image fails due to missing source folders, verify the repository includes the `app/docker/kokoro_german_onnx` folder.
- If a registry returns access denied even after `docker login`, check the image name and registry host in `settings.KOKORO_IMAGE`.

Reference
---------
- Orchestrator code: app/docker/orchestrator.py
