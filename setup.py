from setuptools import find_packages, setup


setup(
    name="otillm",
    version="3.0.0",
    description="OtiLLM 3.0: Evidence-Native, Policy-Aware, Multimodal AI Runtime",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Oti Edema",
    packages=find_packages(),
    python_requires=">=3.9",
    include_package_data=True,
    install_requires=[],
    extras_require={
        "dev": ["pytest>=7.0"],
    },
)
