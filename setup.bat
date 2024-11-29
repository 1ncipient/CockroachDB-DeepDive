%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\python -m venv venv
venv\Scripts\python -m pip install uv
venv\Scripts\python -m uv clean
venv\Scripts\python -m uv pip install --upgrade pip
venv\Scripts\python -m uv pip install wheel
venv\Scripts\python -m uv pip install -r requirements.txt
venv\Scripts\activate