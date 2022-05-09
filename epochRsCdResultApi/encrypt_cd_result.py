import Crypto.Cipher.AES as AES
import Crypto.Util.Padding as Padding
from Crypto.Random import get_random_bytes
import base64
import os
import re

class encrypt:
    """Base class for data encryption - データの暗号化を行う基底クラス
    """
    def __init__(self):
        """constructor
        """
        self._ENCRYPT_KEY = os.environ['ENCRYPT_KEY'].encode()
        self._IV_LENG = 16
        self._PAD_BLOCK_SIZE = 16
        self._PAD_STYLE = 'pkcs7'

    def encrypt(self, strdata):
        """Encrypt the string

        Args:
            strdata (str): The string you want to encrypt - 暗号化したい文字列

        Returns:
            str: Encrypted string - 暗号化した文字列
        """
        iv = get_random_bytes(self._IV_LENG)
        aes = AES.new(self._ENCRYPT_KEY, AES.MODE_CBC, iv)
        encdata = iv + aes.encrypt(Padding.pad(strdata.encode(), self._PAD_BLOCK_SIZE, self._PAD_STYLE))
        return (base64.b64encode(encdata)).decode()

    def decrypt(self, encstrdata):
        """Decrypt the Encrypted string

        Args:
            encstrdata (str): Encrypted string - 暗号化した文字列

        Returns:
            str: Decrypted string - 復号した文字列
        """
        encdata = base64.b64decode(encstrdata.encode())
        iv = encdata[:self._IV_LENG]
        aes = AES.new(self._ENCRYPT_KEY, AES.MODE_CBC, iv)
        return Padding.unpad(aes.decrypt(encdata[self._IV_LENG:]), self._PAD_BLOCK_SIZE, self._PAD_STYLE).decode()


class encrypt_cd_result():
    def __init__(self):
        self._enc = encrypt()

    def encrypt(self, contents):
        ret_contents = contents.copy()

        if 'password' in ret_contents.get('workspace_info',{}).get('ci_config',{}).get('pipelines_common',{}).get('git_repositry',{}):
            ret_contents['workspace_info']['ci_config']['pipelines_common']['git_repositry']['password'] = self._enc.encrypt(ret_contents['workspace_info']['ci_config']['pipelines_common']['git_repositry']['password'])

        if 'token' in ret_contents.get('workspace_info',{}).get('ci_config',{}).get('pipelines_common',{}).get('git_repositry',{}):
            ret_contents['workspace_info']['ci_config']['pipelines_common']['git_repositry']['token'] = self._enc.encrypt(ret_contents['workspace_info']['ci_config']['pipelines_common']['git_repositry']['token'])

        if 'password' in ret_contents.get('workspace_info',{}).get('ci_config',{}).get('pipelines_common',{}).get('container_registry',{}):
            ret_contents['workspace_info']['ci_config']['pipelines_common']['container_registry']['password'] = self._enc.encrypt(ret_contents['workspace_info']['ci_config']['pipelines_common']['container_registry']['password'])

        if 'password' in ret_contents.get('workspace_info',{}).get('cd_config',{}).get('environments_common',{}).get('git_repositry',{}):
            ret_contents['workspace_info']['cd_config']['environments_common']['git_repositry']['password'] = self._enc.encrypt(ret_contents['workspace_info']['cd_config']['environments_common']['git_repositry']['password'])

        if 'token' in ret_contents.get('workspace_info',{}).get('cd_config',{}).get('environments_common',{}).get('git_repositry',{}):
            ret_contents['workspace_info']['cd_config']['environments_common']['git_repositry']['token'] = self._enc.encrypt(ret_contents['workspace_info']['cd_config']['environments_common']['git_repositry']['token'])

        return ret_contents


    def decrypt(self, encrypted_contents):

        ret_contents = encrypted_contents.copy()

        if 'password' in ret_contents.get('workspace_info',{}).get('ci_config',{}).get('pipelines_common',{}).get('git_repositry',{}):
            ret_contents['workspace_info']['ci_config']['pipelines_common']['git_repositry']['password'] = self._enc.decrypt(ret_contents['workspace_info']['ci_config']['pipelines_common']['git_repositry']['password'])

        if 'token' in ret_contents.get('workspace_info',{}).get('ci_config',{}).get('pipelines_common',{}).get('git_repositry',{}):
            ret_contents['workspace_info']['ci_config']['pipelines_common']['git_repositry']['token'] = self._enc.decrypt(ret_contents['workspace_info']['ci_config']['pipelines_common']['git_repositry']['token'])

        if 'password' in ret_contents.get('workspace_info',{}).get('ci_config',{}).get('pipelines_common',{}).get('container_registry',{}):
            ret_contents['workspace_info']['ci_config']['pipelines_common']['container_registry']['password'] = self._enc.decrypt(ret_contents['workspace_info']['ci_config']['pipelines_common']['container_registry']['password'])

        if 'password' in ret_contents.get('workspace_info',{}).get('cd_config',{}).get('environments_common',{}).get('git_repositry',{}):
            ret_contents['workspace_info']['cd_config']['environments_common']['git_repositry']['password'] = self._enc.decrypt(ret_contents['workspace_info']['cd_config']['environments_common']['git_repositry']['password'])

        if 'token' in ret_contents.get('workspace_info',{}).get('cd_config',{}).get('environments_common',{}).get('git_repositry',{}):
            ret_contents['workspace_info']['cd_config']['environments_common']['git_repositry']['token'] = self._enc.decrypt(ret_contents['workspace_info']['cd_config']['environments_common']['git_repositry']['token'])

        return ret_contents
