import io
import typing
import enum_lib
import zlib

from NeonOcean.S4.Main.Tools import Exceptions

class CompressionType(enum_lib.IntEnum):
	Uncompressed = 0x0  # type: CompressionType
	# noinspection SpellCheckingInspection
	ZLIB = 0x5A42  # type: CompressionType
	InternalCompression = 0xFFFF  # type: CompressionType

class PackageEntry:
	def __init__(
			self,
			packageFilePath: str,
			typeID: int,
			groupID: int,
			instanceID: int,
			filePosition: int,
			fileSize: int,
			fileSizeDecompressed: int,
			compressionType: CompressionType):

		self.PackageFilePath = packageFilePath  # type: str

		self.TypeID = typeID  # type: int
		self.GroupID = groupID  # type: int
		self.InstanceID = instanceID  # type: int

		self.FilePosition = filePosition  # type: int
		self.FileSize = fileSize  # type: int
		self.FileSizeDecompressed = fileSizeDecompressed  # type: int

		self.CompressionType = compressionType  # type: CompressionType

	def Read (self) -> bytes:
		"""
		Read, decompress and return this entry's bytes.
		"""

		with open(self.PackageFilePath, mode = "rb") as packageFile:
			packageFile.seek(self.FilePosition)

			compressedFileBytes = packageFile.read(self.FileSize)

		if self.CompressionType == CompressionType.Uncompressed:
			fileBytes = compressedFileBytes  # type: bytes
		elif self.CompressionType == CompressionType.ZLIB:
			fileBytes = zlib.decompress(compressedFileBytes)  # type: bytes
		else:
			fileBytes = _DecompressInternalCompressionPackageFile(compressedFileBytes)  # type: bytes

		if len(fileBytes) != self.FileSizeDecompressed:
			raise Exception("Uncompressed package file size did not match the file's indicated uncompressed size.")

		return fileBytes

	def IdentifiersToString (self) -> str:
		return "%s:%s:%s" % (self.TypeID, self.GroupID, self.InstanceID)  # In an order which can be input into the resource modules "ResourceKeyWrapper".

def GetPackageLocalizationStrings (packageFilePath: str) -> typing.List[PackageEntry]:
	"""
	Get all STBL file entries in the package file at this path.
	:param packageFilePath: The file path of the target package, an exception will be raised if the file does not exist or is not a valid file type.
	:type packageFilePath: str
	"""

	if not isinstance(packageFilePath, str):
		raise Exceptions.IncorrectTypeException(packageFilePath, "packageFilePath", (str, ))

	byteOrder = "little"  # type: str

	with open(packageFilePath, mode = "rb") as packageFile:
		fileIdentifier = packageFile.read(4)  # type: bytes

		# noinspection SpellCheckingInspection
		if fileIdentifier != b"DBPF":
			# noinspection SpellCheckingInspection
			raise Exception("Invalid package file identifier, expected 'DBPF'.")

		majorVersion = int.from_bytes(packageFile.read(4), byteOrder)  # type: int

		if majorVersion != 2:
			raise Exception("Invalid package file major version number. Expected '2', got '%s'." % majorVersion)

		minorVersion = int.from_bytes(packageFile.read(4), byteOrder)  # type: int

		if minorVersion != 1:
			raise Exception("Invalid package file minor version number. Expected '1', got '%s'." % minorVersion)

		packageFile.seek(36)  # Skip to the entry count.

		indexRecordEntryCount = int.from_bytes(packageFile.read(4), byteOrder)  # type: int
		indexRecordPositionLow = int.from_bytes(packageFile.read(4), byteOrder)  # type: int

		packageFile.seek(64)  # Skip to the index record position bytes

		indexRecordPosition = int.from_bytes(packageFile.read(8), byteOrder)  # type: int

		validEntries = list()  # type: typing.List[PackageEntry]

		indexRecordEntrySize = 32  # type: int

		def handleIndexRecordEntry (indexRecordEntryPosition: int) -> None:
			packageFile.seek(indexRecordEntryPosition)

			typeID = int.from_bytes(packageFile.read(4), byteOrder)  # type: int

			if typeID != 570775514:
				packageFile.seek(28, io.SEEK_CUR)  # Skip the rest of the information
				return

			groupID = int.from_bytes(packageFile.read(4), byteOrder)  # type: int
			instanceID = int.from_bytes(packageFile.read(4), byteOrder) << 32 | int.from_bytes(packageFile.read(4), byteOrder)  # type: int

			filePosition = int.from_bytes(packageFile.read(4), byteOrder)  # type: int
			fileSize = int.from_bytes(packageFile.read(4), byteOrder) & 0x7FFFFFFF  # type: int
			fileSizeDecompressed = int.from_bytes(packageFile.read(4), byteOrder) & 0x7FFFFFFF  # type: int

			try:
				compressionType = CompressionType(int.from_bytes(packageFile.read(2), byteOrder))  # type: CompressionType
			except ValueError:
				return

			if fileSize == 0:
				return

			if compressionType == 0xFFE0:  # Deleted record
				return

			validEntries.append(PackageEntry(packageFilePath, typeID, groupID, instanceID, filePosition, fileSize, fileSizeDecompressed, compressionType))

		indexRecordStartPosition = (indexRecordPosition if indexRecordPosition != 0 else indexRecordPositionLow) + 4  # type: int
		packageFile.seek(indexRecordStartPosition)  # Skip to the index record position and skip and four bytes.

		for indexRecordEntryIndex in range(indexRecordEntryCount):  # type: int
			handleIndexRecordEntry(indexRecordStartPosition + indexRecordEntrySize * indexRecordEntryIndex)

		return validEntries

