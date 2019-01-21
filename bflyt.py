import struct
from bflan import FLAN
from common import readString, roundUp, Section


printTexList = False
printFntList = False
printMatInfo = False
printPanInfo = False


def _printTex(*args, **kwargs):
    if printTexList:
        print(*args, **kwargs)


def _printFnt(*args, **kwargs):
    if printFntList:
        print(*args, **kwargs)


def _printMat(*args, **kwargs):
    if printMatInfo:
        print(*args, **kwargs)


def _printPan(*args, **kwargs):
    if printPanInfo:
        print(*args, **kwargs)


def readPane(file, pos):
    if file[pos:pos + 4] == b'pan1':
        return FLYT.Pane(file, pos)

    elif file[pos:pos + 4] == b'pic1':
        return FLYT.Picture(file, pos)

    elif file[pos:pos + 4] == b'txt1':
        return FLYT.TextBox(file, pos)

    elif file[pos:pos + 4] == b'wnd1':
        return FLYT.Window(file, pos)

    elif file[pos:pos + 4] == b'bnd1':
        return FLYT.Bounding(file, pos)

    elif file[pos:pos + 4] == b'prt1':
        return FLYT.Parts(file, pos)

    else:
        raise NotImplementedError("Unknown pane type!")


class FLYT:
    class Layout(Section):
        def __init__(self, file, pos):
            super().__init__(file, pos)

            (self.originType,
             self.layoutWidth,
             self.layoutHeight,
             self.partsWidth,
             self.partsHeight) = struct.unpack_from('>B3x4f', self.data)

            self.name = readString(self.data, 0x14)

    class Control(Section):
        def __init__(self, file, pos, major):
            super().__init__(file, pos)

            self.extUserDataList = None

            if major < 5:
                (self.controlFunctionalPaneNamesOffset,
                 self.controlFunctionalPaneNum,
                 self.controlFunctionalAnimNum) = struct.unpack_from('>I2H', self.data); pos = 8

                self.controlUserNameOffset = 0
                self.controlFunctionalPaneParameterNameOffsetsOffset = 0
                self.controlFunctionalAnimParameterNameOffsetsOffset = 0

            else:
                (self.controlUserNameOffset,
                 self.controlFunctionalPaneNamesOffset,
                 self.controlFunctionalPaneNum,
                 self.controlFunctionalAnimNum,
                 self.controlFunctionalPaneParameterNameOffsetsOffset,
                 self.controlFunctionalAnimParameterNameOffsetsOffset) = struct.unpack_from('>2I2H2I', self.data); pos = 20

            self.controlName = readString(self.data, pos)

            self.controlUserName = ''
            if self.controlUserNameOffset:
                pos = self.controlUserNameOffset - 8
                self.controlUserName = readString(self.data, pos)

            if not self.controlUserName:
                self.controlUserName = self.controlName

            self.controlFunctionalPaneNames = []
            if self.controlFunctionalPaneNamesOffset:
                pos = self.controlFunctionalPaneNamesOffset - 8
                for i in range(self.controlFunctionalPaneNum):
                    name = readString(struct.unpack_from('>24s', self.data, pos)[0]); pos += 24
                    self.controlFunctionalPaneNames.append(name)

            else:
                pos -= 8

            self.controlFunctionalAnimNames = []
            for i in range(self.controlFunctionalAnimNum):
                pName = pos + struct.unpack_from('>I', self.data, pos + 4*i)[0]
                self.controlFunctionalAnimNames.append(readString(self.data, pName))

            self.controlFunctionalPaneParameterNames = []
            if self.controlFunctionalPaneParameterNameOffsetsOffset:
                pos = self.controlFunctionalPaneParameterNameOffsetsOffset - 8
                for i in range(self.controlFunctionalPaneNum):
                    pName = pos + struct.unpack_from('>I', self.data, pos + 4*i)[0]
                    self.controlFunctionalPaneParameterNames.append(readString(self.data, pName))

            self.controlFunctionalAnimParameterNames = []
            if self.controlFunctionalAnimParameterNameOffsetsOffset:
                pos = self.controlFunctionalAnimParameterNameOffsetsOffset - 8
                for i in range(self.controlFunctionalAnimNum):
                    pName = pos + struct.unpack_from('>I', self.data, pos + 4*i)[0]
                    self.controlFunctionalAnimParameterNames.append(readString(self.data, pName))

            if major < 5:
                self.controlFunctionalPaneParameterNames = self.controlFunctionalPaneNames
                self.controlFunctionalAnimParameterNames = self.controlFunctionalAnimNames

        def save(self, major):
            controlFunctionalPaneNum = len(self.controlFunctionalPaneNames)
            controlFunctionalAnimNum = len(self.controlFunctionalAnimNames)
            buff1 = self.controlName.encode('utf-8') + b'\0'

            controlUserNameOffset = len(buff1)
            alignLen = roundUp(controlUserNameOffset, 4) - controlUserNameOffset

            controlUserNameOffset += alignLen
            buff1 += b'\0' * alignLen

            controlFunctionalPaneNamesOffset = len(buff1)
            if self.controlUserName and major >= 5:
                buff1 += self.controlUserName.encode('utf-8') + b'\0'

                controlFunctionalPaneNamesOffset = len(buff1)
                alignLen = roundUp(controlFunctionalPaneNamesOffset, 4) - controlFunctionalPaneNamesOffset

                controlFunctionalPaneNamesOffset += alignLen
                buff1 += b'\0' * alignLen

            buff2 = bytearray()
            for name in self.controlFunctionalPaneNames:
                buff2 += struct.pack('>24s', name.encode('utf-8'))

            buff3 = bytearray()

            controlFunctionalAnimNamesOffsets = []
            for name in self.controlFunctionalAnimNames:
                controlFunctionalAnimNamesOffsets.append(len(buff3))
                buff3 += name.encode('utf-8')
                buff3.append(0)

            buff4 = struct.pack('>%dI' % controlFunctionalAnimNum, *controlFunctionalAnimNamesOffsets)

            if major < 5:
                controlUserNameOffset += 16
                controlFunctionalPaneNamesOffset += 16

                buff5 = struct.pack(
                    '>I2H',
                    controlFunctionalPaneNamesOffset,
                    controlFunctionalPaneNum,
                    controlFunctionalAnimNum,
                )

                self.data = b''.join([buff5, buff1, buff2, buff4, buff3])

                return super().save()

            else:
                controlFunctionalPaneParameterNameOffsetsOffset = len(buff1) + len(buff2) + len(buff4) + len(buff3)
                alignLen = roundUp(controlFunctionalPaneParameterNameOffsetsOffset, 4) - controlFunctionalPaneParameterNameOffsetsOffset

                controlFunctionalPaneParameterNameOffsetsOffset += alignLen
                buff3 += b'\0' * alignLen

                buff6 = bytearray()

                controlFunctionalPaneParameterNameOffsets = []
                for name in self.controlFunctionalPaneParameterNames:
                    controlFunctionalPaneParameterNameOffsets.append(len(buff6))
                    buff6 += name.encode('utf-8')
                    buff6.append(0)

                buff7 = struct.pack('>%dI' % controlFunctionalPaneNum, *controlFunctionalPaneParameterNameOffsets)

                controlFunctionalAnimParameterNameOffsetsOffset = controlFunctionalPaneParameterNameOffsetsOffset + len(buff7) + len(buff6)
                alignLen = roundUp(controlFunctionalAnimParameterNameOffsetsOffset, 4) - controlFunctionalAnimParameterNameOffsetsOffset

                controlFunctionalAnimParameterNameOffsetsOffset += alignLen
                buff6 += b'\0' * alignLen

                buff8 = bytearray()

                controlFunctionalAnimParameterNameOffsets = []
                for name in self.controlFunctionalAnimParameterNames:
                    controlFunctionalAnimParameterNameOffsets.append(len(buff8))
                    buff8 += name.encode('utf-8')
                    buff8.append(0)

                buff9 = struct.pack('>%dI' % controlFunctionalAnimNum, *controlFunctionalAnimParameterNameOffsets)

                controlUserNameOffset += 28
                controlFunctionalPaneNamesOffset += 28
                controlFunctionalPaneParameterNameOffsetsOffset += 28
                controlFunctionalAnimParameterNameOffsetsOffset += 28

                buff5 = struct.pack(
                    '>2I2H2I',
                    controlUserNameOffset,
                    controlFunctionalPaneNamesOffset,
                    controlFunctionalPaneNum,
                    controlFunctionalAnimNum,
                    controlFunctionalPaneParameterNameOffsetsOffset,
                    controlFunctionalAnimParameterNameOffsetsOffset,
                )

                self.data = b''.join([buff5, buff1, buff2, buff4, buff3, buff7, buff6, buff9, buff8])

                return super().save()

    class TextureList(Section):
        def __init__(self, file, pos):
            super().__init__(file, pos)

            self.texNum = struct.unpack_from('>H', self.data)[0]
            self.textures = []
            self.formats = []

            if self.texNum:
                _printTex("Textures:")

            for i in range(self.texNum):
                pTexture = struct.unpack_from('>I', self.data, 4 * (i+1))[0] + 4
                texture = readString(self.data, pTexture)
                format = ""

                assert texture[-6:] == ".bflim"
                texture = texture[:-6]

                if len(texture) > 2:
                    if texture[-1] in 'abcdefghijklmnopqrstu' and texture[-2] == "^":
                        format = texture[-1:]
                        texture = texture[:-2]

                _printTex(texture)
                self.textures.append(texture)
                self.formats.append(format)

            if self.texNum:
                _printTex()

    class FontList(Section):
        def __init__(self, file, pos):
            super().__init__(file, pos)

            self.fontNum = struct.unpack_from('>H', self.data)[0]
            self.fonts = []

            if self.fontNum:
                _printFnt("Fonts:")

            for i in range(self.fontNum):
                pFont = struct.unpack_from('>I', self.data, 4 * (i+1))[0] + 4
                font = readString(self.data, pFont)

                assert font[-6:] == ".bffnt"
                font = font[:-6]

                _printFnt(font)
                self.fonts.append(font)

            if self.fontNum:
                _printFnt()

    class MaterialList(Section):
        class Material:
            class TexMap:
                def __init__(self, file, pos):
                    (self.texIdx,
                     self.wrapSflt,
                     self.wrapTflt) = struct.unpack_from('>H2B', file, pos)

                    _texWrap = ["Clamp", "Repeat", "Mirror"]
                    _texFilter = ["Near", "Linear"]

                    # wrapSflt -> 0000FFWW
                    self.wrapS = self.wrapSflt & 3
                    self.minFilter = (self.wrapSflt >> 2) & 3

                    # wrapTflt -> 0000FFWW
                    self.wrapT = self.wrapTflt & 3
                    self.magFilter = (self.wrapTflt >> 2) & 3

                    _printMat("Texture Index: %d" % self.texIdx)
                    _printMat("Wrap S: %s" % _texWrap[self.wrapS])
                    _printMat("Wrap T: %s" % _texWrap[self.wrapT])
                    _printMat("Min Filter: %s" % _texFilter[self.minFilter])
                    _printMat("Mag Filter: %s" % _texFilter[self.magFilter])

            class TexSRT:
                def __init__(self, file, pos):
                    self.translate = struct.unpack_from('>2f', file, pos); pos += 8
                    self.rotate = struct.unpack_from('>f', file, pos); pos += 4
                    self.scale = struct.unpack_from('>2f', file, pos); pos += 8

                    _printMat("Texture Translation:", self.translate)
                    _printMat("Texture Rotation:", self.rotate)
                    _printMat("Texture Scale:", self.scale)

            class TexCoordGen:
                def __init__(self, file, pos):
                    _texGenTypes = ["Matrix2x4"]
                    _texGenSrcs = [
                        "Tex0", "Tex1", "Tex2", "Orthogonal Projection",
                        "Pane-Based Projection", "Perspective Projection",
                    ]

                    (self.texGenType,
                     self.texGenSrc) = struct.unpack_from('>2B2x', file, pos); pos += 4

                    self.projectionTexGenParameter = None

                    _printMat("Texture Coordinate Generation Type: %s" % _texGenTypes[self.texGenType])
                    _printMat("Texture Coordinate Generation Source: %s" % _texGenSrcs[self.texGenSrc])

            class TevStage:
                def __init__(self, file, pos):
                    _tevModes = [
                        "Replace", "Modulate", "Add", "Add Signed",
                        "Interpolate", "Subtract", "Add Multiplicate", "Multiplicate Add",
                        "Overlay", "Indirect", "Blend Indirect", "Each Indirect",
                    ]

                    (self.combineRgb,
                     self.combineAlpha) = struct.unpack_from('>2B2x', file, pos); pos += 4

                    _printMat("Tev Combine RGB Mode: %s" % _tevModes[self.combineRgb])
                    _printMat("Tev Combine Alpha Mode: %s" % _tevModes[self.combineAlpha])

            class AlphaCompare:
                def __init__(self, file, pos):
                    _funcs = [
                        "Never", "Less", "Less or Equal", "Equal",
                        "Not Equal", "Greater or Equal", "Greater", "Always",
                    ]

                    (self.func,
                     self.ref) = struct.unpack_from('>Bf', file, pos); pos += 5

                    _printMat("Alpha Compare function: %s" % _funcs[self.func])
                    _printMat("Alpha Compare: %f" % self.ref)

            class BlendMode:
                def __init__(self, file, pos, isAlpha=False):
                    _factors = [
                        "0", "1", "Destination Color", "Destination Inverse Color", "Source Alpha",
                        "Source Inverse Alpha", "Destination Alpha", "Destination Inverse Alpha",
                        "Source Color", "Source Inverse Color",
                    ]

                    _blendOp = [
                        "Disable", "Add", "Subtract", "Reverse Subtract",
                        "Select Min", "Select Max",
                    ]

                    _logicOp = [
                        "Disable", "No Op", "Clear", "Set", "Copy",
                        "InvCopy", "Inv", "And", "Nand", "Or",
                        "Nor", "Xor", "Equiv", "RevAnd",
                        "InvAnd", "RevOr", "InvOr",
                    ]

                    (self.blendOp,
                     self.srcFactor,
                     self.dstFactor,
                     self.logicOp) = struct.unpack_from('>4B', file, pos); pos += 4

                    if isAlpha:
                        _printMat("Alpha:")

                    _printMat("Blend Op: %s" % _blendOp[self.blendOp])
                    _printMat("Source factor: %s" % _factors[self.srcFactor])
                    _printMat("Destination factor: %s" % _factors[self.dstFactor])
                    _printMat("Logic Op: %s" % _logicOp[self.logicOp])

            class IndirectParameter:
                def __init__(self, file, pos):
                    self.rotate = struct.unpack_from('>f', file, pos); pos += 4
                    self.scale = struct.unpack_from('>2f', file, pos); pos += 8

                    _printMat("Indirect Rotation:", self.rotate)
                    _printMat("Indirect Scale:", self.scale)

            class ProjectionTexGenParamaters:
                def __init__(self, file, pos):
                    self.translate = struct.unpack_from('>2f', file, pos); pos += 8
                    self.scale = struct.unpack_from('>2f', file, pos); pos += 8
                    flag = file[pos]; pos += 4

                    self.isFittingLayoutSize = bool(flag & 1)
                    self.isFittingPaneSizeEnabled = bool(flag & 2)
                    self.isAdjustProjectionSREnabled = bool(flag & 4)

                    _printMat("Projection Translation:", self.translate)
                    _printMat("Projection Scale:", self.scale)
                    _printMat("Projection isFittingLayoutSize:", self.isFittingLayoutSize)
                    _printMat("Projection isFittingPaneSizeEnabled:", self.isFittingPaneSizeEnabled)
                    _printMat("Projection isAdjustProjectionSREnabled:", self.isAdjustProjectionSREnabled)

            class FontShadowParameter:
                def __init__(self, file, pos):
                    self.blackInterporateColor = struct.unpack_from('>3B', file, pos); pos += 3
                    self.whiteInterporateColor = struct.unpack_from('>4B', file, pos); pos += 5

                    _printMat("Font Shadow Black Interporate Color:", self.blackInterporateColor)
                    _printMat("Font Shadow White Interporate Color:", self.whiteInterporateColor)

            def __init__(self, file, pos):
                try:
                    self.name = readString(file[pos:pos + 28])
                    pos += 28

                except:
                    _printMat(hex(pos))
                    raise Exception from None

                if not self.name:
                    _printMat(hex(pos - 28))
                    raise Exception from None

                self.color0 = struct.unpack_from('>4B', file, pos); pos += 4
                self.color1 = struct.unpack_from('>4B', file, pos); pos += 4

                self.resNum = struct.unpack_from('>I', file, pos)[0]; pos += 4
                self.readResNum()

                _printMat('\n%s' % self.name)
                _printMat("Black Color:", self.color0)
                _printMat("White Color:", self.color1)
                _printMat("Resource Flags: %s" % bin(self.resNum))

                self.resTexMaps = []
                for i in range(self.texNum):
                    self.resTexMaps.append(self.TexMap(file, pos))
                    pos += 4

                self.texSRTs = []
                for i in range(self.texSRTNum):
                    self.texSRTs.append(self.TexSRT(file, pos))
                    pos += 20

                self.texCoordGen = []
                for i in range(self.texCoordGenNum):
                    self.texCoordGen.append(self.TexCoordGen(file, pos))
                    pos += 8

                self.tevStages = []
                for i in range(self.tevStageNum):
                    self.tevStages.append(self.TevStage(file, pos))
                    pos += 4

                self.alphaCompare = None
                if self.hasAlphaCompare:
                    self.alphaCompare = self.AlphaCompare(file, pos)
                    pos += 8

                self.blendType = "None"

                self.blendMode = None
                if self.hasBlendMode:
                    self.blendType = "Blend"
                    self.blendMode = self.BlendMode(file, pos)
                    pos += 4

                self.blendModeAlpha = None
                if self.isSeparateBlendMode:
                    self.blendType = "Logic"
                    self.blendModeAlpha = self.BlendMode(file, pos, True)
                    pos += 4

                self.indirectParameter = None
                if self.hasIndirectParameter:
                    self.indirectParameter = self.IndirectParameter(file, pos)
                    pos += 12

                self.projectionTexGenParameters = []
                for i in range(self.projectionTexGenNum):
                    self.projectionTexGenParameters.append(self.ProjectionTexGenParamaters(file, pos))
                    pos += 20

                if self.hasFontShadowParameter:
                    self.fontShadowParameter = self.FontShadowParameter(file, pos)
                    pos += 8

                numProjectionTexGen = 0
                for i in range(self.texCoordGenNum):
                    if self.texCoordGen[i].texGenSrc in [3, 4, 5]:
                        self.texCoordGen[i].projectionTexGenParameter = self.projectionTexGenParameters[numProjectionTexGen]
                        numProjectionTexGen += 1

            def readResNum(self):
                # resNum -> 0000000000000HFPPI0bTBAVVVCCSSMM
                self.texNum = self.resNum & 3
                self.texSRTNum = (self.resNum >> 2) & 3
                self.texCoordGenNum = (self.resNum >> 4) & 3
                self.tevStageNum = (self.resNum >> 6) & 7
                self.hasAlphaCompare = bool((self.resNum >> 9) & 1)
                self.hasBlendMode = bool((self.resNum >> 10) & 1)
                self.isTextureOnly = bool((self.resNum >> 11) & 1)
                self.isSeparateBlendMode = bool((self.resNum >> 12) & 1)
                self.hasIndirectParameter = bool((self.resNum >> 14) & 1)
                self.projectionTexGenNum = (self.resNum >> 15) & 3
                self.hasFontShadowParameter = bool((self.resNum >> 17) & 1)
                self.isThresholdingAlphaInterpolation = bool((self.resNum >> 18) & 1)

        def __init__(self, file, pos):
            super().__init__(file, pos); pos += 8

            self.materialNum = struct.unpack_from('>H', file, pos)[0]
            self.materials = []

            for i in range(self.materialNum):
                pMaterial = struct.unpack_from('>I', file, pos + 4 * (i+1))[0] + pos - 8
                self.materials.append(self.Material(file, pMaterial))

    class Pane(Section):
        def __init__(self, file, pos):
            super().__init__(file, pos); pos += 8

            _xModes = {
                0: "Center",
                1: "Left",
                2: "Right",
            }

            _yModes = {
                0: "Center",
                1: "Top",
                2: "Bottom",
            }

            (self.flag,
             self.basePosition,
             self.alpha,
             self.flagEx,
             nameBytes,
             userDataBytes) = struct.unpack_from('>4B24s8s', file, pos); pos += 36

            self.name = readString(nameBytes)
            self.userData = readString(userDataBytes)

            _printPan("\nPane name: %s" % self.name)
            _printPan("Pane visible:", bool(self.flag & 1))
            _printPan("Pane influenced alpha:", bool((self.flag >> 1) & 1))
            _printPan("Pane location adjust:", bool((self.flag >> 2) & 1))
            _printPan("Pane hidden (in editor?):", bool((self.flag >> 7) & 1))
            ignorePartsMagnify = bool(self.flagEx & 1)
            _printPan("Pane ignore parts magnify:", ignorePartsMagnify)
            if not ignorePartsMagnify:
                _printPan("Pane parts magnify influence:", bool((self.flagEx >> 1) & 1))

            parentRelativeY = (self.basePosition >> 6) & 3
            parentRelativeX = (self.basePosition >> 4) & 3
            baseY = (self.basePosition >> 2) & 3
            baseX = self.basePosition & 3

            _printPan("Pane base X position:", _xModes[baseX])
            _printPan("Pane base Y position:", _xModes[baseY])
            _printPan("Pane parent-relative X position:", _xModes[parentRelativeX])
            _printPan("Pane parent-relative Y position:", _xModes[parentRelativeY])

            self.translate = struct.unpack_from('>3f', file, pos); pos += 12
            self.rotate = struct.unpack_from('>3f', file, pos); pos += 12
            self.scale = struct.unpack_from('>2f', file, pos); pos += 8
            self.size = struct.unpack_from('>2f', file, pos); pos += 8

            _printPan("Pane translation:", self.translate)
            _printPan("Pane rotation:", self.rotate)
            _printPan("Pane scale:", self.scale)
            _printPan("Pane size:", self.size)

            self.parent = None
            self.childList = []

        def appendChild(self, pane):
            self.childList.append(pane)
            pane.parent = self

        def getChildren(self):
            childList = []

            for child in self.childList:
                childList.append(child)
                if child.childList:
                    childList.extend(child.getChildren())

            return childList

        def getAsTreeDict(self):
            childList = []

            for child in self.childList:
                if child.childList:
                    childList.append(child.getAsTreeDict())

                else:
                    childList.append(child.name)
                
            return {self.name: childList}

    class Picture(Pane):
        def __init__(self, file, pos):
            super().__init__(file, pos); pos += 84
            self.vtxCols = [struct.unpack_from('>4B', file, pos + 4*i) for i in range(4)]; pos += 16

            (self.materialIdx,
             self.texCoordNum) = struct.unpack_from('>HB', file, pos); pos += 4

            self.texCoords = []
            for _ in range(self.texCoordNum):
                self.texCoords.append([struct.unpack_from('>2f', file, pos + 8*z) for z in range(4)]); pos += 32

    class TextBox(Pane):
        class PerCharacterTransform:
            def __init__(self, file, pos):
                (self.evalTimeOffset,
                 self.evalTimeWidth,
                 self.loopType,
                 self.originV,
                 self.hasAnimationInfo) = struct.unpack_from('>2f3Bx', file, pos)

        def __init__(self, file, pos):
            initPos = pos
            super().__init__(file, pos); pos += 84

            (self.textBufBytes,
             self.textStrBytes,
             self.materialIdx,
             self.fontIdx,
             self.textPosition,
             self.textAlignment,
             self.textBoxFlag,
             self.italicRatio,
             self.textStrOffset) = struct.unpack_from('>4H3BxfI', file, pos); pos += 20

            self.readTextBoxFlag()

            self.textCols = [struct.unpack_from('>4B', file, pos + 4*i) for i in range(2)]; pos += 8
            self.fontSize = struct.unpack_from('>2f', file, pos); pos += 8

            (self.charSpace,
             self.lineSpace,
             self.textIDOffset) = struct.unpack_from('>2fI', file, pos); pos += 12

            self.shadowOffset = struct.unpack_from('>2f', file, pos); pos += 8
            self.shadowScale = struct.unpack_from('>2f', file, pos); pos += 8
            self.shadowCols = [struct.unpack_from('>4B', file, pos + 4*i) for i in range(2)]; pos += 8

            (self.shadowItalicRatio,
             self.perCharacterTransformOffset) = struct.unpack_from('>fI', file, pos); pos += 8

            pos = initPos + self.textStrOffset
            if self.forceAssignTextLength:
                self.text = readString(file[pos:pos + self.textStrBytes], 0, 2, 'utf-16be')

            else:
                self.text = readString(file[pos:pos + self.textBufBytes], 0, 2, 'utf-16be')

            pos = initPos + self.textIDOffset
            self.textID = readString(file, pos)

            self.perCharacterTransform = None
            if self.perCharacterTransformEnabled:
                if self.perCharacterTransformOffset:
                    pos = initPos + self.perCharacterTransformOffset
                    self.perCharacterTransform = self.PerCharacterTransform(file, pos); pos += 12
                    if self.perCharacterTransform.hasAnimationInfo:
                        self.perCharacterTransformAnimationInfo = FLAN.AnimationBlock.AnimationContent.AnimationInfo(file, pos)

                else:
                    print("Whoopsie-daisy")
                    self.perCharacterTransformEnabled = False

        def readTextBoxFlag(self):
            self.shadowEnabled = bool(self.textBoxFlag & 1)
            self.forceAssignTextLength = bool((self.textBoxFlag >> 1) & 1)
            self.invisibleBorderEnabled = bool((self.textBoxFlag >> 2) & 1)
            self.doubleDrawnBorderEnabled = bool((self.textBoxFlag >> 3) & 1)
            self.perCharacterTransformEnabled = bool((self.textBoxFlag >> 4) & 1)

    class Window(Pane):
        class WindowContent:
            def __init__(self, file, pos):
                self.vtxCols = [struct.unpack_from('>4B', file, pos + 4*i) for i in range(4)]; pos += 16

                (self.materialIdx,
                 self.texCoordNum) = struct.unpack_from('>HB', file, pos); pos += 4

                self.texCoords = []
                for _ in range(self.texCoordNum):
                    self.texCoords.append([struct.unpack_from('>2f', file, pos + 8*z) for z in range(4)]); pos += 32

        class WindowFrame:
            def __init__(self, file, pos):
                _modes = [
                    "None", "Flip Horizontal", "Flip Vertical", "Rotate 90",
                    "Rotate 180", "Rotate 270",
                ]

                (self.materialIdx,
                 self.textureFlip) = struct.unpack_from('>HB', file, pos)

        def __init__(self, file, pos):
            initPos = pos
            super().__init__(file, pos); pos += 84

            self.inflation = struct.unpack_from('>4h', file, pos); pos += 8
            self.frameSize = struct.unpack_from('>4H', file, pos); pos += 8

            (self.frameNum,
             self.windowFlags,
             self.contentOffset,
             self.frameOffsetTableOffset) = struct.unpack_from('>2B2x2I', file, pos); pos += 12

            self.readWindowFlags()

            pos = initPos + self.contentOffset
            self.content = self.WindowContent(file, pos)

            self.frames = []
            for i in range(self.frameNum):
                pos = initPos + self.frameOffsetTableOffset + 4*i
                pos = initPos + struct.unpack_from('>I', file, pos)[0]
                self.frames.append(self.WindowFrame(file, pos))

        def readWindowFlags(self):
            self.useOneMaterialForAll = bool(self.windowFlags & 1)
            self.useVtxColAll = bool((self.windowFlags >> 1) & 1)
            self.windowKind = (self.windowFlags >> 2) & 3
            self.notDrawContent = bool((self.windowFlags >> 4) & 1)

    class Bounding(Pane):
        pass

    class Parts(Pane):
        class PartsProperty:
            class PartsPaneBasicInfo:
                def __init__(self, file, pos):
                    self.userData = readString(struct.unpack_from('>8s', file, pos)[0]); pos += 8
                    self.translate = struct.unpack_from('>3f', file, pos); pos += 12
                    self.rotate = struct.unpack_from('>3f', file, pos); pos += 12
                    self.scale = struct.unpack_from('>2f', file, pos); pos += 8
                    self.size = struct.unpack_from('>2f', file, pos); pos += 8
                    self.alpha = file[pos]

            def __init__(self, file, initPos, pos):
                (nameBytes,
                 self.usageFlag,
                 self.basicUsageFlag,
                 self.propertyOffset,
                 self.extUserDataOffset,
                 self.paneBasicInfoOffset) = struct.unpack_from('>24s2B2x3I', file, pos)

                self.name = readString(nameBytes)

                self.property = None
                if self.propertyOffset:
                    self.property = readPane(file, initPos + self.propertyOffset)

                self.extUserData = None
                if self.extUserDataOffset:
                    self.extUserData = FLYT.ExtUserDataList.ExtUserData(file, initPos + self.extUserDataOffset)

                self.basicInfo = None
                if self.paneBasicInfoOffset:
                    self.basicInfo = self.PartsPaneBasicInfo(file, initPos + self.paneBasicInfoOffset)

        def __init__(self, file, pos):
            initPos = pos
            super().__init__(file, pos); pos += 84

            self.propertyNum, = struct.unpack_from('>I', file, pos); pos += 4
            self.magnify = struct.unpack_from('>2f', file, pos); pos += 8

            self.properties = [self.PartsProperty(file, initPos, pos + 40*i) for i in range(self.propertyNum)]
            pos += 40 * self.propertyNum

            self.filename = readString(file, pos)
            assert self.filename

    class ExtUserDataList(Section):
        class ExtUserData:
            def __init__(self, file, pos):
                (self.nameStrOffset,
                 self.dataOffset,
                 self.num,
                 self.type) = struct.unpack_from('>2IHB', file, pos)

                self.name = readString(file, pos + self.nameStrOffset)
                self.data = []

                if self.dataOffset:
                    if self.type == 0:
                        tempPos = pos + self.dataOffset
                        for _ in range(self.num):
                            _string = readString(file, tempPos); tempPos += len(string) + 1
                            self.data.append(_string)

                    elif self.type == 1:
                        self.data = struct.unpack_from('>%di' % self.num, file, pos + self.dataOffset)

                    elif self.type == 2:
                        self.data = struct.unpack_from('>%df' % self.num, file, pos + self.dataOffset)

        def __init__(self, file, pos):
            super().__init__(file, pos); pos += 8

            self.num, = struct.unpack_from('>H', file, pos); pos += 4
            self.extUserData = []
            for i in self.num:
                self.extUserData.append(self.ExtUserData(file, pos + 12*i))

    class Group(Section):
        def __init__(self, file, pos, major):
            super().__init__(file, pos); pos += 8

            if major < 5:
                fmt = '>24sH2x'
                size = 28

            else:
                fmt = '>33sxH'
                size = 36

            (nameBytes,
             self.paneNum) = struct.unpack_from(fmt, file, pos); pos += size

            self.name = readString(nameBytes)

            self.panes = []
            for i in range(self.paneNum):
                pane = readString(struct.unpack_from('>24s', file, pos + 24*i)[0])
                self.panes.append(pane)

        def save(self, major):
            fmt = '>24sH2x' if major < 5 else '>33sxH'
            buff1 = struct.pack(
                fmt,
                self.name.encode('utf-8'),
                len(self.panes),
            )

            buff2 = bytearray()
            for pane in self.panes:
                buff2 += struct.pack('>24s', pane.encode('utf-8'))

            self.data = b''.join([buff1, buff2])

            return super().save()

    def __init__(self, file):
        if file[4:6] != b'\xFE\xFF':
            raise NotImplementedError("Only big endian layouts are supported")  # TODO little endian

        (self.magic,
         self.headSize,
         self.version,
         self.fileSize,
         self.numSections) = struct.unpack_from('>4s2xH2IH', file)

        assert self.magic == b'FLYT'
        major = self.version >> 24  # TODO little endian
        if major not in [2, 5]:
            print("Untested BFLYT version: %s\n" % hex(self.version))

        self.lyt = None
        self.cnt = None
        self.txl = None
        self.fnl = None
        self.mat = None

        rootPaneSet = False
        parent = None
        lastPane = None
        bReadRootGroup = False
        self.groupList = []
        groupNestLevel = 0

        self.rootPane = None

        pos = 0x14
        for _ in range(self.numSections):
            if file[pos:pos + 4] == b'lyt1':
                self.lyt = self.Layout(file, pos)
                pos += self.lyt.blockHeader.size

            elif file[pos:pos + 4] == b'cnt1':
                self.cnt = self.Control(file, pos, major)
                pos += self.cnt.blockHeader.size

                if file[pos:pos + 4] == b'usd1':
                    self.cnt.extUserDataList = self.ExtUserDataList(file, pos)

            elif file[pos:pos + 4] == b'txl1':
                self.txl = self.TextureList(file, pos)
                pos += self.txl.blockHeader.size

            elif file[pos:pos + 4] == b'fnl1':
                self.fnl = self.FontList(file, pos)
                pos += self.fnl.blockHeader.size

            elif file[pos:pos + 4] == b'mat1':
                self.mat = self.MaterialList(file, pos)
                pos += self.mat.blockHeader.size

            elif file[pos:pos + 4] in [b'pan1', b'pic1', b'txt1', b'wnd1', b'bnd1', b'prt1']:
                pane = readPane(file, pos)

                if not rootPaneSet:
                    pane.isRootPane = rootPaneSet = True

                    # We don't need to add all panes to a list, since we can just get all panes from the root pane
                    self.rootPane = pane

                if parent:
                    parent.appendChild(pane)

                lastPane = pane
                pos += pane.blockHeader.size

            elif file[pos:pos + 4] == b'pas1':
                assert lastPane is not None
                parent = lastPane

                section = Section(file, pos)
                pos += section.blockHeader.size

            elif file[pos:pos + 4] == b'pae1':
                lastPane = parent
                parent = lastPane.parent

                section = Section(file, pos)
                pos += section.blockHeader.size

            elif file[pos:pos + 4] == b'grp1':
                if not bReadRootGroup:
                    bReadRootGroup = True

                    section = Section(file, pos)
                    pos += section.blockHeader.size

                elif groupNestLevel == 1:
                    group = self.Group(file, pos, major)
                    pos += group.blockHeader.size

                    self.groupList.append(group)

            elif file[pos:pos + 4] == b'grs1':
                groupNestLevel += 1

                section = Section(file, pos)
                pos += section.blockHeader.size

            elif file[pos:pos + 4] == b'gre1':
                groupNestLevel -= 1

                section = Section(file, pos)
                pos += section.blockHeader.size

            else:
                section = Section(file, pos)
                pos += section.blockHeader.size


