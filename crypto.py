import json
import UnityPy
import clr
import os
import shutil

clr.AddReference('System.Security')
clr.AddReference('System.IO')

from System.Security.Cryptography import (
    RijndaelManaged,
    CipherMode,
    PaddingMode
)
from System.Text import Encoding
from System.IO import BinaryReader, BinaryWriter, MemoryStream
from System import Convert

from logger import get_logger
from utils import serialize_json

logger = get_logger(__name__)


class SaveCrypto:

    SAVE_KEY = "e1n6c3dy4n9k2ey5" 
    REFDATA_KEY = "e7nc3r2e6f8k2e0y" 

    BLOCK_SIZE = 128
    CIPHER_MODE = CipherMode.ECB
    PADDING_MODE = PaddingMode.PKCS7

    @staticmethod
    def _create_rijndael(key: str) -> RijndaelManaged:
        rijndael = RijndaelManaged()
        rijndael.Key = Encoding.UTF8.GetBytes(key)
        rijndael.Mode = SaveCrypto.CIPHER_MODE
        rijndael.Padding = SaveCrypto.PADDING_MODE
        rijndael.BlockSize = SaveCrypto.BLOCK_SIZE
        return rijndael

    @staticmethod
    def _decrypt_data(encrypted_str: str, key: str) -> str:
        rijndael = SaveCrypto._create_rijndael(key)
        encrypted = Convert.FromBase64String(encrypted_str)
        decryptor = rijndael.CreateDecryptor()
        decrypted = decryptor.TransformFinalBlock(
            encrypted,
            0,
            len(encrypted)
        )
        return Encoding.UTF8.GetString(decrypted)

    @staticmethod
    def _encrypt_data(data: str, key: str) -> str:
        rijndael = SaveCrypto._create_rijndael(key)
        bytes_to_encrypt = Encoding.UTF8.GetBytes(data)
        encryptor = rijndael.CreateEncryptor()
        encrypted = encryptor.TransformFinalBlock(
            bytes_to_encrypt,
            0,
            len(bytes_to_encrypt)
        )
        # Return base64 string directly, don't encode to bytes
        return Convert.ToBase64String(encrypted)

    @staticmethod
    def decrypt(
        data: bytes | str,
        key: str = None,
        filepath: str = None
    ) -> str:
        try:
            if filepath and (filepath.lower().endswith('.asset') or filepath.lower().endswith('.assets')):
                key = SaveCrypto.REFDATA_KEY
                encrypted_str = (
                    data if isinstance(data, str) else data.decode('utf-8')
                )
                encrypted_str = encrypted_str[len(encrypted_str) % 4:]
                return SaveCrypto._decrypt_data(encrypted_str, key)
            else:
                key = key or SaveCrypto.SAVE_KEY
                logger.debug("Decrypting save data...")
                logger.debug(f"Input data length: {len(data)} bytes")

                mem_stream = None
                binary_reader = None
                try:
                    mem_stream = MemoryStream(data)
                    binary_reader = BinaryReader(mem_stream)
                    encrypted_str = binary_reader.ReadString()
                    logger.debug(f"Read string length: {len(encrypted_str)}")

                    result = SaveCrypto._decrypt_data(encrypted_str, key)
                    logger.debug("Successfully decoded using UTF8")

                    sample_size = min(200, len(result))
                    logger.debug(
                        f"First {sample_size} chars of decrypted data: "
                        f"{result[:sample_size]}"
                    )

                    return result
                finally:
                    if binary_reader:
                        binary_reader.Close()
                    if mem_stream:
                        mem_stream.Close()

        except Exception as e:
            error_type = (
                "WSREF" if filepath and (filepath.lower().endswith('.asset') or filepath.lower().endswith('.assets'))
                else "save"
            )
            logger.error(f"Error decrypting {error_type} data: {str(e)}")
            raise

    @staticmethod
    def encrypt(
        data: str,
        key: str = None,
        filepath: str = None
    ) -> bytes:
        try:
            if filepath and (filepath.lower().endswith('.asset') or filepath.lower().endswith('.assets')):
                key = SaveCrypto.REFDATA_KEY
                result = SaveCrypto._encrypt_data(data, key)
                # For assets files, return bytes directly
                return result.encode('utf-8')
            else:
                key = key or SaveCrypto.SAVE_KEY
                logger.debug("Encrypting text...")
                logger.debug(f"Raw data length: {len(data)} bytes")

                result = SaveCrypto._encrypt_data(data, key)
                logger.debug(f"UTF8 bytes length: {len(data)} bytes")

                mem_stream = None
                binary_writer = None
                try:
                    mem_stream = MemoryStream()
                    binary_writer = BinaryWriter(mem_stream)
                    binary_writer.Write(result)
                    binary_writer.Flush()
                    mem_stream.Position = 0
                    output = bytes(mem_stream.ToArray())

                    logger.debug(f"Final output length: {len(output)} bytes")
                    return output
                finally:
                    if binary_writer:
                        binary_writer.Close()
                    if mem_stream:
                        mem_stream.Close()

        except Exception as e:
            error_type = (
                "WSREF" if filepath and (filepath.lower().endswith('.asset') or filepath.lower().endswith('.assets'))
                else "save"
            )
            logger.error(f"Error encrypting {error_type} data: {str(e)}")
            raise

    @staticmethod
    def extract_refdata(
        file_data: bytes | str,
        filename: str = None
    ) -> tuple[dict, str]:
        try:
            if not filename or not (filename.lower().endswith('.asset') or filename.lower().endswith('.assets')):
                raise ValueError("Please select a resources.asset or resources.assets file")

            env = UnityPy.load(file_data) 
            logger.debug("Loaded assets file")

            wsrefdata = None
            for obj in env.objects:
                if obj.type.name == "TextAsset":
                    data = obj.read()
                    logger.debug(f"  Name: {data.m_Name}")
                    if data.m_Name == "WSREFDATA":
                        logger.debug("Found WSREFDATA!")
                        wsrefdata = data
                        break

            if not wsrefdata:
                raise ValueError("Could not find WSREFDATA in assets file")

            encrypted_bytes = wsrefdata.m_Script
            decrypted_json = SaveCrypto.decrypt(
                encrypted_bytes,
                filepath=filename
            )

            return json.loads(decrypted_json), wsrefdata.m_Name

        except Exception as e:
            logger.error(f"Error extracting reference data: {str(e)}")
            raise

    @staticmethod
    def update_refdata(file_path: str, new_data: dict) -> None:
        """Update WSREFDATA in assets file with new encrypted data"""
        logger.debug(f"Creating backup at {file_path}.backup")
        if not os.path.exists(f"{file_path}.backup"):
            shutil.copy2(file_path, f"{file_path}.backup")
        
        # Encrypt the new data first using custom serializer
        encrypted_data = SaveCrypto.encrypt(serialize_json(new_data, in_game_data=True), SaveCrypto.REFDATA_KEY)
        
        # Load and modify the assets file
        logger.debug(f"open file: {file_path}")
        env = UnityPy.load(file_path)
        logger.debug("Loaded assets file")

        # Find and update WSREFDATA TextAsset
        for obj in env.objects:
            if obj.type.name == "TextAsset":
                data = obj.read()
                if data.m_Name == "WSREFDATA":
                    # Update the script content directly
                    data.m_Script = encrypted_data
                    data.save()  # Save changes back to the object
                    logger.debug("Updated WSREFDATA content")
                    break

        # Save the modified file with original packer
        with open(file_path, "wb") as f:
            f.write(env.file.save(packer="original"))
        logger.debug("Saved modified assets file")
    
