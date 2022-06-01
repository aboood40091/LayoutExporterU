from typing import Any
from bflan import FLAN
from common import dictToXml, Head, Color4, MaterialName, UserData, LRName
from collections import OrderedDict
import os

class AnimShareInfo:
    def __init__(self):
        self.comment: str = ""

        self.srcPaneName: str = ""
        self.targetGroupName = LRName()

    def set(self, srcPaneName: str, targetGroupName: str):
        self.srcPaneName = srcPaneName
        self.targetGroupName.set(targetGroupName)

    def getAsDict(self):
        _dict = {
            "@srcPaneName": self.srcPaneName,
            "@targetGroupName": self.targetGroupName.get(),
        }

        if self.comment:
            _dict["comment"] = self.comment

        return _dict


class AnimShare:
    def __init__(self):
        self.targetTagName = ""
        self.animShareInfo = [AnimShareInfo()]

    def set(self, animShareInfos: list[AnimShareInfo], targetTagName: str = ""):
        self.targetTagName = targetTagName

        self.animShareInfo: list[AnimShareInfo] = []
        for animShareInfo in animShareInfos:
            self.animShareInfo.append(AnimShareInfo())
            self.animShareInfo[-1].set(animShareInfo.srcPaneName, animShareInfo.targetGroupName)  # type: ignore

    def getAsDict(self):
        _dict = {"animShareInfo": [animShareInfo.getAsDict for animShareInfo in self.animShareInfo]}

        if self.targetTagName:
            _dict["targetTagName"] = self.targetTagName  # type: ignore

        return _dict


class AnimLoopType:
    def __init__(self):
        self.loop = True

    def set(self, loop: bool):
        self.loop = loop

    def get(self):
        return "Loop" if self.loop else "OneTime"


class GroupRef:
    def __init__(self):
        self.name = LRName()

    def set(self, name: str):
        self.name.set(name)

    def getAsDict(self):
        return {"@name": self.name.get()}


class AnimTag:
    def __init__(self):
        self.comment: str = ""
        self.userData = None  # AnimTag doesn't even have user data in BFLAN lol
        self.color = None  # AnimTag doesn't even have color in BFLAN lol
        self.group: list[GroupRef] = None  # type: ignore

        self.name: str = ""
        self.startFrame: int = 0
        self.endFrame: int = 0
        self.animLoop = AnimLoopType()  # default: Loop
        self.fileName: str = ""  # not required
        self.descendingBind = True

    def set(self, tag: Any, loop: bool, extUserDataList: list[Any] = [], color: list[int] = []):
        groups: list[GroupRef] = tag.groups
        self.group = []
        for group in groups:
            self.group.append(GroupRef())
            self.group[-1].set(group.name)  # type: ignore

        self.name = tag.name
        self.startFrame = tag.startFrame
        self.endFrame = tag.endFrame
        self.animLoop.set(loop)
        self.fileName = tag.name
        self.descendingBind = bool(tag.flag & 1)

        self.userData = None
        if extUserDataList:
            self.userData = UserData()
            self.userData.set(extUserDataList)  # type: ignore

        self.color = None
        if color:
            self.color = Color4()
            self.color.set(*color)

    def getAsDict(self):
        _dict: dict[str, Any] = {
            "@name": self.name,
            "@startFrame": str(self.startFrame),
            "@endFrame": str(self.endFrame),
            "comment": self.comment,
        }

        if self.userData:
            _dict["userData"] = self.userData.getAsDict()

        if self.color:
            _dict["color"] = self.color.getAsDict()

        if self.group:
            _dict["group"] = [group.getAsDict() for group in self.group]

        if self.animLoop.get() != "Loop":
            _dict["@animLoop"] = self.animLoop.get()

        if self.fileName:
            _dict["@fileName"] = self.fileName

        if not self.descendingBind:
            _dict["@descendingBind"] = "false"

        return _dict


