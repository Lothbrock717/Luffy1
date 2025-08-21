from base64 import standard_b64encode, standard_b64decode


import base64


#def str_to_b64(__str: str) -> str:
#    str_bytes = __str.encode('ascii')
#    bytes_b64 = standard_b64encode(str_bytes)
#    b64 = bytes_b64.decode('ascii')
#    return b64


#def b64_to_str(b64: str) -> str:
#    bytes_b64 = b64.encode('ascii')
#    bytes_str = standard_b64decode(bytes_b64)
#    __str = bytes_str.decode('ascii')
#    return __str


def str_to_b64(text: str) -> str:
    """Encodes a string to Base64 without padding."""
    encoded_bytes = base64.b64encode(text.encode('utf-8'))
    encoded_str = encoded_bytes.decode('utf-8')
    return encoded_str.rstrip('=')

def b64_to_str(encoded_text: str) -> str:
    """Decodes a Base64 string (without padding) back to plain text."""
    # Add padding back if necessary
    padding_needed = 4 - (len(encoded_text) % 4)
    if padding_needed and padding_needed != 4:
        encoded_text += '=' * padding_needed
    decoded_bytes = base64.b64decode(encoded_text.encode('utf-8'))
    return decoded_bytes.decode('utf-8')
