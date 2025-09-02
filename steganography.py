import numpy as np
from PIL import Image

BITS_TO_CHANGE = 2

def encode(image_path: str, output_path: str, text: str):
    try:
        img = Image.open(image_path).convert("RGBA")
        pixels = np.asarray(img).copy()
    except FileNotFoundError:
        raise Exception(f"Error: The image file '{image_path}' was not found.")

    # Encode and Add Delimiter
    data = text.encode('utf-8') + b'###'
    
    total_data = len(data) * 8
    capacity = pixels.size * BITS_TO_CHANGE
    
    if total_data > capacity:
        raise Warning("Error: The message is too long to be encoded in this image.")

    mask = 0x100 - (1 << BITS_TO_CHANGE)

    data_index = 0
    complete = False

    for row in range(pixels.shape[0]):
        if complete: break
        
        for col in range(pixels.shape[1]):
            for channel in range(3):
                if data_index >= total_data:
                    complete = True
                    break
                
                # Determine which Bits to Encode
                byte_index, bit_in_byte_index = divmod(data_index, 8)
                
                enocded_bits = (data[byte_index] >> (8 - bit_in_byte_index - BITS_TO_CHANGE)) & ((1 << BITS_TO_CHANGE) - 1)

                pixels[row, col, channel] &= mask
                pixels[row, col, channel] |= enocded_bits
                
                data_index += BITS_TO_CHANGE

    # Create Encoded Image
    encoded_image = Image.fromarray(pixels)
    encoded_image.save(output_path)

def decode(image_path: str):
    try:
        img = Image.open(image_path).convert("RGB")
    except FileNotFoundError:
        return f"Error: The image file '{image_path}' was not found."

    pixels = np.asarray(img)
    
    extracted_bits = ""
    extracted_bytes = bytearray()
    
    for row in range(pixels.shape[0]):
        for col in range(pixels.shape[1]):
            for channel in range(3):
                # Extract Encoded Bits
                bits = pixels[row, col, channel] & ((1 << BITS_TO_CHANGE) - 1)
                
                # Append the Extracted Bits
                extracted_bits += format(bits, f'0{BITS_TO_CHANGE}b')

                # Process Full Bytes
                if len(extracted_bits) >= 8:
                    byte_to_append = int(extracted_bits[:8], 2)
                    extracted_bytes.append(byte_to_append)
                    
                    # Check for Delimiter at end of ByteArray
                    if extracted_bytes[-3:] == b'###':
                        try:
                            # Remove Delimiter and Decode
                            return extracted_bytes[:-3].decode('utf-8')
                        except UnicodeDecodeError:
                            raise Warning("Could not decode the message. It may be corrupted.")
                    
                    # Remove Processed Byte
                    extracted_bits = extracted_bits[8:]
    
    raise Warning("Could not find the message delimiter. The image may not contain a hidden message or it was corrupted.")

if __name__ == "__main__":
    
    message = "Hello, World! This is a secret message"
    encode("Assets/image.png", "Assets/encoded_image.png", message)

    decoded_message = decode("Assets/encoded_image.png")

    print(f"Decoded Message: {decoded_message}")