def _DecompressInternalCompressionPackageFile (compressedFileBytes: bytes) -> bytes:
	"""
	https://modthesims.info/wiki.php?title=Sims_3:DBPF/Compression
	"""

	compressionType = compressedFileBytes[0]  # type: int

	if compressionType == 0x80:
		fileSizeDecompressed = int.from_bytes(compressedFileBytes[2: 6], "big")  # type: int
		compressedFileBytes = compressedFileBytes[6:]  # Dump the compression information from the file bytes
	else:
		fileSizeDecompressed = int.from_bytes(compressedFileBytes[2: 5], "big")  # type: int
		compressedFileBytes = compressedFileBytes[5:]  # Dump the compression information from the file bytes

	fileBytes = bytearray(fileSizeDecompressed)  # type: bytearray
	writeHeadPosition = 0  # type: int

	currentStateHandler = None  # type: typing.Optional[typing.Callable[[int], None]]

	controlType = None  # type: typing.Optional[int]
	controlByte0 = None  # type: typing.Optional[int]
	controlByte1 = None  # type: typing.Optional[int]
	controlByte2 = None  # type: typing.Optional[int]
	controlByte3 = None  # type: typing.Optional[int]

	uncompressedBytes = 0  # type: int
	compressedBytes = 0  # type: int
	compressedByteOffset = None  # type: typing.Optional[int]

	def resetState () -> None:
		nonlocal currentStateHandler, controlType, controlByte0, controlByte1, controlByte2, controlByte3, uncompressedBytes, compressedBytes, compressedByteOffset

		currentStateHandler = state0
		controlType = None
		controlByte0 = None
		controlByte1 = None
		controlByte2 = None
		controlByte3 = None

		uncompressedBytes = 0
		compressedBytes = 0
		compressedByteOffset = None

	def calculateControlType0Actions () -> None:
		nonlocal uncompressedBytes, compressedBytes, compressedByteOffset

		uncompressedBytes = controlByte0 & 0x03
		compressedBytes = ((controlByte0 & 0x1C) >> 2) + 3
		compressedByteOffset = ((controlByte0 & 0x60) << 3) + controlByte1 + 1

	def calculateControlType1Actions () -> None:
		nonlocal uncompressedBytes, compressedBytes, compressedByteOffset

		uncompressedBytes = ((controlByte1 & 0xC0) >> 6) & 0x03
		compressedBytes = (controlByte0 & 0x3F) + 4
		compressedByteOffset = ((controlByte1 & 0x3F) << 8) + controlByte2 + 1

	def calculateControlType2Actions () -> None:
		nonlocal uncompressedBytes, compressedBytes, compressedByteOffset

		uncompressedBytes = controlByte0 & 0x03
		compressedBytes = ((controlByte0 & 0x0C) << 6) + controlByte3 + 5
		compressedByteOffset = ((controlByte0 & 0x10) << 12) + (controlByte1 << 8) + controlByte2 + 1

	def calculateControlType3Actions () -> None:
		nonlocal uncompressedBytes, compressedBytes, compressedByteOffset

		uncompressedBytes = ((controlByte0 & 0x1F) << 2) + 4

	def calculateControlType4Actions () -> None:
		nonlocal uncompressedBytes, compressedBytes, compressedByteOffset

		uncompressedBytes = controlByte0 & 0x03

	def state0 (stateInputByte: int) -> None:
		"""
		Set control byte 0 and move to state 100 if the control type is 3 or 4, otherwise move to state 1.
		"""

		nonlocal currentStateHandler, controlType, controlByte0
		controlByte0 = stateInputByte

		if controlByte0 <= 0x7F:
			controlType = 0
		elif controlByte0 <= 0xBF:
			controlType = 1
		elif controlByte0 <= 0xDF:
			controlType = 2
		elif controlByte0 <= 0xFB:
			controlType = 3
		elif controlByte0 <= 0xFF:
			controlType = 4
		else:
			assert controlType is not None

		if controlType == 3 or controlType == 4:
			currentStateHandler = state100
		else:
			currentStateHandler = state1

	def state1 (stateInputByte: int) -> None:
		"""
		Set control byte 1 and move to state 100 if the control type is 0, otherwise move to state 2.
		"""

		nonlocal currentStateHandler, controlByte1
		controlByte1 = stateInputByte

		if controlType == 0:
			currentStateHandler = state100
		else:
			currentStateHandler = state2

	def state2 (stateInputByte: int) -> None:  #
		"""
		Set control byte 2 and move to state 100 if the control type is 1, otherwise move to state 3.
		"""

		nonlocal currentStateHandler, controlByte2
		controlByte2 = stateInputByte

		if controlType == 1:
			currentStateHandler = state100
		else:
			currentStateHandler = state3

	def state3 (stateInputByte: int) -> None:
		"""
		Set control byte 3 and move to state 100.
		"""

		nonlocal currentStateHandler, controlByte3
		controlByte3 = stateInputByte

		currentStateHandler = state100

	def state100 (stateInputByte: int) -> None:
		"""
		Calculate the appropriate actions. Trigger once, and move to state 101 if uncompressed bytes exist to copy, otherwise trigger once, and move to state 102.
		"""

		nonlocal currentStateHandler, writeHeadPosition, uncompressedBytes

		calculateActions[controlType]()

		if uncompressedBytes != 0:
			currentStateHandler = state101
		else:
			currentStateHandler = state102

		currentStateHandler(stateInputByte)

	def state101 (stateInputByte: int) -> None:
		"""
		Add the uncompressed input byte to the file bytes. Move to state 102 if this is the last uncompressed byte to add.
		"""

		nonlocal currentStateHandler, writeHeadPosition, uncompressedBytes

		fileBytes[writeHeadPosition] = stateInputByte
		writeHeadPosition += 1

		uncompressedBytes -= 1

		if uncompressedBytes == 0:
			currentStateHandler = state102

	def state102 (stateInputByte: int) -> None:
		"""
		Add all compressed bytes to the file bytes, and move to and trigger state 103.
		"""

		nonlocal currentStateHandler, writeHeadPosition

		if compressedByteOffset is not None:
			readHeadPosition = writeHeadPosition - compressedByteOffset  # type: int
		else:
			currentStateHandler = state103
			currentStateHandler(stateInputByte)
			return

		for addedCompressedBytes in range(compressedBytes):
			fileBytes[writeHeadPosition] = fileBytes[readHeadPosition]
			writeHeadPosition += 1
			readHeadPosition += 1

		currentStateHandler = state103
		currentStateHandler(stateInputByte)

	def state103 (stateInputByte: int) -> None:
		"""
		Reset the read state and trigger the default state.
		"""

		resetState()
		currentStateHandler(stateInputByte)

	currentStateHandler = state0  # type: typing.Callable[[int], None]

	calculateActions = {
		0: calculateControlType0Actions,
		1: calculateControlType1Actions,
		2: calculateControlType2Actions,
		3: calculateControlType3Actions,
		4: calculateControlType4Actions
	}

	for compressedFileByte in compressedFileBytes:  # type: int
		currentStateHandler(compressedFileByte)

	return bytes(fileBytes)