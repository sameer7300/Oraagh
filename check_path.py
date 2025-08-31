import os
import sys

print("--- Python Path Diagnostic ---")
print(f"Current Working Directory: {os.getcwd()}")
print("\nPython Path (sys.path):")
for p in sys.path:
    print(p)
print("--- End of Diagnostic ---")
