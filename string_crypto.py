import os
import clr
from System import Array, String, Char
from System.IO import (
    BinaryWriter,
    BinaryReader,
    FileStream,
    FileMode,
)
from logger import get_logger

clr.AddReference('System.IO')
clr.AddReference('System')

logger = get_logger(__name__)


class StringCrypto:
    DICTIONARY = String(
        "aAbcdEFgGijJklmnoOpPqrSUwXyZ234BCDfHIKMNQtuvWxz7@!#_=|}'68~`$%"
        "ehLRsTVY0159+{:?^&*()-/[];,<>.\\"
    ).ToCharArray()
    
    REFERENCES = String(
        "aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ0123456789"
        "@~`!#$%^&*()_-=+/|[]{}';:,<>?.\\"
    ).ToCharArray()

    @staticmethod
    def encode(input_str):
        """Encrypts a string using the same character substitution as the game."""
        if not isinstance(input_str, str):
            array = input_str.ToCharArray()
        else:
            array = String(input_str).ToCharArray()

        text = String.Empty
        for i in range(len(array)):
            num = -1
            for c in StringCrypto.REFERENCES:
                num += 1
                if array[i] == c:
                    array[i] = StringCrypto.DICTIONARY[num]
                    num = -1
                    break
            text += array[i]
        return str(text)

    @staticmethod
    def decode(input_str):
        """Decrypts a string using the same character substitution as the game."""
        if not isinstance(input_str, str):
            array = input_str.ToCharArray()
        else:
            array = String(input_str).ToCharArray()

        text = String.Empty
        for i in range(len(array)):
            num = -1
            for c in StringCrypto.DICTIONARY:
                num += 1
                if array[i] == c:
                    array[i] = StringCrypto.REFERENCES[num]
                    num = -1
                    break
            text += array[i]
        return str(text)

    @staticmethod
    def save_wsdir(save_paths, filepath):
        """Saves the WSDir.txt file with encrypted save file paths.

        Args:
            save_paths (dict): Dictionary of save names to file paths
            filepath (str): Path where to save the WSDir.txt file
        """
        required_slots = {
            "autosaveLoad": "",
            "save1Load": "",
            "save2Load": "",
            "save3Load": "",
            "save4Load": "",
            "save5Load": "",
        }

        for key in save_paths.keys():
            if key.startswith(("save", "autosave")) and key.endswith("Load"):
                required_slots[key] = ""

        required_slots.update(save_paths)

        content = String.Empty
        for k, v in required_slots.items():
            if not isinstance(k, str) or not isinstance(v, str):
                raise ValueError("Both keys and values must be strings")
            content += f"{k}={v};"

        encrypted = StringCrypto.encode(content)

        fs = None
        writer = None
        try:
            fs = FileStream(filepath, FileMode.Create)
            writer = BinaryWriter(fs)
            writer.Write(String(encrypted))
        finally:
            if writer:
                writer.Close()
            if fs:
                fs.Close()

    @staticmethod
    def load_wsdir(filepath):
        """Loads and decrypts the WSDir.txt file.

        Args:
            filepath (str): Path to the WSDir.txt file

        Returns:
            dict: Dictionary of save names to file paths
        """
        if not os.path.exists(filepath):
            return {}
       
        fs = None
        reader = None
        try:
            fs = FileStream(filepath, FileMode.Open)
            reader = BinaryReader(fs)

            length = fs.Length
            bytes_array = Array.CreateInstance(Char, int(length))
            reader.Read(bytes_array, 0, int(length))
            encrypted = String(bytes_array)

            decrypted = StringCrypto.decode(encrypted)

            result = {}
            pairs = String(decrypted).Split(Array[Char]([';']))
            for pair in pairs:
                if String(pair).Contains('='):
                    key_value = String(pair).Split(Array[Char](['=']))
                    if len(key_value) == 2:
                        result[str(key_value[0])] = str(key_value[1])
            return result
        finally:
            if reader:
                reader.Close()
            if fs:
                fs.Close() 