import os
import binascii
import zlib
import src.GUI.WindowsUtil as wu


# Constant Table
PFS_MAGIC_NUMBER = "50465320"   # "PFS " in hex
FOOTER_TOKEN = "STEVE"          # WHO'S STEVE?!?


def entry(src, cache, error_out):

    """
    Important Notes:
        All eq compressed files: .EQG, .PAK, .PFS(obviously), and .S3D are PFS.
        Individual portions of PFS are compressed by z-lib, but not the entire file.
        This function is the intended entry point for this Python file.
        This function creates a cache folder if given a nonexistent folder.
    Expected Contents by file type:
        EQG -
        PAK -
        PFS -
        S3D -

    Usage:
        Given a PFS file "src" it will extract the contents to directory "cache"
        Expected output is dependent on file type. Each file type can be found
        in the table above.

    Args:
        src: Absolute path of the source PFS file
        cache: Absolute path of where to store the contents of the PFS
        error_out: Text box containing errors in the GUI

    Returns:
        Success: False if process failed, True if process succeeded.
    """

    if not os.path.exists(cache):
        os.makedirs(cache)

    with open(src, 'rb') as file:
        pfs_data = file.read()

    # extracts contents of s3d_data. if there is an error, write to box and return None
    pfs_header = readHeader(pfs_data, error_out)
    if pfs_header is None:
        return False

    return True


def readHeader(pfs_data, error_out):

    """
    Usage:
        Given a PFS file "pfs_data" it will read the header and return
        the header as a variable in memory "header"

    Args:
        pfs_data: PFS file stored in memory
        error_out: Text box containing errors in the GUI

    Returns:
        Success: False if process failed, True if process succeeded.
    """

    if len(pfs_data) < 12:
        # wu.write_to_textbox(error_out, "Error 1100: Invalid PFS File.")
        print("Error 1100: Invalid PFS File.")
        return None

    # there are 3 elements of the header
    header_bytes = pfs_data[:4*3]
    header_hex = [binascii.hexlify(header_bytes[i:i+4]).decode('utf-8') for i in
                  range(0, len(header_bytes), 4)]

    print(pfs_data.count(b'\x53\x54\x45\x56\x45'))

    if header_hex[1] != PFS_MAGIC_NUMBER:
        # wu.write_to_textbox(error_out, "Error 1101: Incorrect Magic Number.")
        print("Error 1101: Incorrect Magic Number.")
        return None
    print(header_hex)
    return header_hex


def readEntryCount(formatted_string):

    """
    Usage:
        Given the 3rd element of a PFS header, it will return an integer

    Args:
        formatted_string: PFS file stored in memory

    Returns:
        Success: False if process failed, True if process succeeded.
    """

    pass
