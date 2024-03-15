import unittest
import src.zones.FileUtils.Archive.PFS as PFS


class TestS3DFileReading(unittest.TestCase):

    def test_read_s3d_file(self):
        src = r"E:\FriepawEQWorldBuilder\zones\soldungc\soldungc.s3d"
        cache = r"E:\FriepawEQWorldBuilder\cache"
        error_out = None  # Replace with an error output mechanism if needed

        success = PFS.entry(src, cache, error_out)
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()