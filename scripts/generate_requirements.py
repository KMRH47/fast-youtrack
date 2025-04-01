from src.version import DEPENDENCIES
import re

def pin_version(requirement):
    match = re.match(r"([^><=]+)>=([^,]+)", requirement)
    if match:
        package, version = match.groups()
        return f"{package}=={version}"
    return requirement

dev_deps = ["flake8==7.1.1", "setuptools>=68.0.0"]

with open("requirements.txt", "w") as f:
    for dep in dev_deps:
        f.write(f"{dep}\n")

    for dep in DEPENDENCIES:
        f.write(f"{pin_version(dep)}\n")

print("requirements.txt generated successfully")
