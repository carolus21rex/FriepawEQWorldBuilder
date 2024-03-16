import os
import binascii
import src.zones.HexUtil as hu
import src.GUI.WindowsUtil as wu


# Constant Table
PFS_MAGIC_NUMBER = "50465320"       # "PFS " in hex
FOOTER_TOKEN = "STEVE"              # WHO'S STEVE?!?
PFS_HEADER_LENGTH = 12              # in bytes
ZLIB_HEADER_LENGTH = 8              # in bytes
EXPECTED_VERSION = ["00020000"]     # May be expanded upon in the future
UINT32_SIZE = 8


def entry(src, cache, error_out):

    """
    Important Notes:
        All eq compressed files: .EQG, .PAK, .PFS(obviously), and .S3d are PFS.
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
        file_count = getIntAt(pfs_data, dir_offset)
        crc, offset, file_size = readMetaData(pfs_data, dir_offset, file_count)

        files = extractFiles(pfs_data, file_count, file_size, dir_offset, error_out)

        file_names = extractNames(pfs_data, file_count, crc, error_out)

        for i, file_data in enumerate(files):
            file_path = os.path.join(cache, f"{file_names[i]}.zlib")
            with open(file_path, 'wb') as f:
                f.write(file_data)

        return True
    except FileNotFoundError:
        wu.write_to_textbox(error_out, "Error 1103: Source file Not Found")
    except ValueError:
        wu.write_to_textbox(error_out, "Error 1104: Casting Failed")
    return False


def getIntAt(pfs_data, offset):

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

    if header_hex[2] not in EXPECTED_VERSION:
        # wu.write_to_textbox(error_out, "Error 1106: Unexpected version.")
        print("Error 1106: Unexpected version.")
        return None

    # debug: print(header_hex)
    return header_hex


def readMetaData(pfs_data, dir_offset, file_count):

    """
    Usage:
        Given a PFS_File in memory "pfs_data", the location to start looking at "dir_offset",
        and the number of files "file_count" this function will return all the required metadata
        in the form of 3 arrays, the crc numbers for file name recovery "crc", the offset where a
        file begins "offset" (redundancy, but doesn't hurt), and the size of the file "file_size"
        which is used to determine how many zlib segments the function "extractFiles" needs to
        pull out of pfs_data to have a completed file.
    Args:
        pfs_data:   PFS file stored in memory.
        dir_offset: The location that delimits raw data from meta_data, will need to be incremented
                    since the location dir_offset is pointed at is "file_count" which is already
                    accounted for.
        file_count: The number of files, or for this function's purposes the count of metadata segments
                    that need to be pulled out of "pfs_data".
    Return:
        crc:        Used to obtain the name of the respective file.
        offset:     Where the respective file is stored in "pfs_data".
        file_size:  The size of the respective file stored at that index.
    """

    crc, offset, file_size = [] * file_count
    pointer = dir_offset + UINT32_SIZE
    for i in range(file_count):
        crc[i] = getIntAt(pfs_data, pointer)
        offset[i] = getIntAt(pfs_data, pointer + UINT32_SIZE)
        file_size[i] = getIntAt(pfs_data, pointer + 2 * UINT32_SIZE)
        pointer += 3 * UINT32_SIZE

    return crc, offset, file_size


def extractFiles(pfs_data, file_count, file_size, dir_offset, error_out):
    # FOR DEMOCRACY!!!

    """
    Usage:
        Given a PFS file in memory "pfs_data" and the number of files
        to be extracted "file_count" it will read "file_count" number of files
        from "pfs_data" and return an array of those files in memory.

    Args:
        pfs_data: PFS file stored in memory.
        file_count: Number of files expected to be in "pfs_data".
        file_size: An array of sizes for each index in "file_count".
        dir_offset: The file pointer should never be greater than "dir_offset".
        error_out: Text box containing errors in the GUI.

    Returns:
        files:  Success, an array in memory containing each individual zlib file.
        None:   Failure, file pointer started pulling data from beyond its scope,
                probably a malformed file, or corrupted header.
    """

    files = [""] * file_count
    pointer = PFS_HEADER_LENGTH
    for i in range(file_count):
        extraction = 0
        base = pointer
        while extraction < file_size[i]:
            if pointer > dir_offset:
                print("Error 1105: File pointer exceeds directory offset")
                # wu.write_to_textbox(error_out, "Error 1105: File pointer exceeds directory offset")
                return None
            size = getIntAt(pfs_data, pointer) + ZLIB_HEADER_LENGTH
            file_data = pfs_data[pointer + ZLIB_HEADER_LENGTH:pointer + ZLIB_HEADER_LENGTH + size]
            files[i] += file_data
            pointer += size
            extraction += size

    return files


def extractNames(pfs_data, file_count, crc, error_out):

    """
    Usage:
        Given a PFS file in memory "pfs_data" and the number of files
        to be extracted "file_count" it will read "file_count" number of names
        from "pfs_data" and return an array of those names in memory.

    Args:
        pfs_data:
        file_count:
        crc:
        error_out: Text box containing errors in the GUI.

    Returns:
        files:  Success, an array in memory containing the names of each zlib file.
        None:   Failure, names are probably corrupted.
    """

    pass
