import click
import json
import os
from crypto import SaveCrypto
from string_crypto import StringCrypto
from utils import serialize_json
from logger import setup_logging, get_logger

# Setup logging
log_file = setup_logging()
logger = get_logger(__name__)

@click.group()
def cli():
    """Holy Potatoes Tools - Command line utilities for Holy Potatoes! A Weapon Shop!"""
    logger.info("Starting Holy Potatoes Tools CLI")
    pass

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path(), required=False)
@click.option('--encrypt/--decrypt', default=False, help='Encrypt or decrypt the save file')
def save(input_file, output_file, encrypt):
    """Encrypt or decrypt save files.
    
    INPUT_FILE: Path to the input save file
    OUTPUT_FILE: Optional path where the result will be saved. If not provided:
    - When decrypting: saves as [original_name].json in the same directory
    - When encrypting: saves as [original_name without .json].txt in the same directory
    """
    try:
        logger.info(f"Processing save file: {input_file}")
        logger.info(f"Operation: {'encrypt' if encrypt else 'decrypt'}")
        
        # Generate default output path if not provided
        if not output_file:
            input_dir = os.path.dirname(input_file)
            input_name = os.path.basename(input_file)
            if encrypt:
                # Remove .json if present and add .txt
                output_name = os.path.splitext(input_name)[0]
                if not output_name.endswith('.txt'):
                    output_name += '.txt'
            else:
                # Remove .txt if present and add .json
                output_name = os.path.splitext(input_name)[0] + '.json'
            output_file = os.path.join(input_dir, output_name)
            logger.info(f"Using default output path: {output_file}")
            
        with open(input_file, 'rb') as f:
            data = f.read()
            logger.debug(f"Read {len(data)} bytes from input file")
            
        if encrypt:
            # Load JSON, serialize and encrypt
            with open(input_file, 'r') as f:
                json_data = json.load(f)
            # Use serialize_json to format data exactly like the game
            json_str = serialize_json(json_data)
            encrypted = SaveCrypto.encrypt(json_str)
            with open(output_file, 'wb') as f:
                f.write(encrypted)
            logger.info("Successfully encrypted save file")
            click.echo(f"Encrypted save file written to {output_file}")
        else:
            # Decrypt and save as JSON
            decrypted = SaveCrypto.decrypt(data)
            decrypted_data = json.loads(decrypted)
            # Use serialize_json to format data exactly like the game
            with open(output_file, 'w') as f:
                json_str = serialize_json(decrypted_data)
                f.write(json_str)
            logger.info("Successfully decrypted save file")
            click.echo(f"Decrypted save file written to {output_file}")
            
    except Exception as e:
        logger.error(f"Error processing save file: {str(e)}", exc_info=True)
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path(), required=False)
@click.option('--encrypt/--decrypt', default=False, help='Encrypt or decrypt the WSDir file')
def wsdir(input_file, output_file, encrypt):
    """Encrypt or decrypt WSDir files.
    
    INPUT_FILE: Path to the input WSDir file
    OUTPUT_FILE: Optional path where the result will be saved. If not provided:
    - When decrypting: saves as WSDir.json in the same directory
    - When encrypting: saves as WSDir.txt in the same directory
    """
    try:
        logger.info(f"Processing WSDir file: {input_file}")
        logger.info(f"Operation: {'encrypt' if encrypt else 'decrypt'}")
        
        # Generate default output path if not provided
        if not output_file:
            input_dir = os.path.dirname(input_file)
            if encrypt:
                output_file = os.path.join(input_dir, 'WSDir.txt')
            else:
                output_file = os.path.join(input_dir, 'WSDir.json')
            logger.info(f"Using default output path: {output_file}")
            
        if encrypt:
            # Load JSON, encrypt and save
            with open(input_file, 'r') as f:
                json_data = json.load(f)
            StringCrypto.save_wsdir(json_data, output_file)
            logger.info("Successfully encrypted WSDir file")
            click.echo(f"Encrypted WSDir file written to {output_file}")
        else:
            # Decrypt and save as JSON
            decrypted = StringCrypto.load_wsdir(input_file)
            with open(output_file, 'w') as f:
                json.dump(decrypted, f, indent=2)
            logger.info("Successfully decrypted WSDir file")
            click.echo(f"Decrypted WSDir file written to {output_file}")
            
    except Exception as e:
        logger.error(f"Error processing WSDir file: {str(e)}", exc_info=True)
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

def repair_json(content: str) -> str:
    """Clean and repair JSON content."""
    # Remove BOM if present
    if content.startswith('\ufeff'):
        content = content[1:]
    
    # Remove control characters except newlines and tabs
    content = ''.join(char for char in content if char >= ' ' or char in '\n\t')
    
    # Fix common JSON issues
    content = content.replace('\r\n', '\n')  # Normalize line endings
    content = content.replace('\\u0000', '')  # Remove null characters
    
    return content

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path(), required=False)
@click.option('--extract/--encrypt', default=True, help='Whether to extract reference data from assets file or encrypt JSON back to reference data format')
def asset(input_file, output_file, extract):
    """Process reference data from resources.assets file"""
    logger.info(f"Processing reference data: {input_file}")
    logger.info(f"Operation: {'extract' if extract else 'encrypt'}")

    try:
        if extract:
            with open(input_file, 'rb') as f:
                data, name = SaveCrypto.extract_refdata(f.read(), input_file)
            
            output_path = os.path.join(os.path.dirname(input_file), f"{name}.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                # Use custom serializer to match game format for both decryption and encryption
                json_str = serialize_json(data, in_game_data=True)
                f.write(json_str)
            
            logger.info(f"Saved extracted reference data to {output_path}")
        else:
            # For encryption, read and parse the JSON first
            with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Clean control characters and repair JSON
            content = repair_json(content)
            
            try:
                data = json.loads(content)
                logger.info("Successfully loaded JSON")
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {str(e)}")
                raise
            
            output_path = os.path.join(os.path.dirname(input_file), "WSREFDATA.bytes")
            with open(output_path, 'wb') as f:
                # Use custom serializer for both decryption and encryption
                json_str = serialize_json(data, in_game_data=True)
                f.write(SaveCrypto.encrypt(json_str))
            
            logger.info(f"Saved encrypted reference data to {output_path}")

    except Exception as e:
        logger.error(f"Error processing reference data: {str(e)}")
        raise ValueError(str(e))

if __name__ == '__main__':
    cli() 