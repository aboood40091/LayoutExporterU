from bflyt import FLYT
from common import Color4, MaterialName, UserData, LRName
from collections import OrderedDict
#import os


class Vec2:
    def __init__(self):
        self.x = 0
        self.y = 0

    def set(self, x, y):
        self.x, self.y = x, y

    def getAsDict(self):
        return {
            "@x": str(self.x),
            "@y": str(self.y),
        }


class Vec3:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0

    def set(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def getAsDict(self):
        return {
            "@x": self.x,
            "@y": self.y,
            "@z": self.z,
        }


class MaterialHSBAdjustment:
    def __init__(self):
        self.hOffset = 0.0
        self.sScale = 1.0
        self.bScale = 1.0

    def getAsDict(self):
        return {
            "@hOffset": self.hOffset,
            "@sScale": self.sScale,
            "@bScale": self.bScale,
        }


class TexVec2:
    def __init__(self):
        self.s = 0.0
        self.t = 0.0

    def set(self, s, t):
        self.s, self.t = s, t

    def getAsDict(self):
        return {
            "@s": str(self.s),
            "@t": str(self.t),
        }


class Position:
    def __init__(self):
        self.xModes = {
            0: "Center",
            1: "Left",
            2: "Right",
        }

        self.yModes = {
            0: "Center",
            1: "Top",
            2: "Bottom",
        }

        self.x = "Left"
        self.y = "Top"

    def set(self, x, y):
        assert x in self.xModes
        assert y in self.yModes
        self.x, self.y = self.xModes[x], self.yModes[y]

    def getAsDict(self):
        return {
            "@x": self.x,
            "@y": self.y,
        }


class BlackColor:
    def __init__(self):
        self.r = 0
        self.g = 0
        self.b = 0
        self.a = 0

    def set(self, r, g, b, a=0):
        self.r, self.g, self.b, self.a = r, g, b, a

    def getAsDict(self):
        _dict = {
            "@r": str(self.r),
            "@g": str(self.g),
            "@b": str(self.b),
        }

        if self.a != 0:
            _dict["@a"] = str(self.a)

        return _dict


class WhiteColor:
    def __init__(self):
        self.r = 255
        self.g = 255
        self.b = 255
        self.a = 255

    def set(self, r, g, b, a=255):
        self.r, self.g, self.b, self.a = r, g, b, a

    def getAsDict(self):
        _dict = {
            "@r": str(self.r),
            "@g": str(self.g),
            "@b": str(self.b),
        }

        if self.a != 255:
            _dict["@a"] = str(self.a)

        return _dict


class TexMapIDRef:
    def __init__(self):
        self.value = -1

    def set(self, value):
        assert -1 <= value <= 2
        self.value = value

    def getAsDict(self):
        return {"@texMap": str(self.value)}


class TexCoord:
    def __init__(self):
        self.texLT = TexVec2()
        self.texRT = TexVec2()
        self.texLB = TexVec2()
        self.texRB = TexVec2()

    def set(self, texLT, texRT, texLB, texRB):
        self.texLT.set(*texLT)
        self.texRT.set(*texRT)
        self.texLB.set(*texLB)
        self.texRB.set(*texRB)

    def getAsDict(self):
        return {
            "texLT": self.texLT.getAsDict(),
            "texRT": self.texRT.getAsDict(),
            "texLB": self.texLB.getAsDict(),
            "texRB": self.texRB.getAsDict(),
        }


class TexWrapMode:
    def __init__(self):
        self.modes = {
            0: "Clamp",
            1: "Repeat",
            2: "Mirror",
        }

        self.string = "Clamp"

    def set(self, mode):
        assert mode in self.modes
        self.string = self.modes[mode]

    def get(self):
        return self.string


class TexFilter:
    def __init__(self):
        self.filters = {
            0: "Near",
            1: "Linear",
        }

        self.string = "Linear"

    def set(self, filter):
        assert filter in self.filters
        self.string = self.filters[filter]

    def get(self):
        return self.string


class TexMap:
    def __init__(self):
        self.imageName = ""
        self.wrap_s = TexWrapMode()
        self.wrap_t = TexWrapMode()
        self.minFilter = TexFilter()
        self.magFilter = TexFilter()

    def set(self, texMap, textureList):
        texName = textureList[texMap.texIdx]
        assert len(texName) <= 128
        self.imageName = texName
        self.wrap_s.set(texMap.wrapS)
        self.wrap_t.set(texMap.wrapT)
        self.minFilter.set(texMap.minFilter)
        self.magFilter.set(texMap.magFilter)

    def getAsDict(self):
        _dict = {
            "@imageName": self.imageName,
            "@wrap_s": self.wrap_s.get(),
            "@wrap_t": self.wrap_t.get(),
        }

        minFilter = self.minFilter.get()
        if minFilter == "Near":
            _dict["@minFilter"] = "Near"

        magFilter = self.magFilter.get()
        if magFilter == "Near":
            _dict["@magFilter"] = "Near"

        return _dict


class TexMatrix:
    def __init__(self):
        self.scale = Vec2()
        self.translate = Vec2()

        self.rotate = 0.0

    def set(self, texMatrix):
        self.scale.set(*texMatrix.scale)
        self.translate.set(*texMatrix.translate)
        self.rotate, = texMatrix.rotate

    def getAsDict(self):
        return {
            "scale": self.scale.getAsDict(),
            "translate": self.translate.getAsDict(),
            "@rotate": str(self.rotate),
        }


class TexGenSrc:
    def __init__(self):
        self.sources = {
            0: "Tex0",
            1: "Tex1",
            2: "Tex2",
            3: "OrthogonalProjection",
            4: "PaneBasedProjection",
            5: "PerspectiveProjection",
        }

        self.string = "Tex0"

    def set(self, source):
        assert source in self.sources
        self.string = self.sources[source]

    def get(self):
        return self.string


class TexCoordGen:
    def __init__(self):
        self.projectionScale = Vec2()
        self.projectionTrans = Vec2()

        self.srcParam = TexGenSrc()
        self.fittingLayoutSizeEnabled = False
        self.fittingPaneSizeEnabled = False
        self.adjustProjectionSREnabled = False

    def set(self, texCoordGen):
        if texCoordGen.projectionTexGenParameter:
            self.projectionScale.set(*texCoordGen.projectionTexGenParameter.scale)
            self.projectionTrans.set(*texCoordGen.projectionTexGenParameter.translate)

            self.fittingLayoutSizeEnabled = texCoordGen.projectionTexGenParameter.isFittingLayoutSize
            self.fittingPaneSizeEnabled = texCoordGen.projectionTexGenParameter.isFittingPaneSizeEnabled
            self.adjustProjectionSREnabled = texCoordGen.projectionTexGenParameter.isAdjustProjectionSREnabled

        else:
            self.projectionScale.set(1.0, 1.0)
            self.projectionTrans.set(0.0, 0.0)

            self.fittingLayoutSizeEnabled = False
            self.fittingPaneSizeEnabled = False
            self.adjustProjectionSREnabled = False

        self.srcParam.set(texCoordGen.texGenSrc)

    def getAsDict(self):
        _dict = {
            "projectionScale": self.projectionScale.getAsDict(),
            "projectionTrans": self.projectionTrans.getAsDict(),
            "@srcParam": self.srcParam.get(),
        }

        if self.fittingLayoutSizeEnabled:
            _dict["@fittingLayoutSizeEnabled"] = "true"

        if self.fittingPaneSizeEnabled:
            _dict["@fittingPaneSizeEnabled"] = "true"

        if self.adjustProjectionSREnabled:
            _dict["@adjustProjectionSREnabled"] = "true"

        return _dict


class Material:
    def __init__(self):
        self.blackColor = BlackColor()
        self.whiteColor = WhiteColor()
        self.hsbAdjustment = MaterialHSBAdjustment()
        self.texMap = []  # TexMap
        self.texMatrix = []  # TexMatrix
        self.texCoordGen = []  # TexCoordGen
        self.textureStage = []  # TexMapIDRef
        self.texBlendRatio = []  # TexBlendRatio

        self.name = MaterialName()
        self.isThresholdingAlphaInterpolationEnabled = False

    def set(self, blackColor, whiteColor, texMap, textureList, texMatrix, texCoordGen, name, isThresholdingAlphaInterpolationEnabled=False):
        self.blackColor.set(*blackColor)
        self.whiteColor.set(*whiteColor)

        self.texMap = []
        for item in texMap:
            self.texMap.append(TexMap())
            self.texMap[-1].set(item, textureList)

        self.texMatrix = []
        for item in texMatrix:
            self.texMatrix.append(TexMatrix())
            self.texMatrix[-1].set(item)

        self.texCoordGen = []
        for item in texCoordGen:
            self.texCoordGen.append(TexCoordGen())
            self.texCoordGen[-1].set(item)

        self.textureStage = []
        for i in range(len(texMap)):
            self.textureStage.append(TexMapIDRef())
            self.textureStage[-1].set(i)

        self.name.set(name)
        self.isThresholdingAlphaInterpolationEnabled = isThresholdingAlphaInterpolationEnabled

    def getAsDict(self):
        _dict = {
            "blackColor": self.blackColor.getAsDict(),
            "whiteColor": self.whiteColor.getAsDict(),
            "hsbAdjustment": self.hsbAdjustment.getAsDict(),
            "@name" : self.name.get(),
        }

        if self.texMap:
            _dict["texMap"] = [texMap.getAsDict() for texMap in self.texMap]

        if self.texMatrix:
            _dict["texMatrix"] = [texMatrix.getAsDict() for texMatrix in self.texMatrix]

        if self.texCoordGen:
            _dict["texCoordGen"] = [texCoordGen.getAsDict() for texCoordGen in self.texCoordGen]

        if self.textureStage:
            _dict["textureStage"] = [textureStage.getAsDict() for textureStage in self.textureStage]

        if self.texBlendRatio:
            _dict["texBlendRatio"] = [texBlendRatio.getAsDict() for texBlendRatio in self.texBlendRatio]

        if self.isThresholdingAlphaInterpolationEnabled:
            _dict["@isThresholdingAlphaInterpolationEnabled"] = "true"

        return _dict


class TevMode:
    def __init__(self):
        self.modes = {
            0: "Replace",
            1: "Modulate",
            2: "Add",
            3: "AddSigned",
            4: "Interpolate",
            5: "Subtract",
            6: "AddMult",
            7: "MultAdd",
            8: "Overlay",
            9: "Indirect",
            10: "BlendIndirect",
            11: "EachIndirect",
        }

        self.string = "Replace"

    def set(self, mode):
        assert mode in self.modes
        self.string = self.modes[mode]

    def get(self):
        return self.string


class RGBCombine:
    def __init__(self):
        self.arg = [{"@source": "Constant", "@op": "Rgb"} for _ in range(3)]
        self.indirectScale = []

        self.mode = TevMode()
        self.konst = "K0"
        self.scale = "V1"
        self.indirectRotate = 0.0
        self.copyReg = False

    def set(self, mode, indirect):
        self.indirectScale = []
        self.indirectRotate = 0.0
        if indirect:
            self.indirectScale.append(Vec2())
            self.indirectScale.set(*indirect.scale)
            self.indirectRotate, = indirect.rotate

        self.mode.set(mode)

    def getAsDict(self):
        _dict = {
            "arg": self.arg,
            "@mode": self.mode.get(),
            "@konst": "K0",
            "@scale": "V1",
        }

        if self.indirectScale:
            _dict["indirectScale"], = self.indirectScale
            _dict["@indirectRotate"] = self.indirectRotate

        return _dict


class AlphaCombine:
    def __init__(self):
        self.arg = [{"@source": "Constant", "@op": "Alpha"} for _ in range(3)]

        self.mode = TevMode()
        self.konst = "K0"
        self.scale = "V1"
        self.copyReg = False

    def set(self, mode):
        self.mode.set(mode)

    def getAsDict(self):
        return {
            "arg": self.arg,
            "@mode": self.mode.get(),
            "@konst": "K0",
            "@scale": "V1",
        }


class TevStage:
    def __init__(self):
        self.rgb = RGBCombine()
        self.alpha = AlphaCombine()

    def set(self, tevStage, indirect=None):
        self.rgb.set(tevStage.combineRgb, indirect)
        self.alpha.set(tevStage.combineAlpha)

    def getAsDict(self):
        return {
            "rgb": self.rgb.getAsDict(),
            "alpha": self.alpha.getAsDict(),
        }


class Compare:
    def __init__(self):
        self.modes = {
            0: "Never",
            1: "Less",
            2: "LEqual",
            3: "Equal",
            4: "NEqual",
            5: "GEqual",
            6: "Greater",
            7: "Always",
        }

        self.string = "Always"

    def set(self, mode):
        assert mode in self.modes
        self.string = self.modes[mode]

    def get(self):
        return self.string


class AlphaCompare:
    def __init__(self):
        self.comp = Compare()
        self.ref = 0.0

    def set(self, alphaCompare=None):
        if alphaCompare:
            self.comp.set(alphaCompare.func)
            self.ref = alphaCompare.ref

    def getAsDict(self):
        return {
            "@comp": self.comp.get(),
            "@ref": str(self.ref),
        }


class BlendMode:
    def __init__(self):
        self.modes = [
            "None",
            "Blend",
            "Logic",
        ]

        self.string = "None"

    def set(self, mode):
        assert mode in self.modes
        self.string = mode

    def get(self):
        return self.string


class BlendFactor:
    def __init__(self):
        self.factors = {
            0: "V0",
            1: "V1_0",
            2: "DstClr",
            3: "InvDstClr",
            4: "SrcAlpha",
            5: "InvSrcAlpha",
            6: "DstAlpha",
            7: "InvDstAlpha",
            8: "SrcClr",
            9: "InvSrcClr",
        }

        self.string = "V0"

    def set(self, factor):
        assert factor in self.factors
        self.string = self.factors[factor]

    def get(self):
        return self.string


class BlendOp:
    def __init__(self):
        self.modes = {
            0: "None",
            1: "Add",
            2: "Subtract",
            3: "ReverseSubtract",
            4: "SelectMin",
            5: "SelectMax",
        }

        self.string = "None"

    def set(self, mode):
        assert mode in self.modes
        self.string = self.modes[mode]

    def get(self):
        return self.string


class LogicOp:
    def __init__(self):
        self.modes = {
            0: "None",
            1: "NoOp",
            2: "Clear",
            3: "Set",
            4: "Copy",
            5: "InvCopy",
            6: "Inv",
            7: "And",
            8: "Nand",
            9: "Or",
            10: "Nor",
            11: "Xor",
            12: "Equiv",
            13: "RevAnd",
            14: "InvAnd",
            15: "RevOr",
            16: "InvOr",
        }

        self.string = "None"

    def set(self, mode):
        assert mode in self.modes
        self.string = self.modes[mode]

    def get(self):
        return self.string


class Material_CTRBlendMode:
    def __init__(self):
        self.type = BlendMode()
        self.srcFactor = BlendFactor()
        self.dstFactor = BlendFactor()
        self.blendOp = BlendOp()
        self.logicOp = LogicOp()

    def set(self, type, blendMode=None, useDefault=False):
        if useDefault:
            self.type.set("Blend")
            self.srcFactor.set(4)
            self.dstFactor.set(5)
            self.blendOp.set(1)
            self.logicOp.set(0)

        else:
            if type != "Logic" and not blendMode:
                type = "None"

            self.type.set(type)

            if type != "None":
                self.srcFactor.set(blendMode.srcFactor)
                self.dstFactor.set(blendMode.dstFactor)
                self.blendOp.set(blendMode.blendOp)
                self.logicOp.set(blendMode.logicOp)

    def getAsDict(self):
        _dict = {"@type": self.type.get()}

        if self.type.get() != "None":
            _dict["@srcFactor"] = self.srcFactor.get()
            _dict["@dstFactor"] = self.dstFactor.get()

            if self.blendOp.get() != "None":
                _dict["@blendOp"] = self.blendOp.get()

            if self.logicOp.get() != "None":
                _dict["@logicOp"] = self.logicOp.get()

        return _dict


class Material_CTR:
    def __init__(self):
        self.tevColReg = Color4(); self.tevColReg.set(0, 0, 0, 0)
        self.tevConstReg = [Color4() for _ in range(6)]
        self.texMap = []  # TexMap
        self.texMatrix = []  # TexMatrix
        self.texCoordGen = []  # TexCoordGen
        self.tevStage = [TevStage()]  # TevStage
        self.alphaCompare = AlphaCompare()
        self.blendMode = Material_CTRBlendMode()
        self.blendModeAlpha = Material_CTRBlendMode()

        self.name = MaterialName()
        self.tevStageNum = 1
        self.useDefaultBlendSettings = False
        self.useDefaultAlphaTestSettings = False

    def set(self, blackColor, whileColor, texMap, textureList, texMatrix, texCoordGen, tevStage, name, indirect=None, alphaCompare=None, blendMode=None, blendModeAlpha=None, blendType="None"):
        r, g, b = blackColor
        self.tevColReg.set(r, g, b, 0)

        r, g, b = whileColor
        for color in self.tevConstReg:
            color.set(r, g, b, 255)

        self.texMap = []
        for item in texMap:
            self.texMap.append(TexMap())
            self.texMap[-1].set(item, textureList)

        self.texMatrix = []
        for item in texMatrix:
            self.texMatrix.append(TexMatrix())
            self.texMatrix[-1].set(item)

        self.texCoordGen = []
        for item in texCoordGen:
            self.texCoordGen.append(TexCoordGen())
            self.texCoordGen[-1].set(item)

        self.tevStage = []
        for item in tevStage:
            self.tevStage.append(TevStage())
            self.tevStage[-1].set(item, indirect)

        self.name.set(name)
        self.tevStageNum = len(tevStage)
        self.useDefaultBlendSettings = blendMode is None
        self.useDefaultAlphaTestSettings = alphaCompare is None

        self.alphaCompare.set(alphaCompare)
        self.blendMode.set(blendType, blendMode, self.useDefaultBlendSettings)
        self.blendModeAlpha.set(blendType, blendModeAlpha)

    def getAsDict(self):
        _dict = {
            "tevColReg": self.tevColReg.getAsDict(),
            "tevConstReg": [tevConstReg.getAsDict() for tevConstReg in self.tevConstReg],
            "alphaCompare": self.alphaCompare.getAsDict(),
            "blendMode": self.blendMode.getAsDict(),
            "blendModeAlpha": self.blendModeAlpha.getAsDict(),
            "@name" : self.name.get(),
            "@tevStageNum" : str(self.tevStageNum),
        }

        if self.texMap:
            _dict["texMap"] = [texMap.getAsDict() for texMap in self.texMap]

        if self.texMatrix:
            _dict["texMatrix"] = [texMatrix.getAsDict() for texMatrix in self.texMatrix]

        if self.texCoordGen:
            _dict["texCoordGen"] = [texCoordGen.getAsDict() for texCoordGen in self.texCoordGen]

        if self.tevStage:
            _dict["tevStage"] = [tevStage.getAsDict() for tevStage in self.tevStage]

        if self.useDefaultBlendSettings:
            _dict["@useDefaultBlendSettings"] = "true"

        if self.useDefaultAlphaTestSettings:
            _dict["@useDefaultAlphaTestSettings"] = "true"

        return _dict


class Picture:
    def __init__(self):
        self.vtxColLT = Color4()
        self.vtxColRT = Color4()
        self.vtxColLB = Color4()
        self.vtxColRB = Color4()
        self.texCoord = []
        self.material = Material()
        self.materialCtr = Material_CTR()

        self.detailSetting = False

    def set(self, pane, materialList, textureList):
        material = materialList[pane.materialIdx]
        vtxCols, texCoords = pane.vtxCols, pane.texCoords

        self.vtxColLT.set(*vtxCols[0])
        self.vtxColRT.set(*vtxCols[1])
        self.vtxColLB.set(*vtxCols[2])
        self.vtxColRB.set(*vtxCols[3])

        self.texCoord = []
        for texCoord in texCoords:
            self.texCoord.append(TexCoord())
            self.texCoord[-1].set(*texCoord)

        self.material.set(
            material.color0, material.color1, material.resTexMaps, textureList, material.texSRTs,
            material.texCoordGen, material.name, material.isThresholdingAlphaInterpolation,
        )

        self.materialCtr.set(
            material.color0[:3], material.color1[:3],
            material.resTexMaps, textureList, material.texSRTs, material.texCoordGen, material.tevStages,
            material.name, material.indirectParameter, material.alphaCompare,
            material.blendMode, material.blendModeAlpha, material.blendType,
        )

        if (material.hasAlphaCompare or material.hasBlendMode or material.isTextureOnly
                or material.isSeparateBlendMode or material.hasIndirectParameter
                or material.hasFontShadowParameter or material.isThresholdingAlphaInterpolation):
            self.detailSetting = True

    def getAsDict(self):
        _dict = {
            "vtxColLT": self.vtxColLT.getAsDict(),
            "vtxColRT": self.vtxColRT.getAsDict(),
            "vtxColLB": self.vtxColLB.getAsDict(),
            "vtxColRB": self.vtxColRB.getAsDict(),
            "material": self.material.getAsDict(),
            "materialCtr": self.materialCtr.getAsDict(),
        }

        if self.texCoord:
            _dict["texCoord"] = [texCoord.getAsDict() for texCoord in self.texCoord]

        if self.detailSetting:
            _dict["@detailSetting"] = "true"

        return _dict


class PerCharacterTransformLoopType:
    def __init__(self):
        self.loop = True

    def set(self, loop):
        self.loop = loop

    def get(self):
        return "Loop" if self.loop else "OneTime"


class VerticalPosition:
    def __init__(self):
        self.modes = {
            0: "Center",
            1: "Top",
            2: "Bottom",
        }

        self.string = "Center"

    def set(self, mode):
        assert mode in self.modes
        self.string = self.modes[mode]

    def get(self):
        return self.string


class TextAlignment:
    def __init__(self):
        self.modes = {
            0: "Synchronous",
            1: "Left",
            2: "Center",
            3: "Right",
        }

        self.string = "Synchronous"

    def set(self, mode):
        assert mode in self.modes
        self.string = self.modes[mode]

    def get(self):
        return self.string


class TextBox:
    def __init__(self):
        self.fontSize = Vec2()
        self.fontSizeOriginal = Vec2()
        self.text = ""
        self.textID = ""
        self.topColor = Color4()
        self.bottomColor = Color4()
        self.positionType = Position()
        self.material = Material()
        self.materialCtr = Material_CTR()
        self.shadowOffset = Vec2()
        self.shadowScale = Vec2()
        self.shadowTopColor = Color4()
        self.shadowBottomColor = Color4()

        self.font = ""
        self.charSpace = 0.0
        self.lineSpace = 0.0
        self.italicFactor = 0.0
        self.shadowItalicFactor = 0.0
        self.perCharacterTransformEnabled = False
        self.perCharacterTransformLoopType = PerCharacterTransformLoopType()  # Loop
        self.perCharacterTransformOriginV = VerticalPosition()  # Center
        self.perCharacterTransformEvalTimeOffset = 0.0
        self.perCharacterTransformEvalTimeWidth = 0.0
        self.shadowEnabled = False
        self.invisibleBorderEnabled = False
        self.doubleDrawnBorderEnabled = False
        self.textAlignment = TextAlignment()

        self.detailSetting = False

    def set(self, pane, materialList, textureList, fontList):
        material = materialList[pane.materialIdx]
        font = fontList[pane.fontIdx]

        self.fontSize.set(*pane.fontSize)
        self.fontSizeOriginal.set(*pane.fontSize)
        self.text = pane.text
        self.textID = pane.textID
        self.topColor.set(*pane.textCols[0])
        self.bottomColor.set(*pane.textCols[1])
        
        x = (pane.textPosition >> 2) & 3
        y = pane.textPosition & 3
        self.positionType.set(x, y)

        self.material.set(
            material.color0, material.color1, material.resTexMaps, textureList, material.texSRTs,
            material.texCoordGen, material.name, material.isThresholdingAlphaInterpolation,
        )

        self.materialCtr.set(
            material.color0[:3], material.color1[:3],
            material.resTexMaps, textureList, material.texSRTs, material.texCoordGen, material.tevStages,
            material.name, material.indirectParameter, material.alphaCompare,
            material.blendMode, material.blendModeAlpha, material.blendType,
        )

        self.shadowOffset.set(*pane.shadowOffset)
        self.shadowScale.set(*pane.shadowScale)
        self.shadowTopColor.set(*pane.shadowCols[0])
        self.shadowBottomColor.set(*pane.shadowCols[1])

        self.font = font
        self.charSpace = pane.charSpace
        self.lineSpace = pane.lineSpace
        self.italicFactor = pane.italicRatio
        self.shadowItalicFactor = pane.shadowItalicRatio
        
        self.perCharacterTransformEnabled = pane.perCharacterTransformEnabled

        if pane.perCharacterTransform:
            self.perCharacterTransformLoopType.set(bool(pane.perCharacterTransform.loopType))
            self.perCharacterTransformOriginV.set(pane.perCharacterTransform.originV)
            self.perCharacterTransformEvalTimeOffset = pane.perCharacterTransform.evalTimeOffset
            self.perCharacterTransformEvalTimeWidth = pane.perCharacterTransform.evalTimeWidth

        self.shadowEnabled = pane.shadowEnabled
        self.invisibleBorderEnabled = pane.invisibleBorderEnabled
        self.doubleDrawnBorderEnabled = pane.doubleDrawnBorderEnabled
        self.textAlignment.set(pane.textAlignment)

        if (material.hasAlphaCompare or material.hasBlendMode or material.isTextureOnly
                or material.isSeparateBlendMode or material.hasIndirectParameter
                or material.hasFontShadowParameter or material.isThresholdingAlphaInterpolation):
            self.detailSetting = True

    def getAsDict(self):
        _dict = {
            "fontSize": self.fontSize.getAsDict(),
            "text": self.text,
            "textID": self.textID,
            "topColor": self.topColor.getAsDict(),
            "bottomColor": self.bottomColor.getAsDict(),
            "positionType": self.positionType.getAsDict(),
            "material": self.material.getAsDict(),
            "materialCtr": self.materialCtr.getAsDict(),
            "shadowOffset": self.shadowOffset.getAsDict(),
            "shadowScale": self.shadowScale.getAsDict(),
            "shadowTopColor": self.shadowTopColor.getAsDict(),
            "shadowBottomColor": self.shadowBottomColor.getAsDict(),
            "@font": self.font,
        }

        if self.charSpace:
            _dict["@charSpace"] = str(self.charSpace)

        if self.lineSpace:
            _dict["@lineSpace"] = str(self.lineSpace)

        if self.italicFactor:
            _dict["@italicFactor"] = str(self.italicFactor)

        if self.shadowItalicFactor:
            _dict["@shadowItalicFactor"] = str(self.shadowItalicFactor)

        if self.perCharacterTransformEnabled:
            _dict["@perCharacterTransformEnabled"] = "true"

        if self.perCharacterTransformLoopType.get() != "Loop":
            _dict["@perCharacterTransformLoopType"] = self.perCharacterTransformLoopType.get()

        if self.perCharacterTransformOriginV.get() != "Center":
            _dict["@perCharacterTransformOriginV"] = self.perCharacterTransformOriginV.get()

        if self.perCharacterTransformEvalTimeOffset:
            _dict["@perCharacterTransformEvalTimeOffset"] = str(self.perCharacterTransformEvalTimeOffset)

        if self.perCharacterTransformEvalTimeWidth:
            _dict["@perCharacterTransformEvalTimeWidth"] = str(self.perCharacterTransformEvalTimeWidth)

        if self.shadowEnabled:
            _dict["@shadowEnabled"] = "true"

        if self.invisibleBorderEnabled:
            _dict["@invisibleBorderEnabled"] = "true"

        if self.doubleDrawnBorderEnabled:
            _dict["@doubleDrawnBorderEnabled"] = "true"

        if self.textAlignment.get() != "Synchronous":
            _dict["@textAlignment"] = self.textAlignment.get()

        if self.detailSetting:
            _dict["@detailSetting"] = "true"

        return _dict


class WindowContent:
    def __init__(self):
        self.vtxColLT = Color4()
        self.vtxColRT = Color4()
        self.vtxColLB = Color4()
        self.vtxColRB = Color4()
        self.texCoord = []
        self.material = Material()
        self.materialCtr = Material_CTR()

        self.detailSetting = False

    def set(self, content, materialList, textureList):
        material = materialList[content.materialIdx]
        vtxCols, texCoords = content.vtxCols, content.texCoords

        self.vtxColLT.set(*vtxCols[0])
        self.vtxColRT.set(*vtxCols[1])
        self.vtxColLB.set(*vtxCols[2])
        self.vtxColRB.set(*vtxCols[3])

        self.texCoord = []
        for texCoord in texCoords:
            self.texCoord.append(TexCoord())
            self.texCoord[-1].set(*texCoord)

        self.material.set(
            material.color0, material.color1, material.resTexMaps, textureList, material.texSRTs,
            material.texCoordGen, material.name, material.isThresholdingAlphaInterpolation,
        )

        self.materialCtr.set(
            material.color0[:3], material.color1[:3],
            material.resTexMaps, textureList, material.texSRTs, material.texCoordGen, material.tevStages,
            material.name, material.indirectParameter, material.alphaCompare,
            material.blendMode, material.blendModeAlpha, material.blendType,
        )

        if (material.hasAlphaCompare or material.hasBlendMode or material.isTextureOnly
                or material.isSeparateBlendMode or material.hasIndirectParameter
                or material.hasFontShadowParameter or material.isThresholdingAlphaInterpolation):
            self.detailSetting = True

    def getAsDict(self):
        _dict = {
            "vtxColLT": self.vtxColLT.getAsDict(),
            "vtxColRT": self.vtxColRT.getAsDict(),
            "vtxColLB": self.vtxColLB.getAsDict(),
            "vtxColRB": self.vtxColRB.getAsDict(),
            "material": self.material.getAsDict(),
            "materialCtr": self.materialCtr.getAsDict(),
        }

        if self.texCoord:
            _dict["texCoord"] = [texCoord.getAsDict() for texCoord in self.texCoord]

        if self.detailSetting:
            _dict["@detailSetting"] = "true"

        return _dict


class TextureFlip:
    def __init__(self):
        self.modes = {
            0: "None",
            1: "FlipH",
            2: "FlipV",
            3: "Rotate90",
            4: "Rotate180",
            5: "Rotate270",
        }

        self.string = "None"

    def set(self, mode):
        assert mode in self.modes
        self.string = self.modes[mode]

    def get(self):
        return self.string


class WindowFrameType:
    def __init__(self):
        self.types = {
            0: "CornerLT",
            1: "CornerRT",
            2: "CornerLB",
            3: "CornerRB",
            4: "FrameT",
            5: "FrameB",
            6: "FrameL",
            7: "FrameR",
        }

        self.string = "CornerLT"

    def set(self, type):
        assert type in self.types
        self.string = self.types[type]

    def get(self):
        return self.string


class WindowFrame:
    def __init__(self):
        self.textureFlip = TextureFlip()
        self.material = Material()
        self.materialCtr = Material_CTR()

        self.frameType = WindowFrameType()
        self.detailSetting = False

    def set(self, frame, i, materialList, textureList):
        material = materialList[frame.materialIdx]

        self.textureFlip.set(frame.textureFlip)
        self.frameType.set(i)

        self.material.set(
            material.color0, material.color1, material.resTexMaps, textureList, material.texSRTs,
            material.texCoordGen, material.name, material.isThresholdingAlphaInterpolation,
        )

        self.materialCtr.set(
            material.color0[:3], material.color1[:3],
            material.resTexMaps, textureList, material.texSRTs, material.texCoordGen, material.tevStages,
            material.name, material.indirectParameter, material.alphaCompare,
            material.blendMode, material.blendModeAlpha, material.blendType,
        )

        if (material.hasAlphaCompare or material.hasBlendMode or material.isTextureOnly
                or material.isSeparateBlendMode or material.hasIndirectParameter
                or material.hasFontShadowParameter or material.isThresholdingAlphaInterpolation):
            self.detailSetting = True

    def getAsDict(self):
        _dict = {
            "textureFlip": self.textureFlip.get(),
            "material": self.material.getAsDict(),
            "materialCtr": self.materialCtr.getAsDict(),
            "@frameType": self.frameType.get(),
        }

        if self.detailSetting:
            _dict["@detailSetting"] = "true"

        return _dict


class InflationRect:
    def __init__(self):
        self.l = 0.0
        self.r = 0.0
        self.t = 0.0
        self.b = 0.0

    def set(self, l, r, t, b):
        self.l, self.r, self.t, self.b = l, r, t, b

    def getAsDict(self):
        return {
            "@l": str(self.l),
            "@r": str(self.r),
            "@t": str(self.t),
            "@b": str(self.b),
        }


class WindowFrameSize:
    def __init__(self):
        self.l = 0.0
        self.r = 0.0
        self.t = 0.0
        self.b = 0.0

    def set(self, l, r, t, b):
        self.l, self.r, self.t, self.b = l, r, t, b

    def getAsDict(self):
        return {
            "@l": str(self.l),
            "@r": str(self.r),
            "@t": str(self.t),
            "@b": str(self.b),
        }


class WindowKind:
    def __init__(self):
        self.kinds = {
            0: "Around",
            1: "Horizontal",
            2: "HorizontalNoContent",
        }

        self.string = "Around"

    def set(self, kind):
        assert kind in self.kinds
        self.string = self.kinds[kind]

    def get(self):
        return self.string


class Window:
    def __init__(self):
        self.content = WindowContent()
        self.frame = [WindowFrame()]
        self.contentInflation = InflationRect()
        self.useLTMaterial = True  # dict
        self.frameSize = WindowFrameSize()

        self.kind = WindowKind()
        self.useVtxColorForAllWindow = False
        self.notDrawContent = False

    def set(self, pane, materialList, textureList):
        self.content.set(pane.content, materialList, textureList)

        assert pane.frames

        self.frame = []
        for i, frame in enumerate(pane.frames):
            self.frame.append(WindowFrame())
            self.frame[-1].set(frame, i, materialList, textureList)

        self.contentInflation.set(*pane.inflation)
        self.useLTMaterial = pane.useOneMaterialForAll
        self.frameSize.set(*pane.frameSize)
        self.kind.set(pane.windowKind)
        self.useVtxColorForAllWindow = pane.useVtxColAll
        self.notDrawContent = pane.notDrawContent

    def getAsDict(self):
        _dict = {
            "content": self.content.getAsDict(),
            "frame": [frame.getAsDict() for frame in self.frame],
            "contentInflation": self.contentInflation.getAsDict(),
            "useLTMaterial": {"@value": "true" if self.useLTMaterial else "false"},
            "frameSize": self.frameSize.getAsDict(),
            "@kind": self.kind.get(),
        }

        if self.useVtxColorForAllWindow:
            _dict["@useVtxColorForAllWindow"] = "true"

        if self.notDrawContent:
            _dict["@notDrawContent"] = "true"

        return _dict


class Bounding:
    def getAsDict(self):
        return None


class PartsPropertyUsageOptions:
    def __init__(self):
        self.options = {
            0: "None",
            1: "UseTextBoxText",
        }

        self.string = "None"

    def set(self, option):
        assert option in self.options
        self.string = self.options[option]

    def get(self):
        return self.string


class Property:
    def __init__(self):
        self.picture = None
        self.textBox = None
        self.window = None
        self.parts = None
        self.userData = None  # UserData
        self.basicUserData = ""
        self.alpha = None  # nillable
        self.visible = None  # nillable
        self.translate = None
        self.rotate = None
        self.scale = None
        self.size = None

        self.kind = PaneKind()
        self.target = LRName()
        self.usageOptions = PartsPropertyUsageOptions()  # default: None

    def set(self, property, materialList, textureList, fontList):
        if property.property:
            pane = property.property

            if isinstance(pane, FLYT.Picture):
                self.picture = Picture()
                self.picture.set(pane, materialList, textureList)
                self.kind.set(1)

            elif isinstance(pane, FLYT.TextBox):
                self.textBox = TextBox()
                self.textBox.set(pane, materialList, textureList, fontList)
                self.kind.set(2)

            elif isinstance(pane, FLYT.Window):
                self.window = Window()
                self.window.set(pane, materialList, textureList)
                self.kind.set(3)

            elif isinstance(pane, FLYT.Parts):
                self.parts = Parts()
                self.parts.set(pane, materialList, textureList, fontList)
                self.kind.set(5)

        if property.extUserData:
            self.userData = UserData()
            self.userData.set([property.extUserData])

        if property.basicInfo:
            self.basicUserData = property.basicInfo.userData
            self.alpha = property.basicInfo.alpha
            self.visible = bool(property.basicInfo.basicUsageFlag & 1)
            self.translate = Vec3(); self.translate.set(*property.basicInfo.translate)
            self.rotate = Vec3(); self.translate.set(*property.basicInfo.rotate)
            self.scale = Vec2(); self.translate.set(*property.basicInfo.scale)
            self.size = Vec2(); self.translate.set(*property.basicInfo.size)

        self.target.set(property.name)
        self.usageOptions.set(property.usageFlag)

    def getAsDict(self):
        _dict = {
            "@kind": self.kind.get(),
            "@target": self.target.get(),
            "@usageOptions": self.usageOptions.get(),
        }

        if self.picture:
            _dict["picture"] = self.picture.getAsDict()

        elif self.textBox:
            _dict["textBox"] = self.textBox.getAsDict()

        elif self.window:
            _dict["window"] = self.window.getAsDict()

        elif self.parts:
            _dict["parts"] = self.parts.getAsDict()

        if self.basicUserData:
            _dict["basicUserData"] = self.basicUserData

        if self.userData:
            _dict["userData"] = self.userData.getAsDict()

        if self.translate:
            _dict["alpha"] = self.alpha
            _dict["visible"] = self.visible
            _dict["translate"] = self.translate.getAsDict()
            _dict["rotate"] = self.rotate.getAsDict()
            _dict["scale"] = self.scale.getAsDict()
            _dict["size"] = self.size.getAsDict()

        return _dict


class Parts:
    def __init__(self):
        self.property = []  # Property
        self.magnify = Vec2()
        self.rawMagnify = Vec2()
        self.sizeConstraint = Vec2()

        self.path = ""

    def set(self, pane, materialList, textureList, fontList):
        properties, magnify, filename = pane.properties, pane.magnify, pane.filename

        """
        for property in properties:
            self.property.append(Property())
            self.property[-1].set(property, materialList, textureList, fontList)
        """

        self.magnify.set(*magnify)
        self.rawMagnify.set(*magnify)
        self.sizeConstraint.set(0.0, 0.0)

        # todo: add part reading
        print("please go convert %s.bflyt as well" % filename)
        self.path = filename + ".flyt"

    def getAsDict(self):
        _dict = {
            "magnify": self.magnify.getAsDict(),
            "rawMagnify": self.rawMagnify.getAsDict(),
            "sizeConstraint": self.sizeConstraint.getAsDict(),
            "@path": self.path,
        }

        if self.property:
            _dict["property"] = [property.getAsDict() for property in self.property]

        return _dict


class PaneKind:
    def __init__(self):
        self.kinds = {
            0: "Null",
            1: "Picture",
            2: "TextBox",
            3: "Window",
            4: "Bounding",
            5: "Parts",
        }

        self.string = "Null"

    def set(self, kind):
        assert kind in self.kinds
        self.string = self.kinds[kind]

    def get(self):
        return self.string


class PartsMagnifyInfluence:
    def __init__(self):
        self.string = "None"

    def set(self, adjustToPartsBound=False):
        if adjustToPartsBound:
            self.string = "AdjustToPartsBound"

        else:
            self.string = "ScaleMagnify"

    def get(self):
        return self.string


class Pane:
    def __init__(self):
        self.comment = ""
        self.basePositionType = Position()
        self.parentRelativePositionType = Position()
        self.translate = Vec3()
        self.rotate = Vec3()
        self.scale = Vec2()
        self.size = Vec2()
        self.picture = None
        self.textBox = None
        self.window = None
        self.bounding = None
        self.parts = None
        self.userData = UserData()

        self.kind = PaneKind()
        self.name = LRName()
        self.visible = True
        self.influencedAlpha = False
        self.hidden = False
        self.locked = False
        self.alpha = 255
        self.locationAdjust = False
        self.ignorePartsMagnify = False
        self.partsMagnifyInfluence = PartsMagnifyInfluence()
        self.readonlyLocked = False
        self.avoidPaneTreeCompression = False

    def set(self, pane, materialList, textureList, fontList):
        parentRelativeY = (pane.basePosition >> 6) & 3
        parentRelativeX = (pane.basePosition >> 4) & 3
        baseY = (pane.basePosition >> 2) & 3
        baseX = pane.basePosition & 3

        self.basePositionType.set(baseX, baseY)
        self.parentRelativePositionType.set(parentRelativeX, parentRelativeY)

        self.translate.set(*pane.translate)
        self.rotate.set(*pane.rotate)
        self.scale.set(*pane.scale)
        self.size.set(*pane.size)
        self.userData.setSingleStr(pane.userData)

        self.picture = None
        self.textBox = None
        self.window = None
        self.bounding = None
        self.parts = None

        if isinstance(pane, FLYT.Picture):
            self.picture = Picture()
            self.picture.set(pane, materialList, textureList)
            self.kind.set(1)

        elif isinstance(pane, FLYT.TextBox):
            self.textBox = TextBox()
            self.textBox.set(pane, materialList, textureList, fontList)
            self.kind.set(2)

        elif isinstance(pane, FLYT.Window):
            self.window = Window()
            self.window.set(pane, materialList, textureList)
            self.kind.set(3)

        elif isinstance(pane, FLYT.Bounding):
            self.bounding = Bounding()
            self.kind.set(4)

        elif isinstance(pane, FLYT.Parts):
            self.parts = Parts()
            self.parts.set(pane, materialList, textureList, fontList)
            self.kind.set(5)

        self.name.set(pane.name)
        self.visible = bool(pane.flag & 1)
        self.influencedAlpha = bool((pane.flag >> 1) & 1)
        self.locationAdjust = bool((pane.flag >> 2) & 1)
        self.hidden = bool((pane.flag >> 7) & 1)
        self.alpha = pane.alpha
        self.ignorePartsMagnify = bool(pane.flagEx & 1)
        if not self.ignorePartsMagnify:
            self.partsMagnifyInfluence.set(bool((pane.flagEx >> 1) & 1))

    def getAsDict(self):
        _dict = {
            "comment": self.comment,
            "basePositionType": self.basePositionType.getAsDict(),
            "parentRelativePositionType": self.parentRelativePositionType.getAsDict(),
            "translate": self.translate.getAsDict(),
            "rotate": self.rotate.getAsDict(),
            "scale": self.scale.getAsDict(),
            "size": self.size.getAsDict(),
            "userData": self.userData.getAsDict(),
            "@kind": self.kind.get(),
            "@name": self.name.get(),
        }

        if self.picture:
            _dict["picture"] = self.picture.getAsDict()

        elif self.textBox:
            _dict["textBox"] = self.textBox.getAsDict()

        elif self.window:
            _dict["window"] = self.window.getAsDict()

        elif self.bounding:
            _dict["bounding"] = self.bounding.getAsDict()

        elif self.parts:
            _dict["parts"] = self.parts.getAsDict()

        if not self.visible:
            _dict["@visible"] = "false"

        if self.influencedAlpha:
            _dict["@influencedAlpha"] = "true"

        if self.hidden:
            _dict["@hidden"] = "true"

        if self.locked:
            _dict["@locked"] = "true"

        if self.alpha != 255:
            _dict["@alpha"] = str(self.alpha)

        if self.locationAdjust:
            _dict["@locationAdjust"] = "true"

        if self.ignorePartsMagnify:
            _dict["@ignorePartsMagnify"] = "true"

        elif self.partsMagnifyInfluence.get() != "ScaleMagnify":
            _dict["@partsMagnifyInfluence"] = self.partsMagnifyInfluence.get()

        if self.readonlyLocked:
            _dict["@readonlyLocked"] = "true"

        if self.avoidPaneTreeCompression:
            _dict["@avoidPaneTreeCompression"] = "true"

        return _dict


class PaneSet:
    def __init__(self):
        self.panes = []

    def set(self, panes, materialList, textureList, fontList):
        for pane in panes:
            self.panes.append(Pane())
            self.panes[-1].set(pane, materialList, textureList, fontList)

    def getAsDict(self):
        return {"pane": [pane.getAsDict() for pane in self.panes]}


class PaneTree:
    def __init__(self):
        self.name = ""
        self.childList = []

    def set(self, pane):
        self.name = pane.name
        self.childList = []
        for child in pane.childList:
            paneTree = PaneTree()
            paneTree.set(child)
            self.childList.append(paneTree.getAsDict())

    def getAsDict(self):
        _dict = {"@name": self.name}

        if self.childList:
            _dict["paneTree"] = self.childList

        return _dict


class PaneHierarchy:
    def __init__(self, rootPane):
        self.rootPane = rootPane

    def getAsDict(self):
        paneTree = PaneTree()
        paneTree.set(self.rootPane)

        return {"paneTree": paneTree.getAsDict()}


class GroupPaneRef:
    def __init__(self):
        self.name = LRName()

    def set(self, name):
        self.name.set(name)

    def getAsDict(self):
        return {"@name": self.name.get()}


class Group:
    def __init__(self):
        self.paneRef = []  # GroupPaneRef
        self.comment = None

        self.name = ""

    def set(self, group):
        self.name = group.name
        self.paneRef = []
        for pane in group.panes:
            self.paneRef.append(GroupPaneRef())
            self.paneRef[-1].set(pane)

    def getAsDict(self):
        _dict = {
            "comment": self.comment,
            "@name": self.name,
        }

        if self.paneRef:
            _dict["paneRef"] = [paneRef.getAsDict() for paneRef in self.paneRef]

        return _dict


class RootGroup:
    def __init__(self):
        self.group = []
        self.comment = None

    def set(self, groupList):
        self.group = []
        for group in groupList:
            self.group.append(Group())
            self.group[-1].set(group)

    def getAsDict(self):
        _dict = {
            "comment": self.comment,
            "@name": "RootGroup",
        }

        if self.group:
            _dict["group"] = [group.getAsDict() for group in self.group]

        return _dict


class GroupSet:
    def __init__(self, groupList):
        self.groupList = groupList

    def getAsDict(self):
        rootGroup = RootGroup()
        rootGroup.set(self.groupList)

        return {"group": rootGroup.getAsDict()}


class BackGround:
    def __init__(self):
        self.color = Color4()
        self.color.set(169, 169, 169, 255)

    def getAsDict(self):
        return {"color": self.color.getAsDict()}


class Grid:
    def __init__(self):
        self.color = Color4()
        self.color.set(128, 128, 64, 128)

        self.moveMethod = "None"
        self.visible = "false"  # todo make this editable
        self.thinDivisionNum = "4"
        self.thickLineInterval = "40"

    def getAsDict(self):
        return {
            "color": self.color.getAsDict(),
            "@moveMethod": self.moveMethod,
            "@visible": self.visible,
            "@thinDivisionNum": self.thinDivisionNum,
            "@thickLineInterval": self.thickLineInterval,
        }


class ScreenOriginType:
    def __init__(self):
        self.types = {
            0: "Classic",
            1: "Normal",
        }

        self.string = "Classic"

    def set(self, type):
        assert type in self.types
        self.string = self.types[type]

    def get(self):
        return self.string


class ScreenSetting:
    def __init__(self):
        self.layoutSize = Vec2()
        self.backGround = BackGround()
        self.grid = Grid()

        self.origin = ScreenOriginType()

    def set(self, width, height, origin):
        self.layoutSize.set(width, height)
        self.origin.set(origin)

    def getAsDict(self):
        return {
            "layoutSize": self.layoutSize.getAsDict(),
            "backGround": self.backGround.getAsDict(),
            "grid": self.grid.getAsDict(),
            "@origin": self.origin.get(),
        }


class ControlParameterPane:
    def __init__(self):
        self.name = ""
        self.paneName = LRName()

    def set(self, paneName, name):
        self.paneName.set(paneName)
        self.name = name

    def getAsDict(self):
        return {
            "@name": self.name,
            "@paneName": self.paneName.get(),
        }


class ControlParameterAnimation:
    def __init__(self):
        self.name = ""
        self.tagName = ""

    def set(self, tagName, name):
        self.tagName = tagName
        self.name = name

    def getAsDict(self):
        return {
            "@name": self.name,
            "@tagName": self.tagName,
        }


class Control:
    def __init__(self):
        self.parameterPane = []  # ControlParameterPane
        self.parameterAnimation = []  # ControlParameterAnimation
        self.userData = None  # UserData

        self.name = ""
        self.userName = ""

    def set(self, name, userName, paneNames, animNames, paneParameterNames, animParameterNames, extUserDataList):
        self.name = name
        self.userName = userName

        if not self.userName:
            self.userName = name

        self.parameterPane = []
        if paneNames:
            if not paneParameterNames:
                paneParameterNames = paneNames

            for paneName, paneParameterName in zip(paneNames, paneParameterNames):
                self.parameterPane.append(ControlParameterPane())
                self.parameterPane[-1].set(paneName, paneParameterName)

        self.parameterAnimation = []
        if animNames:
            if not animParameterNames:
                animParameterNames = animNames

            for animName, animParameterName in zip(animNames, animParameterNames):
                self.parameterAnimation.append(ControlParameterAnimation())
                self.parameterAnimation[-1].set(animName, animParameterName)

        self.userData = None
        if extUserDataList:
            self.userData = UserData()
            self.userData.set(extUserDataList)

    def getAsDict(self):
        _dict = {"@name": self.name, "@userName": self.userName}

        if self.parameterPane:
            _dict["parameterPane"] = [parameterPane.getAsDict() for parameterPane in self.parameterPane]

        if self.parameterAnimation:
            _dict["parameterAnimation"] = [parameterAnimation.getAsDict() for parameterAnimation in self.parameterAnimation]

        if self.userData:
            _dict["userData"] = self.userData.getAsDict()

        return _dict


class TexelFormat:
    def __init__(self, format):
        formats = {
            "a": "L4",
            "b": "A4",
            "c": "L8",
            "d": "A8",
            "e": "LA4",
            "f": "LA8",
            "g": "HILO8",
            "h": "RGB565",
            "i": "RGB8",
            "j": "RGB5A1",
            "k": "RGBA4",
            "l": "RGBA8",
            "m": "ETC1",
            "n": "ETC1A4",
            "o": "BC1",
            "p": "BC2",
            "q": "BC3",
            "r": "BC4L",
            "s": "BC4A",
            "t": "BC5",
            "u": "RGB565_INDIRECT",
        }

        assert format in formats
        self.format = formats[format]

    def get(self):
        return self.format


class TextureFile:
    def __init__(self, texture, format, path=".\\Textures"):
        # todo automatic texture conversion
        #self.imagePath = os.path.join(path, '%s.tga' % texture)
        self.imagePath = '%s\\%s.tga' % (path, texture)
        self.format = TexelFormat(format)
        print(self.imagePath, format, self.format.get())

    def getAsDict(self):
        return {
            "@imagePath": self.imagePath,
            "@format": self.format.get(),
        }


class FontFile:
    def __init__(self, font, path=".\\Fonts"):
        # todo automatic font fetching
        #self.path = os.path.join(path, '%s.bffnt' % font)
        self.path = '%s\\%s.bffnt' % (path, font)
        print(self.path)
        self.name = '%s.bffnt' % font

    def getAsDict(self):
        return {
            "@path": self.path,
            "@name": self.name,
        }


class Layout:
    def __init__(self, file, textures, formats):
        with open(file, "rb") as inf:
            inb = inf.read()

        self.flyt = FLYT(inb)
        if self.flyt.txl and textures and formats:
            for texture, format in zip(textures, formats):
                if texture not in self.flyt.txl.textures:
                    self.flyt.txl.textures.append(texture)
                    self.flyt.txl.formats.append(format)

    def getAsDict(self):
        if self.flyt.rootPane and self.flyt.lyt:
            rootPane = self.flyt.rootPane
            layout = self.flyt.lyt

            if self.flyt.txl:
                textures = self.flyt.txl.textures
                formats = self.flyt.txl.formats

            else:
                textures = []
                formats = []

            if self.flyt.fnl:
                fonts = self.flyt.fnl.fonts

            else:
                fonts = []

            if self.flyt.mat:
                materials = self.flyt.mat.materials

            else:
                materials = []

            paneSet = PaneSet()
            paneSet.set(rootPane.getChildren(), materials, textures, fonts)

            paneHierarchy = PaneHierarchy(rootPane)
            groupSet = GroupSet(self.flyt.groupList)
            screenSetting = ScreenSetting()
            screenSetting.set(layout.layoutWidth, layout.layoutHeight, layout.originType)

            control = None
            if self.flyt.cnt:
                cnt = self.flyt.cnt

                control = Control()
                control.set(
                    cnt.controlName, cnt.controlUserName, cnt.controlFunctionalPaneNames,
                    cnt.controlFunctionalAnimNames, cnt.controlFunctionalPaneParameterNames,
                    cnt.controlFunctionalAnimParameterNames, cnt.extUserDataList,
                )

            textureList = []
            fontList = []

            for texture, format in zip(textures, formats):
                textureList.append(TextureFile(texture, format))

            for font in fonts:
                fontList.append(FontFile(font))

            _dict = OrderedDict()
            _dict["paneSet"] = paneSet.getAsDict()
            _dict["paneHierarchy"] = paneHierarchy.getAsDict()
            _dict["groupSet"] = groupSet.getAsDict()
            _dict["screenSetting"] = screenSetting.getAsDict()

            if control:
                _dict["control"] = control.getAsDict()

            if textureList:
                _dict["textureFile"] = [texture.getAsDict() for texture in textureList]

            if fontList:
                _dict["fontFile"] = [font.getAsDict() for font in fontList]

            return _dict

        return None
