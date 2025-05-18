import os
import uvicorn
from handler import app

if __name__ == "__main__":
    port = int(os.getenv("port", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
