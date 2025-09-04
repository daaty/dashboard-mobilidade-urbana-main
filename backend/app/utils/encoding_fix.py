"""
Utilities to fix encoding issues in API responses.
This module provides functions to correct common encoding problems 
with Portuguese characters in API responses.
"""

def fix_encoding(text):
    """
    Fix common encoding issues with Portuguese characters.
    
    Args:
        text (str): The text with encoding issues
        
    Returns:
        str: The corrected text
    """
    if not isinstance(text, str):
        return text
        
    # Map of incorrectly encoded characters to their correct form
    encoding_map = {
        'Ã£': 'ã',
        'Ã¡': 'á',
        'Ã©': 'é',
        'Ãª': 'ê',
        'Ã³': 'ó',
        'Ã´': 'ô',
        'Ã§': 'ç',
        'Ãº': 'ú',
        'Ã¼': 'ü',
        'Ã­': 'í',
        'Ã': 'Á',
        'Ã‰': 'É',
        'Ãƒ': 'Ã',
        'Ãª': 'ê',
        'Ã"': 'Ó',
        'Ã"': 'Ô',
        'Ã‡': 'Ç',
        'Ãš': 'Ú',
        'ÃŠ': 'Ê',
        'Ã€': 'À',
        'Ã±': 'ñ',
        'â€™': "'",
        'â€"': "–",
        'â€"': "—",
        'â€œ': '"',
        'â€': '"'
    }
    
    for incorrect, correct in encoding_map.items():
        text = text.replace(incorrect, correct)
        
    return text

def fix_encoding_list(items):
    """
    Fix encoding for a list of strings
    
    Args:
        items (list): List of strings
        
    Returns:
        list: List with fixed encoding
    """
    if not isinstance(items, list):
        return items
    
    return [fix_encoding(item) for item in items]

def fix_encoding_dict(data):
    """
    Recursively fix encoding issues in a dictionary
    
    Args:
        data (dict): Dictionary with possible encoding issues
        
    Returns:
        dict: Dictionary with fixed encoding
    """
    if not isinstance(data, dict):
        return data
        
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = fix_encoding(value)
        elif isinstance(value, list):
            result[key] = [
                fix_encoding_dict(item) if isinstance(item, dict) 
                else fix_encoding(item) if isinstance(item, str)
                else item
                for item in value
            ]
        elif isinstance(value, dict):
            result[key] = fix_encoding_dict(value)
        else:
            result[key] = value
    
    return result

def fix_encoding_response(response_data):
    """
    DESABILITADO: Retorna response sem modificações para evitar Content-Length errors
    """
    return response_data