class AnimTargetType:
    def __init__(self):
        self.paneTargets = [
            "TranslateX",
            "TranslateY",
            "TranslateZ",
            "RotateX",
            "RotateY",
            "RotateZ",
            "ScaleX",
            "ScaleY",
            "SizeW",
            "SizeH",
        ]

        self.paneColorTargets = [
            "LT_r",
            "LT_g",
            "LT_b",
            "LT_a",
            "RT_r",
            "RT_g",
            "RT_b",
            "RT_a",
            "LB_r",
            "LB_g",
            "LB_b",
            "LB_a",
            "RB_r",
            "RB_g",
            "RB_b",
            "RB_a",
            "PaneAlpha",
        ]

        self.matColorTargets = [
            "BlackColor_r",
            "BlackColor_g",
            "BlackColor_b",
            "BlackColor_a",
            "WhiteColor_r",
            "WhiteColor_g",
            "WhiteColor_b",
            "WhiteColor_a",
        ]

        self.fontShadowTargets = [
            "FontShadowBlackColor_r",
            "FontShadowBlackColor_g",
            "FontShadowBlackColor_b",
            "FontShadowWhiteColor_r",
            "FontShadowWhiteColor_g",
            "FontShadowWhiteColor_b",
            "FontShadowWhiteColor_a",
        ]

        self.texSRTTargets = [
            "TranslateS",
            "TranslateT",
            "Rotate",
            "ScaleS",
            "ScaleT",
        ]

        self.perCharacterTransformCurveTargets = [
            "PerCharacterTransformTranslateX",
            "PerCharacterTransformTranslateY",
            "PerCharacterTransformTranslateZ",
            "PerCharacterTransformRotateX",
            "PerCharacterTransformRotateY",
            "PerCharacterTransformRotateZ",
        ]

        self.value: str = ""

    def set(self, value: str):
        self.value = value

    def get(self):
        return self.value


class Step:
    def __init__(self):
        self.frame: float = 0.0
        self.value: float = 0.0
        self.slopeType: str = "Step"

    def set(self, startFrame: float, key: 'Step'):
        self.frame = startFrame + key.frame
        self.value = key.value

    def getAsDict(self):
        return {
            "@frame": str(self.frame),
            "@value": str(self.value),
            "@slopeType": self.slopeType,
        }


class Hermite:
    def __init__(self):
        self.frame: float = 0.0
        self.value: float = 0.0
        self.slope: float = 0.0

    def set(self, startFrame: float, key: 'Hermite'):
        self.frame = startFrame + key.frame
        self.value = key.value
        self.slope = key.slope

    def getAsDict(self):
        return {
            "@frame": str(self.frame),
            "@value": str(self.value),
            "@slope": str(self.slope),
        }


class RefRes:
    def __init__(self):
        self.name: str = ""

    def set(self, name: str):
        self.name = name

    def getAsDict(self):
        return {"@name": self.name}


class AnimTarget:
    def __init__(self):
        self.key: list[Step or Hermite] = []

        self.id: int = 0
        self.target = AnimTargetType()

        self.idx: int = 0
        self.lan: Lan = None  # type: ignore
        self.isTexPattern: bool = False

    def __eq__(self, other: object) -> bool:
        return self.idx == other.idx  # type: ignore

    def addKeys(self, startFrame: Any, curveType: Any, keys: list[Any]):
        func: Any = None
        if curveType:
            if curveType == 1:
                func = Step

            else:
                func = Hermite

        for key in keys:
            self.key.append(func())
            self.key[-1].set(startFrame, key)  # type: ignore

    def set(self, startFrame: Any, curveType: Any, keys: list[Any], id: int, type_: str, target: int, lan: 'Lan'):
        self.id = id
        self.lan = lan

        self.idx = target
        if type_ in ["TextureSRT", "TexturePattern", "IndTextureSRT"]:
            self.idx |= id << 8

        self.key = []
        self.addKeys(startFrame, curveType, keys)

        if type_ == "PaneSRT":
            self.target.set(self.target.paneTargets[target])

        elif type_ == "Visibility":
            self.target.set("Visibility")

        elif type_ == "VertexColor":
            self.target.set(self.target.paneColorTargets[target])

        elif type_ == "MaterialColor":
            self.target.set(self.target.matColorTargets[target])

        elif type_ == "TextureSRT":
            self.target.set(self.target.texSRTTargets[target])

        elif type_ == "TexturePattern":
            self.target.set("Image")
            self.isTexPattern = True

        elif type_ == "IndTextureSRT":
            self.target.set(self.target.texSRTTargets[target + 2])

        elif type_ == "AlphaTest":
            self.target.set("AlphaTest")

        elif type_ == "FontShadow":
            self.target.set(self.target.fontShadowTargets[target])

        elif type_ == "PerCharacterTransform":
            self.target.set("PerCharacterTransformEvalTimeOffset")

        elif type_ == "PerCharacterTransformCurve":
            self.target.set(self.target.perCharacterTransformCurveTargets[target])

    def getAsDict(self):
        _dict: dict[str, Any] = {
            "@id": str(self.id),
            "@target": self.target.get(),
        }

        if self.isTexPattern:
            _dict["refRes"] = [{"@name": refRes} for refRes in self.lan.refRes]

        if self.key:
            _dict["key"] = [key.getAsDict() for key in self.key]

        return _dict


