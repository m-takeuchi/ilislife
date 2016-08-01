#!/usr/bin/env python3
# coding=utf-8
from Crypto.PublicKey import RSA
from Crypto import Random
import os,sys

random_func = Random.new().read
rsa = RSA.generate(2048, random_func)

def get_id_rsa(id_rsa_file, passphrase=None):
    with open(id_rsa_file, 'rb') as f:
        id_rsa = RSA.importKey(f.read())
    return id_rsa

def get_id_rsa_pub(id_rsa_pub_file, passphrase=None):
    with open(id_rsa_pub_file, 'rb') as f:
        id_rsa_pub = RSA.importKey(f.read())
        # id_rsa_pub = RSA.pudkey(f.read())
    return id_rsa_pub


def make_id_rsa(passphrase=None):
    # 秘密鍵作成
    # private_key = rsa.exportKey(format='PEM', passphrase='hogehoge')
    private_key = rsa.exportKey(format='PEM', passphrase=passphrase)
    with open('id_rsa', 'wb') as f:
        f.write(private_key)

def make_id_rsa_pub(id_rsa_file, pasphrase=None):
    id_rsa = get_id_rsa(id_rsa_file)
    # print(id_rsa)
    public_pem = id_rsa.publickey().exportKey()
    # print(public_pem)
    with open('id_rsa.pub', 'wb') as f:
        f.write(public_pem)


def encrypt(id_rsa_pub_file, plain_text_file, encrypted_text_file):
# # 公開鍵による暗号化
    id_rsa_pub = get_id_rsa_pub(id_rsa_pub_file)
    print(id_rsa_pub)
    with open(plain_text_file, 'r') as f:
        plain_text = f.read()
    with open(encrypted_text_file, 'wb') as f2:
        # f2.write(id_rsa_pub.publickey().encrypt(plain_text, random_func)[0])
        f2.write(id_rsa_pub.encrypt(plain_text, random_func)[0])
#
# # 秘密鍵による復号化
# with open('cipher.txt', 'r') as f:
#     with open('plain_decoded.txt', 'w') as f2:
#         f2.write(RSA.importKey(private_pem, 'hogehoge').decrypt(f.read()))
#
# # 秘密鍵による電子署名の作成
# with open('file.txt', 'r') as f:
#     with open('signature.bin', 'w') as f2:
#         f2.write(str(RSA.importKey(private_pem, 'hogehoge').sign(f.read(), random_func)[0]))
#
# # 公開鍵による電子署名の検証
# with open('signature.bin', 'r') as f:
#     with open('file.txt', 'r') as f2:
#         rsa.verify(f2.read(), (long(f.read()),))

if __name__ == '__main__':

    HOME = os.path.expanduser('~')
    RSA_FILES = {'PRV': HOME+'/.ssh/id_rsa', 'PUB':HOME+'/.ssh/id_rsa.pub'}
    print(os.path.expanduser(HOME+'/.ssh/'), HOME+RSA_FILES['PRV'], HOME+RSA_FILES['PUB'])
    SSH = os.path(HOME+'/.ssh/')
    if not SSH:
        print('No '+HOME+'/.ssh/ dir. '+'Making .ssh/ dir in your HOME.)
        os.mkdir(SSH)
        input_gmail_password = input('Please input gmail password>>>  ')
    # if not os.path(RSA_FILES['PRV']):
    #     make_id_rsa(RSA_FILES['PRV'])
    # if not os.path(RSA_FILES['PUB']):
    #     make_id_rsa_pub(RSA_FILES['PUB'])
    # print(get_id_rsa('id_rsa'))
    # print(get_id_rsa_pub('id_rsa.pub'))
    # encrypt(RSA_FILES['PUB'], input_gmail_password, 'pass.rsa')
