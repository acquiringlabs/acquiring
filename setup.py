from setuptools import find_packages, setup

setup(
    name="django-acquiring",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    license="MIT License",
    description="Payment Orchestration Library for Django.",
    long_description=open("README.md").read(),
    url="https://github.com/acquiringlabs/django-acquiring",
    author="Alvaro Duran",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        "Django>=4.2",  # TODO Link to supported Django versions
    ],
)
