from collections import OrderedDict
import os

from common import dictToXml, Head
from flyt import Layout
from flan import main as flanMain


def main(file, output):
    print("Layout Exporter U v1.0.0")
    print("(C) 2019 AboodXD\n")

    print("Please note that animation keys' slope type is set to Step.")
    print("Meaning that the animation playback in NW LayoutEditor will")
    print("be a bit sloppy.")
    print("This is due to the tool not being able to determine which")
    print("slope type to use. Additionally, Step ensures that none of the")
    print("keys will be removed when exporting as binary from LayoutEditor.")
    print("Don't worry, this will not affect animation playback ingame.")
    print("Enjoy. ;)")

    animPath = os.path.join(os.path.dirname(os.path.dirname(file)), 'anim')
    fileName = os.path.splitext(os.path.basename(file))[0]
    animOutput = os.path.splitext(output)[0] + ".flan"
    if os.path.isfile(os.path.join(animPath, fileName + ".bflan")):
        files = [fileName + ".bflan"]

    else:
        files = []
        for _file in os.listdir(animPath):
            if _file.startswith(fileName + "_"):
                files.append(_file)

    textures, formats = None, None
    if files:
        textures, formats = flanMain(files, animPath, animOutput)

    lyt = Layout(file, textures, formats)

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

if name == "__main__":
    file = input("Input (.bflyt):  ")
    output = input("Output (.flyt):  ")
    main(file, output)
