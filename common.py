from collections import OrderedDict
from typing import Any, Mapping
import struct
import xmltodict

def xmlToDict(file: str, process_namespaces: bool = False, namespaces: Any = {}):
    with open(file) as inf:
        xml = inf.read()

    return xmltodict.parse(xml, process_namespaces=process_namespaces, namespaces=namespaces)


def dictToXml(dict_: Mapping[str, Any], pretty: bool = True):
    return xmltodict.unparse(dict_, pretty=pretty)


def readString(data: bytes, offset: int = 0, charWidth: int = 1, encoding: str = 'utf-8'):
    end = data.find(b'\0' * charWidth, offset)
    while end != -1:
        if (end - offset) % charWidth == 0:
            break
        end = data.find(b'\0' * charWidth, end + 1)

    if end == -1:
        return data[offset:].decode(encoding)

    return data[offset:end].decode(encoding)


def roundUp(x: int, y: int):
    return ((x - 1) | (y - 1)) + 1


class BlockHeader:
    def __init__(self, file: bytes, pos: int):
        self.magic, self.size = struct.unpack_from('>4sI', file, pos)

    def save(self):
        return struct.pack(
            '>4sI',
            self.magic,
            self.size,
        )


class Section:
    def __init__(self, file: bytes, pos: int):
        self.blockHeader = BlockHeader(file, pos)
        self.data = file[pos + 8:pos + self.blockHeader.size]

    def save(self):
        self.blockHeader.size = 8 + len(self.data)
        return b''.join([self.blockHeader.save(), self.data])


class Head:
    user = "someone"
    host = "somewhere"
    date = "2019-01-19T22:30:54.551+00:00"
    source = ""
    title = None
    comment = None
    generatorName = "Layout Exporter U"
    generatorVersion = "1.0.2"

    def getAsDict(self):
        _dict: OrderedDict[str, Any] = OrderedDict()
        _dict["create"] = OrderedDict()
        _dict["create"]["@user"] = self.user
        _dict["create"]["@host"] = self.host
        _dict["create"]["@date"] = self.date
        _dict["create"]["@source"] = self.source
        _dict["title"] = self.title
        _dict["comment"] = self.comment
        _dict["generator"] = OrderedDict()
        _dict["generator"]["@name"] = self.generatorName
        _dict["generator"]["@version"] = self.generatorVersion

        return _dict


class Color4:
    def __init__(self):
        self.r: int = 255
        self.g: int = 255
        self.b: int = 255
        self.a: int = 255

    def set(self, r: int, g: int, b: int, a: int):
        self.r, self.g, self.b, self.a = r, g, b, a

    def getAsDict(self):
        return {
            "@r": str(self.r),
            "@g": str(self.g),
            "@b": str(self.b),
            "@a": str(self.a),
        }


class MaterialName:
    def __init__(self):
        self.string = ""

    def set(self, string: str):
        if len(string) > 20:
            print("Warning, material name '%s' must be less than 20 characters!" % string)

        self.string = string

    def get(self):
        return self.string


class UserData:
    class Item:
        def __init__(self):
            self.name: str = ""
            self.type: Any = ""
            self.data: str = ""

        def set(self, userData: 'UserData.Item'):
            self.name = userData.name

            type = userData.type
            data = userData.data

            if type == 0:
                self.data = ' '.join(data)
                self.type = "string"

            elif type == 1:
                self.data = ' '.join([str(_int) for _int in data])
                self.type = "int"

            elif type == 2:
                self.data = ' '.join([str(_float) for _float in data])
                self.type = "float"

        def getAsDict(self):
            if self.type:
                return {
                    "@name": self.name,
                    "#text": self.data,
                }

            return None

    def __init__(self):
        self.string: list[dict[str, str]] = []
        self.int: list[dict[str, str]] = []
        self.float: list[dict[str, str]] = []

    def set(self, extUserData: dict[Any, Any]):
        self.string = []
        self.int = []
        self.float = []

        self.append(extUserData)

    def append(self, extUserData: dict[Any, Any]):
        for userData in extUserData:
            item = self.Item()
            item.set(userData)

            if item.type == "string":
                self.string.append(item.getAsDict())  # type: ignore

            elif item.type == "int":
                self.int.append(item.getAsDict())  # type: ignore

            elif item.type == "float":
                self.float.append(item.getAsDict())  # type: ignore

    def setSingleStr(self, string: str):
        self.string = [{
            "@name": "__BasicUserDataString",
            "#text": string,
        }]

        self.int = []
        self.float = []

    def getAsDict(self):
        _dict: dict[str, list[dict[str, str]]] = {}

        if self.string:
            _dict["string"] = self.string

        if self.int:
            _dict["int"] = self.int

        if self.float:
            _dict["float"] = self.float

        return _dict


class LRName:
    def __init__(self):
        self.string = ""

    def set(self, string: str):
        if len(string) > 24:
            print("Warning, string '%s' must be less than 24 characters!" % string)

        self.string = string

    def get(self):
        return self.string
