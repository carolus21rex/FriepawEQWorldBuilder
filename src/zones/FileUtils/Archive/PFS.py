import os
import binascii
import zlib
from src.zones.FileUtils.Archive.crc32Table import FilenameCRC
import src.zones.HexUtil as hu
import src.GUI.WindowsUtil as wu


# Constant Table
PFS_MAGIC_NUMBER = "50465320"   # "PFS " in hex
FOOTER_TOKEN = "STEVE"          # WHO'S STEVE?!?
PFS_HEADER_LENGTH = 12
ZLIB_HEADER_LENGTH = 8


def entry(src, cache, error_out):

    """
    Important Notes:
        All eq compressed files: .EQG, .PAK, .PFS(obviously), and .PFS are PFS.
        Individual portions of PFS are compressed by z-lib, but not the entire file.
        This function is the intended entry point for this Python file.
        This function creates a cache folder if given a nonexistent folder.
    Expected Contents by file type:
        EQG -
        PAK -
        PFS -
        PFS -

    Usage:
        Given a PFS file "src" it will extract the contents to directory "cache"
        Expected output is dependent on file type. Each file type can be found
        in the table above.

    Args:
        src: Absolute path of the source PFS file.
        cache: Absolute path of where to store the contents of the PFS.
        error_out: Text box containing errors in the GUI.

    Returns:
        Success: False if process failed, True if process succeeded.
    """

    try:
        if not os.path.exists(cache):
            os.makedirs(cache)

        with open(src, 'rb') as file:
            pfs_data = file.read()

        # extracts contents of pfs_data. if there is an error, write to box and return None
        pfs_header = readHeader(pfs_data, error_out)
        if pfs_header is None:
            return False

        dir_offset = hu.LEHexStringToInt(pfs_header[0])

        # file count, reads 8 bytes after the dir offset as an integer.
        file_count = get_int_at(pfs_data, dir_offset)

        files = extract_files(pfs_data, file_count, dir_offset, error_out)

        for i, file_data in enumerate(files):
            file_path = os.path.join(cache, f"file_{i}.zlib")
            with open(file_path, 'wb') as f:
                f.write(file_data)


        return True
    except FileNotFoundError:
        wu.write_to_textbox(error_out, "Error 1103: Source file Not Found")
    except ValueError:
        wu.write_to_textbox(error_out, "Error 1104: Casting Failed")
    return False


def get_int_at(pfs_data, offset):

    """
    Usage:
        gets the integer interpretation of a PFS file in memory "pfs_data" by reading
        a 32-bit Little Endian integer at the location "offset"
    Args:
        pfs_data: PFS file in memory to be read.
        offset: Location where integer to be read can be found.
    Returns:
        int_out: integer value found at location "offset" in "pfs_data"
    """

    return hu.LEHexStringToInt(binascii.hexlify(
        pfs_data[offset: offset + 4]).decode('utf-8'))


def readHeader(pfs_data, error_out):

    """
    Usage:
        Given a PFS file in memory "pfs_data" it will read the header and return
        the header as a variable in memory "header".

    Args:
        pfs_data: PFS file stored in memory.
        error_out: Text box containing errors in the GUI.

    Returns:
        header_hex: Success, contains the first 3 words of "pfs_data".
        None: Failure, probably from a malformed header.
    """

    if len(pfs_data) < 12:
        # wu.write_to_textbox(error_out, "Error 1100: Invalid PFS File.")
        print("Error 1100: Invalid PFS File.")
        return None

    header_bytes = pfs_data[:4*3]
    header_hex = [binascii.hexlify(header_bytes[i:i+4]).decode('utf-8') for i in
                  range(0, len(header_bytes), 4)]

    # debug: print(pfs_data.count(b'\x53\x54\x45\x56\x45'))

    if header_hex[1] != PFS_MAGIC_NUMBER:
        # wu.write_to_textbox(error_out, "Error 1101: Incorrect Magic Number.")
        print("Error 1101: Incorrect Magic Number.")
        return None

    # debug: print(header_hex)
    return header_hex


def extract_files(pfs_data, file_count, dir_offset, error_out):
    # Helldiver, we can't stay this low much longer!

    """
    Usage:
        Given a PFS file in memory "pfs_data" and the number of files
        to be extracted "file_count" it will read "file_count" number of files
        from "pfs_data" and return an array of those files in memory.

    Args:
        pfs_data: PFS file stored in memory.
        error_out: Text box containing errors in the GUI.
        file_count: Number of files expected to be in "pfs_data".
        dir_offset: The file pointer should never be greater than "dir_offset".

    Returns:
        files:  Success, an array in memory containing each individual zlib file.
        None:   Failure, file pointer started pulling data from beyond its scope,
                probably a malformed file, or corrupted header.
    """

    files = []
    pointer = PFS_HEADER_LENGTH
    for _ in range(file_count):
        if pointer > dir_offset:
            print("Error 1105: File pointer exceeds directory offset")
            # wu.write_to_textbox(error_out, "Error 1105: File pointer exceeds directory offset")
            return None
        file_size = get_int_at(pfs_data, pointer) + ZLIB_HEADER_LENGTH
        file_data = pfs_data[pointer:pointer + file_size]
        files.append(file_data)
        pointer += file_size

    return files
