from setuptools import setup, find_packages

setup(
    name="drill_map_ai",
    version="0.1.0",
    description="Drill Map AI 模組",
    author="你的名字",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "torch",
        "cnocr",
        "opencv-python",
        "autogluon.tabular",
        "scipy",
        "Pillow",
        # ...其他相依套件...
    ],
    python_requires=">=3.8",
)