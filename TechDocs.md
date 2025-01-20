# WSREFData Documentation

## Overview
`WSREFData` is the game's primary reference data file that contains all static game data in JSON format. The "WS" likely stands for "Weapon Shop" and "REF" stands for "Reference".

## Purpose
This file stores all reference/static data used by the game, including:
- Hero data (stats, descriptions)
- Dialogue data
- Item definitions
- Shop levels
- Furniture data
- Quest/objective data
- And much more

## Technical Details

### Loading Process
1. The file is loaded from the `Resources/Data/` directory
2. It's encrypted and needs to be decrypted using a specific key
3. The data is processed by `RefDataController.cs`
4. Different language versions exist:
   - WSREFDATA (English/Default)
   - WSREFDATA_GERMANY
   - WSREFDATA_RUSSIA
   - WSREFDATA_JAP
   - WSREFDATA_CHINESE
   - WSREFDATA_FRENCH
   - WSREFDATA_ITALIAN
   - WSREFDATA_SPANISH

### Data Structure
- Data is stored in a `ServerResponse` object
- Contains a `value` field that holds all reference data lists
- Each type of data is stored in its own list (e.g., `RefHero`, `RefDialogueNEW`, `RefItem`, etc.)

### Implementation
- The game loads this data at startup through `RefDataController.getRefDataFromFile()`
- Data is processed in coroutines to avoid freezing the game
- Each type of data is processed separately and stored in the `GameData` class for use during gameplay

## Usage
The data from this file is used throughout the game to:
- Define hero characteristics and behaviors
- Set up shop items and furniture
- Configure dialogue systems
- Establish game mechanics and rules
- Define quest objectives and rewards
- And manage various other game systems 

## WSDir.txt
`WSDir.txt` is the game's save directory index file that manages and tracks all save files and their timestamps.

### Purpose
- Acts as a master index/directory of all save files in the game
- Stores mappings between save file IDs and their timestamps
- Located at `MyDocuments/SavedGames/WSDir.txt`

### Structure
- Stores data as key-value pairs in the format: `saveID=timestamp;`
- Example: `autosaveLoad=timestamp;save1Load=timestamp;save2Load=timestamp;`
- The file is encrypted using the game's encryption system

### Save Types Tracked
- Autosaves (`autosaveLoad`)
- Manual saves (save1 through save5)
- Scenario-specific saves (e.g., `save1scenarioIDLoad`)

### Technical Implementation
- Loading: `Dictionary<string, string> saveDir = jsonFileController.loadSaveFileDir(game);`
- Saving: `jsonFileController.saveSaveFileDir(dictionary);`
- Includes a fallback system to PlayerPrefs if the file is missing or empty
- The game will recreate the file from PlayerPrefs data if needed

### Integration
- Used by the save/load system to display save slots in the UI
- Updated whenever a game is saved
- Used to verify save file existence and timestamps 

## Save Files
The game uses a sophisticated save system with multiple components and file types.

### Save File Types
1. **Game Save Files** (`WS_[saveName].txt`)
   - Contains the actual game state data
   - Encrypted using the key "e1n6c3dy4n9k2ey5"
   - Includes player data, shop state, heroes, weapons, etc.
   - Stored as JSON in a `ServerDynResponse` object

2. **Auto-saves**
   - Automatically created at certain points
   - Named `WS_autosave.txt`
   - Uses the same format as manual saves

3. **Scenario-specific Saves**
   - Special saves for different game scenarios
   - Named `WS_save[number][scenarioID].txt`
   - Allows separate save slots for different scenarios

### Save Slots
- 5 manual save slots (save1 through save5)
- 1 auto-save slot
- Each scenario has its own set of 5 save slots plus auto-save
- Save slots show:
  - Date and time of save
  - Current weather
  - Game progress information
  - Empty slots marked as "UNUSED"

### Technical Implementation
1. **Saving Process**:
   ```csharp
   // Create save data
   ServerDynValue serverDynValue = new ServerDynValue();
   // Populate with current game state
   serverDynValue.DynPlayer = player data
   serverDynValue.DynShop = shop data
   // etc...
   
   // Encrypt and save
   string jsonData = JsonMapper.ToJson(serverDynResponse);
   string encrypted = CommonAPI.Encrypt(jsonData, "e1n6c3dy4n9k2ey5");
   jsonFileController.saveContent("WS_" + saveName + ".txt", encrypted);
   ```

