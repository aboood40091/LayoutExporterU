from collections import OrderedDict
import os
import sys

from common import dictToXml, Head
from flyt import Layout
from flan import main as flanMain

def main():
    print("Layout Exporter U v1.0.2")
    print("(C) 2019 AboodXD\n")
    if len(sys.argv) == 2: return print("Usage: py main.py <input.bflyt> <output.flyt>")

    if len(sys.argv) < 2:
        file = input("Input file (.bflyt): ")
        output = input("Output file: (.flyt): ")
    else:
        file = sys.argv[1]
        output = sys.argv[2]

    print(f"Exporting {file} -> {output}")

    animPath = os.path.join(os.path.dirname(os.path.dirname(file)), 'anim')
    timgPath = os.path.join(os.path.dirname(os.path.dirname(file)), 'timg')
    timgOutP = os.path.join(os.path.dirname(output), 'Textures')

    fileName = os.path.splitext(os.path.basename(file))[0]
    animOutput = os.path.splitext(output)[0] + ".flan"

    files: list[str] = []
    if os.path.isfile(os.path.join(animPath, fileName + ".bflan")):
        files.append(fileName + ".bflan")

    elif os.path.isdir(animPath):
        for _file in os.listdir(animPath):
            if _file.startswith(fileName + "_"):
                files.append(_file)

    textures: list[str] = []
    formats: list[str] = []
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