class AnimContent:
    def __init__(self):
        self.animPaneSRTTarget = []
        self.animVisibilityTarget = []
        self.animVertexColorTarget = []
        self.animMaterialColorTarget = []
        self.animTexSRTTarget = []
        self.animTexPatternTarget = []
        self.animIndTexSRTTarget = []
        self.animAlphaTestTarget = []
        self.animFontShadowTarget = []
        self.animPerCharacterTransformEvalTarget = []
        self.animPerCharacterTransformCurveTarget = []

        self.name = MaterialName()

    def set(self, name: str, targetsUsed: list[Any], type_: str):
        self.name.set(name)

        self.animPaneSRTTarget: list[Any] = []
        self.animVisibilityTarget: list[Any] = []
        self.animVertexColorTarget: list[Any] = []
        self.animMaterialColorTarget: list[Any] = []
        self.animTexSRTTarget: list[Any] = []
        self.animTexPatternTarget: list[Any] = []
        self.animIndTexSRTTarget: list[Any] = []
        self.animAlphaTestTarget: list[Any] = []
        self.animFontShadowTarget: list[Any] = []
        self.animPerCharacterTransformEvalTarget: list[Any] = []
        self.animPerCharacterTransformCurveTarget: list[Any] = []

        if type_ == "PaneSRT":
            extend = self.animPaneSRTTarget.extend

        elif type_ == "Visibility":
            extend = self.animVisibilityTarget.extend

        elif type_ == "VertexColor":
            extend = self.animVertexColorTarget.extend

        elif type_ == "MaterialColor":
            extend = self.animMaterialColorTarget.extend

        elif type_ == "TextureSRT":
            extend = self.animTexSRTTarget.extend

        elif type_ == "TexturePattern":
            extend = self.animTexPatternTarget.extend

        elif type_ == "IndTextureSRT":
            extend = self.animIndTexSRTTarget.extend

        elif type_ == "AlphaTest":
            extend = self.animAlphaTestTarget.extend

        elif type_ == "FontShadow":
            extend = self.animFontShadowTarget.extend

        elif type_ == "PerCharacterTransform":
            extend = self.animPerCharacterTransformEvalTarget.extend

        elif type_ == "PerCharacterTransformCurve":
            extend = self.animPerCharacterTransformCurveTarget.extend

        extend(targetsUsed)  # type: ignore

    def getAsDict(self):
        _dict: dict[str, Any] = {"@name": self.name.get()}

        if self.animPaneSRTTarget:
            _dict["animPaneSRTTarget"] = [animPaneSRTTarget.getAsDict() for animPaneSRTTarget in self.animPaneSRTTarget]

        if self.animVisibilityTarget:
            _dict["animVisibilityTarget"] = [animVisibilityTarget.getAsDict() for animVisibilityTarget in self.animVisibilityTarget]

        if self.animVertexColorTarget:
            _dict["animVertexColorTarget"] = [animVertexColorTarget.getAsDict() for animVertexColorTarget in self.animVertexColorTarget]

        if self.animMaterialColorTarget:
            _dict["animMaterialColorTarget"] = [animMaterialColorTarget.getAsDict() for animMaterialColorTarget in self.animMaterialColorTarget]

        if self.animTexSRTTarget:
            _dict["animTexSRTTarget"] = [animTexSRTTarget.getAsDict() for animTexSRTTarget in self.animTexSRTTarget]

        if self.animTexPatternTarget:
            _dict["animTexPatternTarget"] = [animTexPatternTarget.getAsDict() for animTexPatternTarget in self.animTexPatternTarget]

        if self.animIndTexSRTTarget:
            _dict["animIndTexSRTTarget"] = [animIndTexSRTTarget.getAsDict() for animIndTexSRTTarget in self.animIndTexSRTTarget]

        if self.animAlphaTestTarget:
            _dict["animAlphaTestTarget"] = [animAlphaTestTarget.getAsDict() for animAlphaTestTarget in self.animAlphaTestTarget]

        if self.animFontShadowTarget:
            _dict["animFontShadowTarget"] = [animFontShadowTarget.getAsDict() for animFontShadowTarget in self.animFontShadowTarget]

        if self.animPerCharacterTransformEvalTarget:
            _dict["animPerCharacterTransformEvalTarget"] = [animPerCharacterTransformEvalTarget.getAsDict() for animPerCharacterTransformEvalTarget in self.animPerCharacterTransformEvalTarget]

        if self.animPerCharacterTransformCurveTarget:
            _dict["animPerCharacterTransformCurveTarget"] = [animPerCharacterTransformCurveTarget.getAsDict() for animPerCharacterTransformCurveTarget in self.animPerCharacterTransformCurveTarget]

        return _dict


