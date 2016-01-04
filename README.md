# seekstream

A python library to let you seek in file-like objects that
do not support seeking. This is a achieved by by caching already
read data in memory.

The library tries as hard as possible to not seek ahead.

## Installation

    pip install git+https://github.com/talwrii/seekstream.git#seekstream

## Usage

    import seekstream
    with open('/dev/urandom') as stream:
        seekable = seekstream.SeekableStream(stream)
        old = seekable.read(10)
        seekable.seek(0)
        seekable.read(10) == old

    # urandom is not seekable

## Development
    git clone https://github.com/talwrii/seekstream.git
    cd seekstream
    ./runtests.sh # tests coverage
