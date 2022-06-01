import struct
from common import readString, roundUp, Section

class FLAN:
    class AnimationTagBlock(Section):
        class AnimationGroupRef:
            def __init__(self, file, pos, fmt):
                (nameBytes,
                 self.flag) = struct.unpack_from(fmt, file, pos)

                self.name = readString(nameBytes)
                self.fmt = fmt

            def save(self):
                return struct.pack(
                    self.fmt,
                    self.name.encode('utf-8'),
                    self.flag,
                )

        def __init__(self, file, pos, major):
            initPos = pos
            super().__init__(file, pos); pos += 8

            (self.tagOrder,
             self.groupNum,
             self.nameOffset,
             self.groupsOffset,
             self.startFrame,
             self.endFrame,
             self.flag) = struct.unpack_from('>2H2I2hB', file, pos)

            # flag & 1 -> ANIMTAGFLAG_DESCENDINGBIND

            pos = initPos + self.nameOffset
            self.name = readString(file, pos)

            pos = initPos + self.groupsOffset
            self.groups = []

            if major < 5:
                fmt = '>24sB3x'
                size = 28

            else:
                fmt = '>33sB2x'
                size = 36

            for _ in range(self.groupNum):
                self.groups.append(self.AnimationGroupRef(file, pos, fmt))
                pos += size

        def save(self):
            buff1 = b''.join([self.name.encode('utf-8'), b'\0'])

            groupsOffset = 28 + len(buff1)
            alignLen = roundUp(groupsOffset, 4) - groupsOffset

            groupsOffset += alignLen
            buff1 += b'\0' * alignLen

            buff2 = struct.pack(
                '>2H2I2hB3x',
                self.tagOrder,
                len(self.groups),
                28,
                groupsOffset,
                self.startFrame,
                self.endFrame,
                self.flag,
            )

            buff3 = b''.join([group.save() for group in self.groups])
            self.data = b''.join([buff2, buff1, buff3])

            return super().save()

    class AnimationShareBlock(Section):
        class AnimationShareInfo:
            def __init__(self, file, pos):
                (srcPaneNameBytes,
                 targetGroupNameBytes) = struct.unpack_from('>25s25s', file, pos)

                self.srcPaneName = readString(srcPaneNameBytes)
                self.targetGroupName = readString(targetGroupNameBytes)

                #print(self.srcPaneName)

            def save(self):
                return struct.pack(
                    '>25s25s2x',
                    self.srcPaneName.encode('utf-8'),
                    self.targetGroupName.encode('utf-8'),
                )

        def __init__(self, file, pos):
            super().__init__(file, pos); pos += 8

            (self.animShareInfoOffset,
             self.shareNum) = struct.unpack_from('>IH', file, pos)

            pos += self.animShareInfoOffset - 8
            self.animShareInfos = []

            for _ in range(self.shareNum):
                self.animShareInfos.append(self.AnimationShareInfo(file, pos))
                pos += 52

        def save(self):
            buff1 = struct.pack(
                '>IH2x',
                16,
                len(self.animShareInfos),
            )

            buff2 = b''.join([animShareInfo.save() for animShareInfo in self.animShareInfos])
            self.data = b''.join([buff1, buff2])

            return super().save()

    class AnimationBlock(Section):
        class AnimationContent:
            class AnimationInfo:
                class AnimationTarget:
                    class HermiteKey:
                        def __init__(self, file, pos):
                            (self.frame,
                             self.value,
                             self.slope) = struct.unpack_from('>3f', file, pos)

                        def save(self):
                            return struct.pack(
                                '>3f',
                                self.frame,
                                self.value,
                                self.slope,
                            )

                    class StepKey:
                        def __init__(self, file, pos):
                            (self.frame,
                             self.value) = struct.unpack_from('>fH2x', file, pos)

                        def save(self):
                            return struct.pack(
                                '>fH2x',
                                self.frame,
                                self.value,
                            )

                    def __init__(self, file, pos):
                        initPos = pos
                        _curveTypes = ["Constant", "Step", "Hermite"]

                        (self.id,
                         self.target,
                         self.curveType,
                         self.keyNum,
                         self.keysOffset) = struct.unpack_from('>3BxH2xI', file, pos); pos += 12

                        assert self.keysOffset == 12

                        self.keys = []
                        if self.curveType:
                            size = 8 if self.curveType == 1 else 12
                            key = self.StepKey if self.curveType == 1 else self.HermiteKey
                            pos = initPos + self.keysOffset

                            for _ in range(self.keyNum):
                                self.keys.append(key(file, pos)); pos += size

                    def save(self):
                        buff1 = struct.pack(
                            '>3BxH2xI',
                            self.id,
                            self.target,
                            self.curveType,
                            len(self.keys),
                            12,
                        )

                        buff2 = bytearray()
                        for key in self.keys:
                            buff2 += key.save()

                        return b''.join([buff1, buff2])

                def __init__(self, file, pos):
                    initPos = pos

                    (self.magic,
                     self.num) = struct.unpack_from('>4sB', file, pos); pos += 8

                    self.animTargets = []
                    animTargetOffsets = struct.unpack_from('>%dI' % self.num, file, pos)

                    for pAnimTarget in animTargetOffsets:
                        self.animTargets.append(self.AnimationTarget(file, initPos + pAnimTarget))

                def save(self):
                    num = len(self.animTargets)

                    buff1 = struct.pack(
                        '>4sB3x',
                        self.magic,
                        num,
                    )

                    buff2 = bytearray()

                    animTargetOffsets = []
                    for animTarget in self.animTargets:
                        animTargetOffsets.append(8 + 4*num + len(buff2))
                        buff2 += animTarget.save()

                    buff3 = struct.pack('>%dI' % num, *animTargetOffsets)

                    return b''.join([buff1, buff3, buff2])

            def __init__(self, file, pos):
                initPos = pos

                _types = ["Pane", "Material"]

                (nameBytes,
                 self.num,
                 self.type) = struct.unpack_from('>28s2B', file, pos); pos += 32

                self.name = readString(nameBytes)
                #print(self.name)

                animInfoOffsets = struct.unpack_from('>%dI' % self.num, file, pos)
                self.animInfos = []

                for pAnimInfo in animInfoOffsets:
                    self.animInfos.append(self.AnimationInfo(file, initPos + pAnimInfo))

            def save(self):
                num = len(self.animInfos)

                buff1 = struct.pack(
                    '>28s2B2x',
                    self.name.encode('utf-8'),
                    num,
                    self.type,
                )

                buff2 = bytearray()

                animInfoOffsets = []
                for animInfo in self.animInfos:
                    animInfoOffsets.append(32 + 4*num + len(buff2))
                    buff2 += animInfo.save()

                buff3 = struct.pack('>%dI' % num, *animInfoOffsets)

                return b''.join([buff1, buff3, buff2])

        def __init__(self, file, pos):
            initPos = pos
            super().__init__(file, pos); pos += 8

            (self.frameSize,
             self.loop,
             self.fileNum,
             self.animContNum,
             animContOffsetsOffset) = struct.unpack_from('>HBx2HI', file, pos); pos += 12

            self.fileNames = []
            self.formats = []

            for i in range(self.fileNum):
                pFileName, = struct.unpack_from('>I', file, pos + 4*i)
                fileName = readString(file, pos + pFileName)
                format = ""

                assert fileName[-6:] == ".bflim"
                fileName = fileName[:-6]

                if len(fileName) > 2:
                    if fileName[-1] in 'abcdefghijklmnopqrstu' and fileName[-2] in '^+':
                        format = fileName[-2:]
                        fileName = fileName[:-2]

                self.fileNames.append(fileName)
                self.formats.append(format)

            pos = initPos + animContOffsetsOffset
            animContOffsets = struct.unpack_from('>%dI' % self.animContNum, file, pos)
            self.animConts = []

            for pAnimCont in animContOffsets:
                self.animConts.append(self.AnimationContent(file, initPos + pAnimCont))

        def save(self):
            fileNum = len(self.fileNames)
            animContNum = len(self.animConts)

            buff1 = bytearray()

            fileNameOffsets = []
            for fileName, format in zip(self.fileNames, self.formats):
                fileNameOffsets.append(4*fileNum + len(buff1))

                cFileName = ''.join([fileName, format, ".bflim"])
                buff1 += cFileName.encode('utf-8')
                buff1.append(0)

            buff2 = struct.pack('>%dI' % fileNum, *fileNameOffsets)

            animContOffsetsOffset = 20 + 4*fileNum + len(buff1)
            alignLen = roundUp(animContOffsetsOffset, 4) - animContOffsetsOffset

            animContOffsetsOffset += alignLen
            buff1 += b'\0' * alignLen

            buff3 = struct.pack(
                '>HBx2HI',
                self.frameSize,
                self.loop,
                fileNum,
                animContNum,
                animContOffsetsOffset,
            )

            buff4 = bytearray()

            animContOffsets = []
            for animCont in self.animConts:
                animContOffsets.append(animContOffsetsOffset + 4*animContNum + len(buff4))
                buff4 += animCont.save()

            buff5 = struct.pack('>%dI' % animContNum, *animContOffsets)
            self.data = b''.join([buff3, buff2, buff1, buff5, buff4])

            return super().save()

    def __init__(self, file):
        if file[4:6] != b'\xFE\xFF':
            raise NotImplementedError("Only big endian layouts are supported")  # TODO little endian

        (self.magic,
         self.headSize,
         self.version,
         self.fileSize,
         self.numSections) = struct.unpack_from('>4s2xH2IH', file)

        assert self.magic == b'FLAN'
        major = self.version >> 24  # TODO little endian
        if major not in [2, 3, 5]:
            print("Untested BFLAN version: %s\n" % hex(self.version))

        self.tag = None
        self.share = None
        self.info = None

        pos = 20
        for _ in range(self.numSections):
            if file[pos:pos + 4] == b'pat1':
                self.tag = self.AnimationTagBlock(file, pos, major)
                pos += self.tag.blockHeader.size

            elif file[pos:pos + 4] == b'pah1':
                self.share = self.AnimationShareBlock(file, pos)
                pos += self.share.blockHeader.size

            elif file[pos:pos + 4] == b'pai1':
                self.info = self.AnimationBlock(file, pos)
                pos += self.info.blockHeader.size

    def save(self):
        buff1 = bytearray()

        numSections = 0
        if self.tag:
            buff1 += self.tag.save(); numSections += 1

        if self.share:
            buff1 += self.share.save(); numSections += 1

        if self.info:
            buff1 += self.info.save(); numSections += 1

        buff2 = struct.pack(
            '>4s2H2IH2x',
            b'FLAN',
            0xFEFF,
            20,
            self.version,
            20 + len(buff1),
            numSections,
        )

        return b''.join([buff2, buff1])


def toVersion(file, output, version):
    major = version >> 24  # TODO little endian
    fmt = '>24sB3x' if major < 5 else '>33sB2x'

    flan = FLAN(file)
    flan.version = version

    if flan.tag:
        for group in flan.tag.groups:
            group.fmt = fmt

    with open(output, "wb") as out:
        out.write(flan.save())


def main():
    file = input("Input (.bflan):  ")
    output = input("Output (.bflan):  ")
    version = int(input("Convert to version (e.g. 0x02020000):  "), 0)

    with open(file, "rb") as inf:
        inb = inf.read()

    toVersion(inb, output, version)


if __name__ == "__main__":
    main()
