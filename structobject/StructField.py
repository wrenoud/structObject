import struct

from .StructBase import *

class StructFieldBase(StructBase):
    """
    Acts as a descriptor class for a class attribute in a BinaryObjectBase
    """
    format = None  # a struct Format String, see https://docs.python.org/3.5/library/struct.html#format-strings
    _python_type = None

    def AddSetter(self, func):
        if self._setters is None:
            self._setters = []
        self._setters.append(func)

    def AddGetter(self, func):
        if self._getters is None:
            self._getters = []
        self._getters.append(func)

    def AddValidator(self, func):
        if self._validators is None:
            self._validators = []
        self._validators.append(func)

    def __init__(self, default=None, getter=None, setter=None, value=None):
        super(StructFieldBase, self).__init__()
        self._structs = [struct.Struct(self.format)]
        self._default = None
        self._setters = None
        self._getters = None
        self._validators = None

        if default is not None: self._default = default
        if getter is not None: self.AddGetter(getter)
        if setter is not None: self.AddSetter(setter)
        if value is not None:
            self._default = value

            def match_value(x):
                return x == value

            self.AddValidator(match_value)

    def flat(self):
        return True

    def __get__(self, parent, parent_type=None):
        if parent is None:
            return self
        elif id(self) in parent._values:
            return parent._values[id(self)]

    def __set__(self, parent, value):
        if value is None:
            parent._values[id(self)] = self._default
        else:
            if self._validators is not None:
                self.validate(value)
            parent._values[id(self)] = value

    def validate(self, value):
        if self._validators is not None:
            for validator in self._validators:
                if not validator(value):
                    raise Exception("Failed validator: {} with value {}".format(validator.__name__, value))

    def prep(self, parent):
        """Runs Setters on value to prepare for serialization

        Args:
            parent: the parent object so the descriptor can look up the value
        """
        _tmp = self.__get__(parent)
        if self._setters is not None:
            for setter in self._setters:
                _tmp = setter(_tmp)
        return _tmp

    def unprep(self, parent):
        """Runs Getters on deserialized value

        Args:
            parent: the parent object so the descriptor can look up and set value
        """
        if self._getters is not None:
            _tmp = self.__get__(parent)
            for getter in self._getters:
                _tmp = getter(_tmp)
            self.__set__(parent, _tmp)

    @property
    def size(self):
        return self._structs[0].size


class pad(StructFieldBase):
    """padding byte"""
    format = b'x'
    _python_type = str


class char(StructFieldBase):
    """string of length 1"""
    format = b'c'
    _python_type = str


class schar(StructFieldBase):
    """signed char"""
    format = b'b'
    _python_type = int


class uchar(StructFieldBase):
    """unsigned char"""
    format = b'B'
    _python_type = int


class bool(StructFieldBase):
    """boolean value"""
    format = b'?'
    _python_type = bool


class short(StructFieldBase):
    """short"""
    format = b'h'
    _python_type = int


class ushort(StructFieldBase):
    """unsigned short"""
    format = b'H'
    _python_type = int


class int(StructFieldBase):
    """signed integer"""
    format = b'i'
    _python_type = int


class uint(StructFieldBase):
    """unsigned integer"""
    format = b'I'
    _python_type = int


class long(StructFieldBase):
    """signed long"""
    format = b'l'
    _python_type = int


class ulong(StructFieldBase):
    """unsigned long"""
    format = b'L'
    _python_type = int


class double(StructFieldBase):
    """double"""
    format = b'd'
    _python_type = float


class float(StructFieldBase):
    """float"""
    format = b'f'
    _python_type = float

class none(StructBase):
    pass