class AnimationType:
    def __init__(self):
        self.types = {
            b'FLPA': "PaneSRT",
            b'FLVI': "Visibility",
            b'FLVC': "VertexColor",
            b'FLMC': "MaterialColor",
            b'FLTS': "TextureSRT",
            b'FLTP': "TexturePattern",
            b'FLIM': "IndTextureSRT",
            b'FLAC': "AlphaTest",
            b'FLFS': "FontShadow",
            b'FLCT': "PerCharacterTransform",
            b'FLCC': "PerCharacterTransformCurve",
        }

        self.value: str = ""

    def set(self, magic: bytes):
        self.value = self.types[magic]

    def get(self):
        return self.value


class Lan:
    def __init__(self):
        self.animContent: list[AnimContent] = []

        self.animType = AnimationType()
        self.startFrame: int = 0
        self.endFrame: int = 0
        self.convertStartFrame: int = 0
        self.convertEndFrame: int = 0

        self.refRes: list[str] = []

    def set(self, tags: list[Any], anim: list[FLAN], animContsNames: list[str], type_: bytes, minFrame: int, maxFrame: int):
        self.animType.set(type_)
        self.startFrame = minFrame
        self.endFrame = maxFrame
        self.convertStartFrame = minFrame
        self.convertEndFrame = maxFrame

        for animContName in animContsNames:
            targetsUsed = []
            for i, flan in enumerate(anim):
                if tags:
                    startFrame = tags[i].startFrame
                else:
                    startFrame = 0
                if self.animType.get() == 'TexturePattern':
                    for name in flan.info.fileNames:  # type: ignore
                        self.refRes.append(name)
                    self.refRes = list(dict.fromkeys(self.refRes))

                for animCont in flan.info.animConts:  # type: ignore
                    if animContName == animCont.name:  # type: ignore
                        for animInfo in animCont.animInfos:  # type: ignore
                            if type_ == animInfo.magic:  # type: ignore
                                for target in animInfo.animTargets:  # type: ignore
                                    _target = AnimTarget()
                                    _target.set(startFrame, target.curveType, target.keys, target.id, self.animType.get(), target.target, self)  # type: ignore

                                    for __target in targetsUsed:  # type: ignore
                                        if _target == __target:
                                            __target.addKeys(startFrame, target.curveType, target.keys)  # type: ignore
                                            break

                                    else:
                                        targetsUsed.append(_target)  # type: ignore

            targetsUsed.sort(key=lambda target: target.idx)  # type: ignore

            self.animContent.append(AnimContent())
            self.animContent[-1].set(animContName, targetsUsed, self.animType.get())

    def getAsDict(self):
        _dict: dict[str, Any] = {
            "@animType": self.animType.get(),
            "@startFrame": str(self.startFrame),
            "@endFrame": str(self.endFrame),
            "@convertStartFrame": str(self.convertStartFrame),
            "@convertEndFrame": str(self.convertEndFrame),
        }

        if self.animContent:
            _dict["animContent"] = [animContent.getAsDict() for animContent in self.animContent]

        return _dict


