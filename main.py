from collections import OrderedDict
import os

from common import dictToXml, Head
from flyt import Layout
from flan import main as flanMain


def main():
    print("Layout Exporter U v1.0.0")
    print("(C) 2019 AboodXD\n")

    file = input("Input (.bflyt):  ")
    output = input("Output (.flyt):  ")

    animPath = os.path.join(os.path.dirname(os.path.dirname(file)), 'anim')
    timgPath = os.path.join(os.path.dirname(os.path.dirname(file)), 'timg')
    timgOutP = os.path.join(os.path.dirname(output), 'Textures')

    fileName = os.path.splitext(os.path.basename(file))[0]
    animOutput = os.path.splitext(output)[0] + ".flan"

    files = []
    if os.path.isfile(os.path.join(animPath, fileName + ".bflan")):
        files.append(fileName + ".bflan")

    elif os.path.isdir(animPath):
        for _file in os.listdir(animPath):
            if _file.startswith(fileName + "_"):
                files.append(_file)

    textures, formats = None, None
    if files:
        textures, formats = flanMain(files, animPath, animOutput)

    lyt = Layout(file, timgPath, timgOutP, textures, formats)

    file = {}
    file["nw4f_layout"] = OrderedDict()
    file["nw4f_layout"]["@version"] = "1.5.14"
    file["nw4f_layout"]["@xmlns:xsd"] = "http://www.w3.org/2001/XMLSchema"
    file["nw4f_layout"]["@xmlns:xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
    file["nw4f_layout"]["@xmlns"] = "http://www.nintendo.co.jp/NW4F/LayoutEditor"
    file["nw4f_layout"]["head"] = Head().getAsDict()
    file["nw4f_layout"]["body"] = {}
    file["nw4f_layout"]["body"]["lyt"] = lyt.getAsDict()

    xml = dictToXml(file)
    with open(output, "w", encoding="utf-8") as out:
        out.write(xml)


if __name__ == "__main__":
    main()
