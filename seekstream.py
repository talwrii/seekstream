import StringIO

def switch_proxy(f):
    def patched(self, *args, **kwargs):
        while True:
            try:
                return f(self, *args, **kwargs)
            except FinishedReading as e:
                self.proxy = self.buffer
                return ''
            except FinishedBuffer as e:
                self.proxy = self.buffer_read_proxy
                rest = switch_proxy(f)(self, *e.args, **e.kwargs)
                if e.partial_result:
                    return e.partial_result + rest
                else:
                    return rest
            except CannotSeek:
                self.proxy = self.buffer_reread_proxy
                return switch_proxy(f)(self, *args, **kwargs)
            except NeedRandomAccess:
                self.complete_read()
                return switch_proxy(f)(self, *args, **kwargs)
    return patched

class SeekableStream(object):
    "Buffer a stream that does not support seeking so that we can seek"

    # Use trendy: "encapsulation instead of stateful behaviour via containment"
    #    to simplify state within classes

    # Invariants: We *never* read ahead (since this could in theory take a long time)

    def __init__(self, stream):
        self.buffer = StringIO.StringIO()
        self.buffer_read_proxy = BufferReadAdaptor(self.buffer, stream)
        self.buffer_reread_proxy = BufferReReadAdaptor(self.buffer)
        self.proxy = self.buffer_read_proxy

    @switch_proxy
    def read(self, num=None):
        return self.proxy.read(num)

    @switch_proxy
    def readline(self):
        return self.proxy.readline()

    @switch_proxy
    def seek(self, pos, whence=0):
        return self.proxy.seek(pos, whence)

    @switch_proxy
    def tell(self):
        return self.proxy.tell()

    @switch_proxy
    def complete_read(self):
        self.buffer_read_proxy.read(None)

class BufferReadAdaptor(object):
    """Read writing state into buffer, raise errors on attempt to seek"""
    def __init__(self, buf, stream):
        self.buffer = buf
        self.stream = stream

    def read(self, num):
        if num is None:
            result = self._buffered_operation(self.stream.read)
        else:
            result = self._buffered_operation(self.stream.read, num)
        if result == '':
            raise FinishedReading()
        else:
            return result

    def readline(self):
        result = self._buffered_operation(self.stream.readline)
        if result == '':
            raise FinishedReading()
        else:
            return result

    def _write_into_buffer(self, text):
        self.buffer.write(text)
        return text

    def _buffered_operation(self, func, *args, **kwargs):
        result = func(*args, **kwargs)
        self._write_into_buffer(result)
        return result

    def seek(self, pos, whence):
        if whence == 2:
            raise NeedRandomAccess()
        elif whence == 1:
            raise CannotSeek()

        num_to_read = pos - self.buffer.tell()
        if num_to_read < 0:
            raise CannotSeek()
        elif num_to_read == 0:
            pass
        else:
            self.read(num_to_read)

    def tell(self):
        return self.buffer.len

class BufferReReadAdaptor(object):
    def __init__(self, buf):
        self.buffer = buf

    def read(self, num):
        result = self.buffer.read(num)
        if len(result) == num:
            return result
        else:
            remaining = None if num is None else num - len(result)
            raise FinishedBuffer(result, remaining)

    def readline(self):
        result = self.buffer.readline()
        if not result.endswith('\n'):
            raise FinishedBuffer(result)
        else:
            return result

    def seek(self, pos, whence):
        if whence == 2:
            raise NeedRandomAccess()
        elif whence == 1:
            self.seek(self.buffer.tell() + pos, 0)

        if pos > self.buffer.len:
            raise FinishedBuffer(None, pos, whence)
        else:
            self.buffer.seek(pos, whence)

    def tell(self):
        return self.buffer.tell()

class BehaviourChange(Exception):
    "Change how the seekable stream behaves"

class FinishedReading(BehaviourChange):
    "Finished populating buffer. We can now random access things"

class FinishedBuffer(BehaviourChange):
    def __init__(self, partial_result, *args, **kwargs):
        BehaviourChange.__init__(self)
        self.partial_result = partial_result
        self.args = args
        self.kwargs = kwargs

class NeedRandomAccess(BehaviourChange):
    pass

class CannotSeek(BehaviourChange):
    pass
