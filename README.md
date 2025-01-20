# Holy Potatoes Tools - Command Line Tools

A command-line tool for managing save files and game data from Holy Potatoes! A Weapon Shop!

## Documentation

This project includes detailed technical documentation in `TechDocs.md` that explains:

- **WSREFData**: The game's primary reference data file
  - Data structure and loading process
  - Multi-language support
  - Implementation details

- **WSDir.txt**: Save directory index file
  - Purpose and structure
  - Save types and tracking
  - Technical implementation

- **Save Files**: Complete save system documentation
  - File types and formats
  - Save slots system
  - Backup mechanisms
  - Data structures

- **Encryption System**: Detailed encryption documentation
  - Save file encryption (Rijndael/AES)
  - Directory index encryption (String substitution)
  - Reference data encryption
  - Security considerations

For detailed technical information about the game's file formats and systems, please refer to `TechDocs.md`.

## Example Mod

This project includes an example mod in the `ExampleMod` folder that demonstrates how to add custom weapons to the game using BepInEx:

- **Features**:
  - Custom weapon implementation
  - Mod framework foundation
  - Integration with game's weapon system
  - Example of BepInEx plugin structure

- **Requirements**:
  - BepInEx 5.4 or later
  - Holy Potatoes! A Weapon Shop! (Tested On Steam Version)

- **Demo**:
  - Watch `ExampleMod.mp4` to see the mod in action
  - Shows custom weapon creation and usage
  - Demonstrates mod framework capabilities

The example mod serves as a starting point for creating your own mods and understanding the game's modding potential.

## Features

- **Save File Management**
  - Decrypt save files (WS_save*.txt) to readable JSON format
  - Encrypt modified JSON files back to game-compatible save files
  - Preserves exact game formatting for compatibility

- **WSDir Management**
  - View and edit WSDir.txt file contents
  - Decrypt WSDir.txt to JSON format
  - Encrypt modified WSDir data back to game format

- **Reference Data Extraction**
  - Extract and decrypt WSREFDATA from resources.assets
  - Save reference data in JSON format
  - Support for both .asset and .assets file extensions

## Installation

1. Make sure you have Python 3.8+ installed
2. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/hpaws-tools.git
   cd hpaws-tools/click_app
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Save Files

```bash
# Decrypt a save file
python cli.py save "C:\Path\To\WS_save1.txt" --decrypt
# Creates WS_save1.json in the same directory

# Encrypt a modified save file
python cli.py save "C:\Path\To\WS_save1.json" --encrypt
# Creates WS_save1.txt in the same directory
```

### WSDir Management

```bash
# Decrypt WSDir.txt
python cli.py wsdir "C:\Path\To\WSDir.txt" --decrypt
# Creates WSDir.json in the same directory

# Encrypt modified WSDir data
python cli.py wsdir "C:\Path\To\WSDir.json" --encrypt
# Creates WSDir.txt in the same directory
```

### Reference Data

```bash
# Extract reference data and automatically decrypts it
python cli.py asset "C:\Path\To\resources.assets" --extract
# Creates WSREFDATA.json in the same directory

# Encrypt modified reference data
python cli.py asset "C:\Path\To\WSREFDATA.json" --encrypt
# Creates WSREFDATA.bytes in the same directory
```

> **Note**: While this tool can create encrypted reference data files, you'll still need to use [UABEA (Unity Asset Bundle Extractor Avalonia)](https://github.com/nesrak1/UABEA) to insert them back into the resources.assets file. UABEA is a cross-platform tool for reading and writing Unity asset bundles and serialized files.

## Editing JSON Files

You can edit the extracted JSON files with any text editor of your choice. However, for the best experience with large JSON files, we recommend using [JSON Editor Online](https://jsoneditoronline.org/). This web-based editor offers:
- Visual tree view for easier navigation
- JSON validation and formatting
- Search and replace functionality
- Side-by-side comparison view
- Error detection and auto-repair

## File Locations

- Save files are typically located in: `%USERPROFILE%\Documents\SavedGames\`
- Game files are typically located in: `[Steam Directory]\steamapps\common\Holy Potatoes! A Weapon Shop!\HPAWS_Data\`

## Logging

The application maintains detailed logs in the `Logs` directory:
- All operations are logged to `Logs/Editor.log`
- Includes debug information, file sizes, and operation results
- Helpful for troubleshooting issues

## Technical Details

- Uses Rijndael encryption (ECB mode) for save files
- Custom string encryption for WSDir.txt
- UnityPy for assets file handling
- Exact JSON serialization matching game format

## Requirements

- Python 3.8+
- click>=8.1.7
- pythonnet==3.0.5
- UnityPy==1.20.17
- pycryptodome==3.19.0

## Safety Features

- Validation of file types and contents
- Detailed error messages and logging
- Non-destructive operations (creates new files instead of overwriting)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is released into the public domain under the [Unlicense](https://unlicense.org/). You can copy, modify, publish, use, compile, sell, or distribute this software, either in source code form or as a compiled binary, for any purpose, commercial or non-commercial, and by any means.

## Acknowledgments

- Thanks to the Holy Potatoes! A Weapon Shop! community
- Built with [Click](https://click.palletsprojects.com/) framework
- Uses [UnityPy](https://github.com/K0lb3/UnityPy) for Unity asset extraction 