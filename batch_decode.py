# 依赖pycrypto库
import binascii
import struct
import base64
import json
import os
from Crypto.Cipher import AES
import traceback


def dump(file_name, file_path, save_to_sub_folder):
    core_key = binascii.a2b_hex("687A4852416D736F356B496E62617857")
    meta_key = binascii.a2b_hex("2331346C6A6B5F215C5D2630553C2728")
    unpad = lambda s : s[0:-(s[-1] if type(s[-1]) == int else ord(s[-1]))]
    f = open(file_path,'rb')
    header = f.read(8)
    assert binascii.b2a_hex(header) == b'4354454e4644414d'
    f.seek(2, 1)
    key_length = f.read(4)
    key_length = struct.unpack('<I', bytes(key_length))[0]
    key_data = f.read(key_length)
    key_data_array = bytearray(key_data)
    for i in range (0,len(key_data_array)): key_data_array[i] ^= 0x64
    key_data = bytes(key_data_array)
    cryptor = AES.new(core_key, AES.MODE_ECB)
    key_data = unpad(cryptor.decrypt(key_data))[17:]
    key_length = len(key_data)
    key_data = bytearray(key_data)
    key_box = bytearray(range(256))
    c = 0
    last_byte = 0
    key_offset = 0
    for i in range(256):
        swap = key_box[i]
        c = (swap + last_byte + key_data[key_offset]) & 0xff
        key_offset += 1
        if key_offset >= key_length: key_offset = 0
        key_box[i] = key_box[c]
        key_box[c] = swap
        last_byte = c
    meta_length = f.read(4)
    meta_length = struct.unpack('<I', bytes(meta_length))[0]
    meta_data = f.read(meta_length)
    meta_data_array = bytearray(meta_data)
    for i in range(0,len(meta_data_array)): meta_data_array[i] ^= 0x63
    meta_data = bytes(meta_data_array)
    meta_data = base64.b64decode(meta_data[22:])
    cryptor = AES.new(meta_key, AES.MODE_ECB)
    meta_data = unpad(cryptor.decrypt(meta_data)).decode('utf-8')[6:]
    meta_data = json.loads(meta_data)
    crc32 = f.read(4)
    crc32 = struct.unpack('<I', bytes(crc32))[0]
    f.seek(5, 1)
    image_size = f.read(4)
    image_size = struct.unpack('<I', bytes(image_size))[0]
    image_data = f.read(image_size)
    file_name = file_name.replace('.ncm', '') + '.' + meta_data['format']
    m = open(os.path.join(os.path.split(file_path)[0],save_to_sub_folder,file_name),'wb')
    chunk = bytearray()
    while True:
        chunk = bytearray(f.read(0x8000))
        chunk_length = len(chunk)
        if not chunk:
            break
        for i in range(1,chunk_length+1):
            j = i & 0xff;
            chunk[i-1] ^= key_box[(key_box[j] + key_box[(key_box[j] + j) & 0xff]) & 0xff]
        m.write(chunk)
    m.close()
    f.close()


def process(base_path):
    if not os.path.exists(base_path):
        print('** ERROR ** : Path does not exist !')
        return
    save_to_sub_folder = 'dumps'
    if os.path.exists(os.path.join(base_path, save_to_sub_folder)):
        print('** ERROR ** : Sub folder (dumps) already exists. Please delete it first !')
        return
    os.mkdir(os.path.join(base_path, save_to_sub_folder))
    all_files = [name for name in os.listdir(base_path) if os.path.isfile(os.path.join(base_path, name))]
    ncm_files = [name for name in all_files if name.endswith('.ncm')]
    for f in ncm_files:
        print('Processing %s ...' % f)
        dump(f, os.path.join(base_path, f), save_to_sub_folder)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        for file_path in sys.argv[1:]:
            try:
                print('Decoding ...')
                process(file_path)
                print('done.')
            except Exception as ex:
                traceback.print_exc()
                
    else:
        print("Usage: python batch_decode.py your_path")