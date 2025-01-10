from setuptools import setup, find_packages

setup(
    name="mistake-lang",
    version="0.1.0",
    author="Elliot",
    author_email="captainexpo@gmail.com",
    description="A Mistake",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Captainexpo-1/Mistake-Lang",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "mistake-lang=mistake.main:main",
        ],
    },
    install_requires=open("requirements.txt").readlines(),
)
