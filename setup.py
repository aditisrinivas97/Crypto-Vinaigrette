import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

with open("requirements.txt", "r") as fh:
	install_requires = fh.read()

setuptools.setup(
	name="cryptovinaigrette",
	version="1.0.0",
	install_requires=install_requires,
	author="Aditi Srinivas, Avinash Shenoy <mailto:avi123shenoy@hotmail.com>",
	author_email="aditisrinivas97@gmail.com",
	description="A quantum resistent asymmetric key generation tool based on the rainbow scheme for digital signatures.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/aditisrinivas97/Crypto-Vinaigrette",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3.6",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
)