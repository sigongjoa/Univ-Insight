
import os

file_path = '전국대학및전문대학정보표준데이터.csv'

def convert_to_utf8(path):
    encodings = ['cp949', 'euc-kr', 'utf-8-sig', 'latin1']
    
    content = None
    detected_encoding = None
    
    for enc in encodings:
        try:
            with open(path, 'r', encoding=enc) as f:
                content = f.read()
            detected_encoding = enc
            print(f"Successfully read with encoding: {enc}")
            break
        except UnicodeDecodeError:
            continue
            
    if content is None:
        print("Failed to decode file with common encodings.")
        return

    # Write back as utf-8
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully converted {path} from {detected_encoding} to utf-8")
    except Exception as e:
        print(f"Error writing file: {e}")

if __name__ == "__main__":
    convert_to_utf8(file_path)
