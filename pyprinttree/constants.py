class _Constant:
    def __eq__(self, other):
        return id(self) == id(other)


DoesNotExist = _Constant()
Unset = _Constant()
