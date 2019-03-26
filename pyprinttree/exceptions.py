class PyPrintTreeException(Exception):
    pass


class DuplicateNode(PyPrintTreeException):
    pass


class DuplicateEdge(PyPrintTreeException):
    pass


class NodeNotFound(PyPrintTreeException):
    pass


class EdgeDoesNotLinkNode(PyPrintTreeException):
    pass


class EdgeFormsLoop(PyPrintTreeException):
    pass
