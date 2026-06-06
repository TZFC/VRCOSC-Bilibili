import os
import shutil
import subprocess

def main():
    print("Building React frontend...")
    os.chdir("frontend")
    subprocess.run(["npm", "install"], check=True, shell=True)
    subprocess.run(["npm", "run", "build"], check=True, shell=True)
    os.chdir("..")
    
    print("Copying built frontend to backend static directory...")
    # This assumes we want to serve frontend via FastAPI for the final .exe
    # Let's modify main.py to serve static files if dist exists
    if os.path.exists("backend/static"):
        shutil.rmtree("backend/static")
    shutil.copytree("frontend/dist", "backend/static")
    
    print("Building with PyInstaller...")
    os.chdir("backend")
    # We use --add-data to include the static files in the exe
    subprocess.run([
        "python", "-m", "PyInstaller", 
        "--name", "VRCOSC-Bilibili", 
        "--onedir", 
        "--windowed", 
        "--add-data", "static;static",
        "main.py"
    ], check=True)
    
    print("Build complete! Executable is in backend/dist/VRCOSC-Bilibili")

if __name__ == "__main__":
    main()
