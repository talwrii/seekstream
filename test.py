import unittest
import StringIO
from seekstream import SeekableStream

class Test(unittest.TestCase):
    def setUp(self):
        self.text = "01234567890\ntwo\nthree"
        f = StringIO.StringIO(self.text)
        f.secret_seek = f.seek
        f.secret_tell = f.tell
        f.seek = lambda: None
        f.tell = lambda: None
        self.sample_stream = f

    def test_read_all(self):
        stream = SeekableStream(self.sample_stream)
        text = stream.read()
        self.assertEquals(text[:3], "012")
        self.assertEquals(text[-3:], "ree")
        self.assertEquals(stream.read(), '')

    def test_random_access_reread(self):
        # Reread mode
        stream = SeekableStream(self.sample_stream)
        stream.readline()
        stream.seek(0)

        # Seek to the end
        stream.seek(0, 2)

    def test_random_access_first_read(self):
        stream = SeekableStream(self.sample_stream)
        stream.seek(0, 2)
        self.assertEquals(stream.tell(), len(self.text))

    def test_readline_first_access(self):
        stream = SeekableStream(self.sample_stream)
        lines = []
        while True:
            line = stream.readline().strip()
            if line == '':
                break
            else:
                lines.append(line)

        self.assertEquals(lines, self.text.splitlines())

    def test_basic(self):
        f = self.sample_stream
        stream = SeekableStream(self.sample_stream)

        # Seeking and telling
        stream.seek(1)
        self.assertEquals(stream.tell(), 1)

        self.assertEquals(f.secret_tell(), 1)
        self.assertEquals(stream.read(1), "1")
        self.assertEquals(stream.tell(), 2)
        self.assertEquals(f.secret_tell(), 2)
        self.assertEquals(stream.read(1), "2")

        stream.seek(1)
        self.assertEquals(stream.tell(), 1)
        self.assertEquals(f.secret_tell(), 3)

        stream.readline()

        self.assertEquals(stream.readline(), 'two\n')

        stream.seek(0)
        stream.readline()
        self.assertEquals(stream.readline(), 'two\n')
        self.assertEquals(stream.read(), 'three')
        self.assertEquals(stream.read(), '')


        stream.seek(0, 2)

        stream.seek(0)
        stream.read()

if __name__ == '__main__':
	unittest.main()
