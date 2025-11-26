
import sys
import os
import uvicorn
import traceback

# Add project root to path
sys.path.append(os.getcwd())

if __name__ == "__main__":
    try:
        print("🚀 Starting server debug...")
        from src.api.main import app
        print("✅ App imported successfully.")
        uvicorn.run(app, host="0.0.0.0", port=8001)
    except Exception:
        print("❌ Server crashed!")
        with open("server_error.log", "w") as f:
            traceback.print_exc(file=f)
        traceback.print_exc()
