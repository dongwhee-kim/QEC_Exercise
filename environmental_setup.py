import os
import sys

def install_package(package):
    print(f"Installing {package}...")
    command = f'"{sys.executable}" -m pip install {package}'
    print(f"Executing: {command}")
    result = os.system(command)
    
    if result != 0:
        print(f"ERROR: Failed to install {package}. Exiting.")
        sys.exit(1)
    else:
        print(f"Successfully installed {package}\n")

# Package list
packages = [
    "qiskit==2.1.2",
    "matplotlib==3.10.0",
    "pylatexenc",
    "qiskit-aer==0.17.1",
    "numpy==2.0.2",
    "qiskit_ibm_runtime==0.41.1"
]

print("Starting environmental setup...")

# Install package
for pkg in packages:
    install_package(pkg)

print("All specified packages have been processed successfully.")