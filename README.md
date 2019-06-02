# Crypto-Vinaigrette
[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)]()
![Status](https://img.shields.io/badge/status-active-brightgreen.svg?style=flat)
[![License](https://img.shields.io/badge/license-mit-brightgreen.svg?style=flat)](https://github.com/aditisrinivas97/Crypto-Vinaigrette/blob/master/LICENSE)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/Django.svg)

A quantum resistent asymmetric key generation tool based on the rainbow scheme for digital signatures.

## Why would you need this?

![Auth Comic](https://github.com/aditisrinivas97/Crypto-Vinaigrette/blob/master/extras/identity.png)

Digital signatures are a common way of authenticating a sender by verifying a piece of information attached to the document. In our case, the attached piece of information is a sequence of numbers generated using the document which is to be signed. <br>

As mentioned before, we employ the Generalised Unbalanced Oil and Vinegar scheme or the Rainbow scheme to achieve the same. <br>

You can find the paper here : https://bit.ly/2vwckRw


## Installing

To build and install cryptovinaigrette, run the following commands
```
$ git clone https://github.com/aditisrinivas97/Crypto-Vinaigrette
$ cd Crypto-Vinaigrette
$ python3 setup.py install
```

Or install the package using pip  (Pending..)

```
$ pip install cryptovinaigrette
``` 

## Usage

1. Creating a key-pair. <br>

    The keys generated are stored in the directory passed as parameter to generate_keys.

    ```python
    from cryptovinaigrette import cryptovinaigrette

    # Initialise keygen object and generate keys
    myKeyObject = cryptovinaigrette.rainbowKeygen(save="/path/to/dest/folder")
    ``` 

2. Signing a document. <br>

    Signing is done using the `Private Key`. Assuming the private key is named `cvPriv.pem` and the document to be signed is `testfile.txt`,
    
    ```python
    signature = cryptovinaigrette.rainbowKeygen.sign('cvPriv.pem', 'test/testFile.txt')
    ``` 

3. Verifying the digital signature. <br>

    Verification is done using the `Public Key`. Assuming the public key is named `cvPub.pub` and the document whose signature is to be verified is `testfile.txt`,

    ```python

    # Case where signature is valid
    check = cryptovinaigrette.rainbowKeygen.verify('cvPub.pub', signature, 'test/testFile.txt')

    # Case where signature is invalid 
    check = cryptovinaigrette.rainbowKeygen.verify('cvPub.pub', signature, 'test/testFile2.txt')

    if check == True :
        print("Verified successfully!")
    else :
        print("Signature does not match the file!")
    ``` 

## Example

![Example](https://github.com/aditisrinivas97/Crypto-Vinaigrette/blob/master/extras/example.png)

## License

This project is made available under the [MIT License](http://www.opensource.org/licenses/mit-license.php).

## Primary Contributors

| | |
|:-:|:-:|
|<img src="https://github.com/aditisrinivas97.png" width="48">  | [Aditi Srinivas](https://github.com/aditisrinivas97) |
|<img src="https://github.com/avinashshenoy97.png" width="48">  | [Avinash Shenoy](https://github.com/avinashshenoy97) |