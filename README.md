# decode_ncm

Decode `*.ncm` file (NetEase Cloud Music format)

Install requirements:
```
pip install pycrypto
```

Usage:

1) Decode single file.

```
python decode.py file_name
```


2) Decode all `*.ncm` files in a folder.
```
python batch_decode.py input_path
```

This will create a sub folder named "dumps" under input path.


3) Decode all `*.ncm` files in a folder and its sub folders.

```
python batch_decode_with_subfolder.py input_path output_path
```

This will decode all `.ncm` files under input_path and its 1st level subfolder, and output will be under output_path with the same sub folder hierarchy. And it will also copy `.flac` and `.mp3` files under input_path to output folder.

