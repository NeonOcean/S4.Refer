from __future__ import annotations

import typing
import io

from NeonOcean.S4.Main.Tools import Exceptions

def ParseSTBLFileBytes (stblBytes: typing.Union[bytes, bytearray]) -> typing.Dict[int, str]:
	if not isinstance(stblBytes, (bytes, bytearray)):
		raise Exceptions.IncorrectTypeException(stblBytes, "stblBytes", (bytes, bytearray))

	headPosition = 0  # type: int
	byteOrder = "little"  # type: str

	def read (readingBytes: int) -> typing.Union[bytes, bytearray]:
		nonlocal headPosition

		readBytes = stblBytes[headPosition : readingBytes + headPosition]  # type: typing.Union[bytes, bytearray]
		headPosition += readingBytes
		return readBytes

	def seek (positionOrOffset: int, fromPosition: int = io.SEEK_SET) -> int:
		nonlocal headPosition

		if fromPosition == io.SEEK_SET:
			headPosition = positionOrOffset
		elif fromPosition == io.SEEK_CUR:
			headPosition = headPosition + positionOrOffset
		elif fromPosition == io.SEEK_END:
			headPosition = len(stblBytes) + positionOrOffset
		else:
			headPosition = positionOrOffset

		return headPosition

	fileIdentifier = read(4)  # type: bytes

	if not fileIdentifier == b"STBL":
		raise ValueError("Invalid STBL file identifier, expected 'STBL'.")

	version = int.from_bytes(read(2), byteOrder)  # type: int

	if version != 5:
		raise ValueError("Invalid STBL file version, expected '5'.")

	seek(1, io.SEEK_CUR)  # Skip the 'compressed' byte, its not used.

	entryCount = int.from_bytes(read(8), byteOrder)  # type: int

	seek(6, io.SEEK_CUR)  # Skip the two 'reserved' bytes and the 'string length' bytes.

	def readEntryBytes () -> typing.Tuple[typing.Optional[int], typing.Optional[str]]:
		entryKey = int.from_bytes(read(4), byteOrder)  # type: int
		seek(1, io.SEEK_CUR)  # Skip the flags byte
		entryLength = int.from_bytes(read(2), byteOrder)  # type: int
		entryText = read(entryLength).decode("utf-8")  # type: str
		return entryKey, entryText

	parsedLocalizationStrings = dict()  # type: typing.Dict[int, str]

	for entryIndex in range(entryCount):  # type: int
		if headPosition >= len(stblBytes) - 1:
			raise Exception("Could not find %s entries that should exist, according to the stbl file's entry count." % (entryCount - entryIndex + 1))

		readEntryKey, readEntryText = readEntryBytes()  # type: typing.Optional[int], typing.Optional[str]

		if readEntryKey is None or readEntryText is None:
			continue

		readEntryText = readEntryText.replace("\\t", "\t")
		readEntryText = readEntryText.replace("\\r", "\r")
		readEntryText = readEntryText.replace("\\n", "\n")

		parsedLocalizationStrings[readEntryKey] = readEntryText

	return parsedLocalizationStrings