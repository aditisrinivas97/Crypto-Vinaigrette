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

Install the package using pip  (Pending..)

```
$ pip install crypto-vinaigrette
``` 

## Usage

1. Creating a key-pair. <br>

    The keys generated are stored in the current working directory.

    ```python
    import rainbowKeygen

    myKeyObject = rainbowKeygen()
    myKeyObject.generate_keys()
    ``` 

2. Signing a document. <br>

    Signing is done using the `Private Key`. Assuming the private key is named `rPriv.rkey` and the document to be signed is `testfile.txt`,
    
    ```python
    rainbowKeygen.sign('rPriv.rkey', 'testFile.txt')
    ``` 

3. Verifying the digital signature. <br>

    Verification is done using the `Public Key`. Assuming the public key is named `rPub.rkey` and the document whose signature is to be verified is `testfile.txt`,

    ```python
    check = rainbowKeygen.verify('rPub.rkey', signature, 'testFile.txt')

    if check == True :
        print("Verified successfully!")
    else :
        print("Invalid signature!")
    ``` 

## License

This project is made available under the [MIT License](http://www.opensource.org/licenses/mit-license.php).

## Primary Contributors

| | |
|:-:|:-:|
|<img src="https://github.com/aditisrinivas97.png" width="48">  | [Aditi Srinivas](https://github.com/aditisrinivas97) |
|<img src="https://github.com/avinashshenoy97.png" width="48">  | [Avinash Shenoy](https://github.com/avinashshenoy97) |