def toVersion(file, output, dVersion):
    if file[4:6] != b'\xFE\xFF':
        raise NotImplementedError("Only big endian layouts are supported")  # TODO little endian

    (magic,
     version,
     numSections) = struct.unpack_from('>4s4xI4xH', file)

    assert magic == b'FLYT'

    file = bytearray(file)
    dMajor = dVersion >> 24
    major = version >> 24  # TODO little endian
    if major not in [2, 5]:
        print("Untested BFLYT version: %s\n" % hex(version))

    pos = 0x14
    for _ in range(numSections):
        if file[pos:pos + 4] == b'cnt1':
            cnt = FLYT.Control(file, pos, major)
            size = cnt.blockHeader.size

            file[pos:pos + size] = cnt.save(dMajor)
            pos += cnt.blockHeader.size

        elif file[pos:pos + 4] == b'grp1':
            group = FLYT.Group(file, pos, major)
            size = group.blockHeader.size

            file[pos:pos + size] = group.save(dMajor)
            pos += group.blockHeader.size

        else:
            section = Section(file, pos)
            pos += section.blockHeader.size

    file[:0x14] = struct.pack(
        '>4s2H2IH2x',
        b'FLYT',
        0xFEFF,
        20,
        dVersion,
        len(file),
        numSections,
    )

    with open(output, "wb") as out:
        out.write(file)


def main():
    file = input("Input (.bflyt):  ")
    output = input("Output (.bflyt):  ")
    version = int(input("Convert to version (e.g. 0x02020000):  "), 0)

    with open(file, "rb") as inf:
        inb = inf.read()

    toVersion(inb, output, version)


if __name__ == "__main__":
    main()