2. **Loading Process**:
   ```csharp
   // Read and decrypt save file
   string encrypted = jsonFileController.readContent("WS_" + saveName + ".txt");
   string decrypted = CommonAPI.Decrypt(encrypted, "e1n6c3dy4n9k2ey5");
   
   // Parse and load game state
   ServerDynResponse saveData = JsonMapper.ToObject<ServerDynResponse>(decrypted);
   // Process each component
   processDynamicPlayer(saveData.DynPlayer);
   processDynamicShop(saveData.DynShop);
   // etc...
   ```

### Backup System
- Save data is backed up to PlayerPrefs
- If a save file is corrupted or missing, the game can restore from PlayerPrefs
- The WSDir.txt file maintains an index of all saves and their timestamps

### Save Data Structure
The save files contain comprehensive game state data including:
- Player information (gold, stats, progress)
- Shop state (level, upgrades, inventory)
- Heroes (levels, equipment, stats)
- Weapons (crafted items, research progress)
- Quests and objectives
- Game world state (weather, time, events)
- Scenario-specific variables 

## Encryption System

The game uses multiple layers of encryption and encoding to protect various data files:

### 1. Save Files (WS_*.txt)
- **Algorithm**: Rijndael (AES)
- **Key**: "e1n6c3dy4n9k2ey5"
- **Mode**: ECB (Electronic Code Book)
- **Padding**: PKCS7
- **Process**:
  ```csharp
  // Saving:
  string jsonData = JsonMapper.ToJson(serverDynResponse);
  string encrypted = CommonAPI.Encrypt(jsonData, "e1n6c3dy4n9k2ey5");
  jsonFileController.saveContent("WS_" + saveName + ".txt", encrypted);
  
  // Loading:
  string encrypted = jsonFileController.readContent("WS_" + saveName + ".txt");
  string decrypted = CommonAPI.Decrypt(encrypted, "e1n6c3dy4n9k2ey5");
  ServerDynResponse data = JsonMapper.ToObject<ServerDynResponse>(decrypted);
  ```

### 2. Directory Index (WSDir.txt)
- Uses a custom string substitution cipher (SC class)
- **Dictionary**: "aAbcdEFgGijJklmnoOpPqrSUwXyZ234BCDfHIKMNQtuvWxz7@!#_=|}'68~`$%ehLRsTVY0159+{:?^&*()-/[];,<>.\"
- **References**: "aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ0123456789@~`!#$%^&*()_-=+/|[]{}';:,<>?.\\"
- **Process**:
  ```csharp
  // Encoding:
  char[] chars = input.ToCharArray();
  foreach(char c in chars) {
    int index = Array.IndexOf(References, c);
    if(index >= 0) {
      output += Dictionary[index];
    }
  }
  
  // Decoding:
  char[] chars = input.ToCharArray();
  foreach(char c in chars) {
    int index = Array.IndexOf(Dictionary, c);
    if(index >= 0) {
      output += References[index];
    }
  }
  ```
- Format: `key=value;` pairs for save file mappings
- Each character in the input is substituted with its corresponding character from the Dictionary based on its position in References
- Used for encoding save file timestamps and paths

### 3. Reference Data (WSREFData)
- Uses the same Rijndael encryption as save files
- **Key**: "e7nc3r2e6f8k2e0y"
- Loaded from Resources/Data directory
- Contains static game data in JSON format

### Technical Details
- **File Locations**:
  - Save Files: MyDocuments/SavedGames/
  - WSDir: MyDocuments/SavedGames/WSDir.txt
  - WSREFData: Resources/Data/

- **Backup System**:
  - PlayerPrefs serves as a backup for WSDir data
  - Files are copied to MyDocuments if found in persistent data path

- **Error Handling**:
  - Failed decryption falls back to PlayerPrefs
  - IO exceptions are logged but don't crash the game
  - Corrupted files trigger automatic backup restoration

### Security Notes
- ECB mode is used for simplicity but may not be ideal for security
- The encryption key is hardcoded in the executable
- The string substitution cipher for WSDir provides basic obfuscation
- The system focuses on preventing casual tampering rather than providing strong security 