def main(files: list[str], path: str, output: str):
    minFrame, maxFrame = 0x7fffffff, -1

    hasAnimTag = True
    addAnimTag = len(files) > 1

    anim: list[FLAN] = []
    animShares: list[AnimShare] = []
    animTags: list[AnimTag] = []
    for file in files:
        with open(os.path.join(path, file), "rb") as inf:
            inb = inf.read()

        flan = FLAN(inb)

        if not flan.info:
            raise RuntimeError("No Animation block found in %s.bflan" % file)

        if not flan.tag:
            hasAnimTag = False

        anim.append(flan)

    if addAnimTag:
        if not hasAnimTag:
            raise RuntimeError("%s.bflan must have an Animation tag!" % file)  # type: ignore

        else:
            anim.sort(key=lambda flan: flan.tag.tagOrder)  # type: ignore

    for flan in anim:
        if hasAnimTag:
            print(flan.tag.tagOrder, flan.tag.name)  # type: ignore

        if flan.share:
            print("Animation share is not supported yet.")
            animShare = AnimShare()
            animShare.set(flan.share.animShareInfos)  # type: ignore

        else:
            animShare = None

        loop = bool(flan.info.loop & 1)  # type: ignore

        if hasAnimTag:
            tag = flan.tag
            animTag = AnimTag()
            animTag.set(tag, loop)  # type: ignore
            if tag.startFrame < minFrame:  # type: ignore
                minFrame = tag.startFrame  # type: ignore

            if tag.endFrame > maxFrame:  # type: ignore
                maxFrame = tag.endFrame  # type: ignore

            if addAnimTag:
                animTags.append(animTag)

    textures: list[str] = []
    formats: list[str] = []
    usedTypes: list[str] = []

    for flan in anim:
        textures.extend(flan.info.fileNames)  # type: ignore
        formats.extend(flan.info.formats)     # type: ignore

        for animCont in flan.info.animConts:  # type: ignore
            for animInfo in animCont.animInfos:  # type: ignore
                if animInfo.magic not in usedTypes:  # type: ignore
                    usedTypes.append(animInfo.magic)  # type: ignore

    lans: list[Lan] = []
    for type_ in usedTypes:  # type: ignore
        animContsNames = []
        for flan in anim:
            for animCont in flan.info.animConts:  # type: ignore
                for animInfo in animCont.animInfos:  # type: ignore
                    if type_ == animInfo.magic:  # type: ignore
                        if animCont.name not in animContsNames:  # type: ignore
                            animContsNames.append(animCont.name)  # type: ignore

                        break

        lan = Lan()
        lan.set(animTags, anim, animContsNames, type_, minFrame, maxFrame)  # type: ignore
        lans.append(lan)

    file = {}
    file["nw4f_layout"] = OrderedDict()
    file["nw4f_layout"]["@version"] = "1.5.2"
    file["nw4f_layout"]["@xmlns:xsd"] = "http://www.w3.org/2001/XMLSchema"
    file["nw4f_layout"]["@xmlns:xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
    file["nw4f_layout"]["@xmlns"] = "http://www.nintendo.co.jp/NW4F/LayoutEditor"
    file["nw4f_layout"]["head"] = Head().getAsDict()
    file["nw4f_layout"]["body"] = OrderedDict()
    file["nw4f_layout"]["body"]["animShare"] = [animShare.getAsDict() for animShare in animShares]
    file["nw4f_layout"]["body"]["animTag"] = [animTag.getAsDict() for animTag in animTags]
    file["nw4f_layout"]["body"]["lan"] = [lan.getAsDict() for lan in lans]

    xml = dictToXml(file)
    with open(output, "w", encoding="utf-8") as out:
        out.write(xml)

    return textures, formats
