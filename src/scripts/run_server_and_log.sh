
#!/bin/bash
cd /mnt/d/progress/Univ-Insight
source .venv_wsl/bin/activate
pkill -f uvicorn
sleep 2
uvicorn src.api.main:app --host 0.0.0.0 --port 8001 > server.log 2>&1 &
echo "Server started. Tailing log..."
sleep 2
cat server.log
