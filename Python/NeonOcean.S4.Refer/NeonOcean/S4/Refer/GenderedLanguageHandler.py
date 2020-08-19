from __future__ import annotations

import json
import os
import time
import typing

from NeonOcean.S4.Main import Debug, Director
from NeonOcean.S4.Main.Tools import Exceptions, Patcher, Python, Timer, Version
from NeonOcean.S4.Refer import GenderedLanguage, LanguageHandlers, This
from NeonOcean.S4.Refer.Tools import Package, STBL
from protocolbuffers import Localization_pb2
from server import client
from sims4 import common as Sims4Common, localization, resources

class _LanguageCacheInfo:
	_cachedHandlerLanguageSavingKey = "CachedHandlerLanguage"  # type: str
	_cachedHandlerVersionSavingKey = "CachedHandlerVersion"  # type: str
	_packageModifiedTimeSavingKey = "PackageModifiedTime"  # type: str

	def __init__ (self, cachedHandlerLanguage: typing.Optional[int], cachedHandlerVersion: typing.Optional[Version.Version], packageModifiedTime: typing.Optional[float]):
		if not isinstance(cachedHandlerLanguage, int) and cachedHandlerLanguage is not None:
			raise Exceptions.IncorrectTypeException(cachedHandlerLanguage, "cachedHandlerLanguage", (int, None))

		if not isinstance(cachedHandlerVersion, Version.Version) and cachedHandlerVersion is not None:
			raise Exceptions.IncorrectTypeException(cachedHandlerVersion, "cachedHandlerVersion", (Version.Version, None))

		if not isinstance(packageModifiedTime, (float, int)) and packageModifiedTime is not None:
			raise Exceptions.IncorrectTypeException(packageModifiedTime, "packageModifiedTime", (float, int, None))

		self.CachedHandlerLanguage = cachedHandlerLanguage  # type: typing.Optional[int]
		self.CachedHandlerVersion = cachedHandlerVersion  # type: typing.Optional[Version.Version]
		self.PackageModifiedTime = packageModifiedTime  # type: typing.Optional[float]

	@classmethod
	def FromDictionary (cls, sourceDictionary: dict) -> _LanguageCacheInfo:
		cachedHandlerLanguage = sourceDictionary.get(cls._cachedHandlerLanguageSavingKey, None)  # type: typing.Optional[int]
		cachedHandlerVersionString = sourceDictionary.get(cls._cachedHandlerVersionSavingKey, None)  # type: typing.Optional[str]

		if cachedHandlerVersionString is not None:
			cachedHandlerVersion = Version.Version(cachedHandlerVersionString)  # type: typing.Optional[Version.Version]
		else:
			cachedHandlerVersion = None  # type: typing.Optional[Version.Version]

		packageModifiedTime = sourceDictionary.get(cls._packageModifiedTimeSavingKey, None)  # type: typing.Optional[float]
		return cls(cachedHandlerLanguage, cachedHandlerVersion, packageModifiedTime)

	def ToDictionary (self) -> dict:
		return {
			self._cachedHandlerLanguageSavingKey: self.CachedHandlerLanguage,
			self._cachedHandlerVersionSavingKey: str(self.CachedHandlerVersion),
			self._packageModifiedTimeSavingKey: self.PackageModifiedTime
		}

class _Announcer(Director.Announcer):
	Host = This.Mod

	_onClientConnectTriggered = False  # type: bool

	@classmethod
	def OnClientConnect (cls, clientReference: client.Client) -> None:
		if not cls._onClientConnectTriggered:
			searchStartTime = time.time()  # type: float
			# noinspection PyProtectedMember
			_AddLocalizationStringsToDictionaries(GenderedLanguage._allLocalizationStrings, GenderedLanguage._genderedLocalizationStrings)
			searchTime = time.time() - searchStartTime  # type: float

			# noinspection PyProtectedMember
			Debug.Log("Found %s localization strings. Of those strings, we found %s with gendered terms we can handle. This operation took %s seconds to complete." % (len(GenderedLanguage._allLocalizationStrings), len(GenderedLanguage._genderedLocalizationStrings), searchTime), This.Mod.Namespace, Debug.LogLevels.Info, group = This.Mod.Namespace, owner = __name__)

			cls._onClientConnectTriggered = True

	@classmethod
	def ZoneLoad (cls, zoneReference) -> None:
		global _trueLocalizationStringValues
		_trueLocalizationStringValues = dict()

def _Setup () -> None:
	_DoPatches()

def _AddLocalizationStringsToDictionaries (allLocalizationStrings: typing.Dict[int, str], genderedLocalizationStrings: typing.Dict[int, str]) -> None:
	# TODO notify player of issues

	currentLanguageHandler = LanguageHandlers.GetCurrentLanguageHandler()  # type: typing.Optional[LanguageHandlers.LanguageHandlerBase]

	if currentLanguageHandler is None:
		return

	def filterAndFixText (handlingLocalizationStrings: typing.Dict[int, str]) -> typing.Dict[int, str]:
		filteredAndFixedLocalizationStrings = dict()  # type: typing.Dict[int, str]

		for handlingSTBLEntryKey, handlingSTBLEntryText in handlingLocalizationStrings.items():  # type: int, str
			handlingSTBLEntryTextIsGendered, handlingSTBLEntryTextMatches = GenderedLanguage.TextIsGendered(handlingSTBLEntryText)  # type: bool, typing.List[GenderedLanguage.CachedGenderTagPairMatch]

			if not handlingSTBLEntryTextIsGendered:
				continue

			fixedHandlingSTBLEntryText = currentLanguageHandler.FixGenderTagUsageInconsistency(handlingSTBLEntryText, handlingSTBLEntryTextMatches)
			filteredAndFixedLocalizationStrings[handlingSTBLEntryKey] = fixedHandlingSTBLEntryText

		return filteredAndFixedLocalizationStrings

	for targetPack in Sims4Common.get_available_packs():  # type: Sims4Common.Pack
		targetPackageFilePaths = currentLanguageHandler.GetPackLocalizationPackageFilePaths(targetPack)  # type: typing.List[str]

		for targetPackageFilePath in targetPackageFilePaths:  # type: str
			try:
				targetPackageModifiedTime = os.path.getmtime(targetPackageFilePath)  # type: float

				targetPackageEntries = Package.GetPackageLocalizationStrings(targetPackageFilePath)  # type: typing.List[Package.PackageEntry]

				for targetPackageEntry in targetPackageEntries:  # type: Package.PackageEntry
					if not currentLanguageHandler.IsHandlingLanguageSTBLFile(("%016x" % targetPackageEntry.InstanceID).upper()):
						continue

					targetLocalizationStrings = None  # type: typing.Optional[typing.Dict[int, str]]
					targetGenderedLocalizationStrings = None  # type: typing.Optional[typing.Dict[int, str]]

					minimumCacheHandlerVersion = currentLanguageHandler.GetMinimumCacheHandlerVersion()  # type: typing.Optional[Version.Version]

					try:
						targetPackageEntryCacheInfo = _GetGamePackLanguageCacheInfo(targetPack, targetPackageEntry)  # type: typing.Optional[_LanguageCacheInfo]
					except:
						Debug.Log("Failed to read language cache info file of the package at '%s' and the STBL entry '%s'." % (targetPackageFilePath, targetPackageEntry.IdentifiersToString()), This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)
					else:
						if targetPackageEntryCacheInfo is not None:
							if targetPackageEntryCacheInfo.PackageModifiedTime == targetPackageModifiedTime and \
									targetPackageEntryCacheInfo.CachedHandlerLanguage == currentLanguageHandler.HandlingLanguage and \
									targetPackageEntryCacheInfo.CachedHandlerVersion is not None and \
									(minimumCacheHandlerVersion is None or targetPackageEntryCacheInfo.CachedHandlerVersion >= minimumCacheHandlerVersion):

								try:
									targetLocalizationStrings = _GetGamePackLanguageCache(targetPack, targetPackageEntry)

									if targetLocalizationStrings is not None:
										allLocalizationStrings.update(targetLocalizationStrings)
								except:
									Debug.Log("Failed to read the language cache file of the package at '%s' and the STBL entry '%s'." % (targetPackageFilePath, targetPackageEntry.IdentifiersToString()), This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)

					try:
						targetPackageEntryGenderedCacheInfo = _GetGamePackGenderedLanguageCacheInfo(targetPack, targetPackageEntry)  # type: typing.Optional[_LanguageCacheInfo]
					except:
						Debug.Log("Failed to read the gendered language cache info file of the package at '%s' and the STBL entry '%s'." % (targetPackageFilePath, targetPackageEntry.IdentifiersToString()), This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)
					else:
						if targetPackageEntryGenderedCacheInfo is not None:

							if targetPackageEntryGenderedCacheInfo.PackageModifiedTime == targetPackageModifiedTime and \
									targetPackageEntryGenderedCacheInfo.CachedHandlerLanguage == currentLanguageHandler.HandlingLanguage and \
									targetPackageEntryGenderedCacheInfo.CachedHandlerVersion is not None and \
									(minimumCacheHandlerVersion is None or targetPackageEntryGenderedCacheInfo.CachedHandlerVersion >= minimumCacheHandlerVersion):

								try:
									targetGenderedLocalizationStrings = _GetGamePackGenderedLanguageCache(targetPack, targetPackageEntry)

									if targetGenderedLocalizationStrings is not None:
										genderedLocalizationStrings.update(targetGenderedLocalizationStrings)
								except:
									Debug.Log("Failed to read the gendered language cache file of the package at '%s' and the STBL entry '%s'." % (targetPackageFilePath, targetPackageEntry.IdentifiersToString()), This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)

					if targetLocalizationStrings is None:
						try:
							targetLocalizationStrings = STBL.ParseSTBLFileBytes(targetPackageEntry.Read())  # type: typing.Dict[int, str]
						except:
							Debug.Log("Failed to read the localization strings of the package at '%s' and the STBL entry '%s'." % (targetPackageFilePath, targetPackageEntry.IdentifiersToString()), This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)
						else:
							try:
								_WriteGamePackLanguageCache(
									targetPack,
									targetPackageEntry,
									targetLocalizationStrings,
									_LanguageCacheInfo(int(currentLanguageHandler.HandlingLanguage), This.Mod.Version, targetPackageModifiedTime))
							except:
								Debug.Log("Failed to write the language cache file for the package at '%s' and the STBL entry '%s'." % (targetPackageFilePath, targetPackageEntry.IdentifiersToString()), This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)
							else:
								Debug.Log("Read and cached the localization strings of the package at '%s' and the STBL entry '%s'." % (targetPackageFilePath, targetPackageEntry.IdentifiersToString()), This.Mod.Namespace, Debug.LogLevels.Info, group = This.Mod.Namespace, owner = __name__)

					if targetGenderedLocalizationStrings is None and targetLocalizationStrings is not None:
						try:
							targetGenderedLocalizationStrings = filterAndFixText(targetLocalizationStrings)  # type: typing.Dict[int, str]
						except:
							Debug.Log("Failed to filter and fix the gendered localization strings of the package at '%s' and the STBL entry '%s'." % (targetPackageFilePath, targetPackageEntry.IdentifiersToString()), This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)
						else:
							try:
								_WriteGamePackGenderedLanguageCache(
									targetPack,
									targetPackageEntry,
									targetGenderedLocalizationStrings,
									_LanguageCacheInfo(int(currentLanguageHandler.HandlingLanguage), This.Mod.Version, targetPackageModifiedTime))
							except:
								Debug.Log("Failed to write the gendered language cache file for the pack '%s' and the STBL entry '%s'." % (targetPack.name, targetPackageEntry.IdentifiersToString()), This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)
							else:
								Debug.Log("Filtered, fixed, and cached the gendered localization strings of the package at '%s' and the STBL entry '%s'." % (targetPackageFilePath, targetPackageEntry.IdentifiersToString()), This.Mod.Namespace, Debug.LogLevels.Info, group = This.Mod.Namespace, owner = __name__)

					allLocalizationStrings.update(targetLocalizationStrings)
					genderedLocalizationStrings.update(targetGenderedLocalizationStrings)
			except:
				Debug.Log("Failed to read the localization strings of a package file at '%s'." % targetPackageFilePath, This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)

	# noinspection PyTypeChecker
	modSTBLFileKeys = resources.get_all_resources_of_type(570775514)  # type: typing.Tuple[typing.Any, ...]

	for targetSTBLFileKey in modSTBLFileKeys:  # type: typing.Any
		if not currentLanguageHandler.IsHandlingLanguageSTBLFile(("%016x" % targetSTBLFileKey.instance).upper()):
			continue

		targetSTBLFileLoader = resources.ResourceLoader(targetSTBLFileKey, resource_type = 570775514)  # type: resources.ResourceLoader

		with targetSTBLFileLoader.load() as targetSTBLFileStream:
			targetLocalizationStrings = STBL.ParseSTBLFileBytes(targetSTBLFileStream.read())  # type: typing.Dict[int, str]
			targetGenderedLocalizationStrings = filterAndFixText(targetLocalizationStrings)  # type: typing.Dict[int, str]

			allLocalizationStrings.update(allLocalizationStrings)
			genderedLocalizationStrings.update(targetGenderedLocalizationStrings)

def _WriteGamePackLanguageCache (pack: Sims4Common.Pack, packageEntry: Package.PackageEntry, localizationStrings: typing.Dict[int, str], cacheInfo: _LanguageCacheInfo) -> None:
	cacheFilePath = _GetGamePackLanguageCacheFilePath(pack, packageEntry)  # type: str
	cacheInfoFilePath = _GetGamePackLanguageCacheInfoFilePath(pack, packageEntry)  # type: str
	cacheFilesDirectory = os.path.dirname(cacheFilePath)  # type: str

	if not os.path.exists(cacheFilesDirectory):
		os.makedirs(cacheFilesDirectory)

	with open(cacheInfoFilePath, "w+") as cacheInfoFile:
		cacheInfoFile.write(json.JSONEncoder(indent = "\t").encode(cacheInfo.ToDictionary()))

	with open(cacheFilePath, "w+") as cacheFile:
		cacheFile.write(json.JSONEncoder(indent = "\t").encode(localizationStrings))

def _GetGamePackLanguageCache (pack: Sims4Common.Pack, packageEntry: Package.PackageEntry) -> typing.Optional[typing.Dict[int, str]]:
	cacheFilePath = _GetGamePackLanguageCacheFilePath(pack, packageEntry)  # type: str
	cacheInfoFilePath = _GetGamePackLanguageCacheInfoFilePath(pack, packageEntry)  # type: str

	if not os.path.exists(cacheFilePath) or not os.path.exists(cacheInfoFilePath):
		return None

	with open(cacheFilePath, "r") as cacheFile:
		cacheDictionary = json.JSONDecoder().decode(cacheFile.read())

	cacheDictionary = { int(cachedLanguageKey): cachedLanguageText for cachedLanguageKey, cachedLanguageText in cacheDictionary.items() }

	return cacheDictionary

def _GetGamePackLanguageCacheInfo (pack: Sims4Common.Pack, packageEntry: Package.PackageEntry) -> typing.Optional[_LanguageCacheInfo]:
	cacheFilePath = _GetGamePackLanguageCacheFilePath(pack, packageEntry)  # type: str
	cacheInfoFilePath = _GetGamePackLanguageCacheInfoFilePath(pack, packageEntry)  # type: str

	if not os.path.exists(cacheFilePath) or not os.path.exists(cacheInfoFilePath):
		return None

	with open(cacheInfoFilePath, "r") as cacheInfoFile:
		cacheInfoDictionary = json.JSONDecoder().decode(cacheInfoFile.read())

	return _LanguageCacheInfo.FromDictionary(cacheInfoDictionary)

def _GetGamePackLanguageCacheFilePath (pack: Sims4Common.Pack, packageEntry: Package.PackageEntry) -> str:
	return os.path.join(_gameLanguageCacheFolderPath, pack.name, packageEntry.IdentifiersToString().replace(":", "-")) + ".json"

def _GetGamePackLanguageCacheInfoFilePath (pack: Sims4Common.Pack, packageEntry: Package.PackageEntry) -> str:
	return os.path.join(_gameLanguageCacheFolderPath, pack.name, packageEntry.IdentifiersToString().replace(":", "-")) + "-info.json"

def _WriteGamePackGenderedLanguageCache (pack: Sims4Common.Pack, packageEntry: Package.PackageEntry, genderedLocalizationStrings: typing.Dict[int, str], cacheInfo: _LanguageCacheInfo) -> None:
	cacheFilePath = _GetGamePackGenderedLanguageCacheFilePath(pack, packageEntry)  # type: str
	cacheInfoFilePath = _GetGamePackGenderedLanguageCacheInfoFilePath(pack, packageEntry)  # type: str
	cacheFilesDirectory = os.path.dirname(cacheFilePath)  # type: str

	if not os.path.exists(cacheFilesDirectory):
		os.makedirs(cacheFilesDirectory)

	with open(cacheInfoFilePath, "w+") as cacheInfoFile:
		cacheInfoFile.write(json.JSONEncoder(indent = "\t").encode(cacheInfo.ToDictionary()))

	with open(cacheFilePath, "w+") as cacheFile:
		cacheFile.write(json.JSONEncoder(indent = "\t").encode(genderedLocalizationStrings))

def _GetGamePackGenderedLanguageCache (pack: Sims4Common.Pack, packageEntry: Package.PackageEntry) -> typing.Optional[typing.Dict[int, str]]:
	cacheFilePath = _GetGamePackGenderedLanguageCacheFilePath(pack, packageEntry)  # type: str
	cacheInfoFilePath = _GetGamePackGenderedLanguageCacheInfoFilePath(pack, packageEntry)  # type: str

	if not os.path.exists(cacheFilePath) or not os.path.exists(cacheInfoFilePath):
		return None

	with open(cacheFilePath, "r") as cacheFile:
		cacheDictionary = json.JSONDecoder().decode(cacheFile.read())

	cacheDictionary = { int(cachedLanguageKey): cachedLanguageText for cachedLanguageKey, cachedLanguageText in cacheDictionary.items() }

	return cacheDictionary

def _GetGamePackGenderedLanguageCacheInfo (pack: Sims4Common.Pack, packageEntry: Package.PackageEntry) -> typing.Optional[_LanguageCacheInfo]:
	cacheFilePath = _GetGamePackGenderedLanguageCacheFilePath(pack, packageEntry)  # type: str
	cacheInfoFilePath = _GetGamePackGenderedLanguageCacheInfoFilePath(pack, packageEntry)  # type: str

	if not os.path.exists(cacheFilePath) or not os.path.exists(cacheInfoFilePath):
		return None

	with open(cacheInfoFilePath, "r") as cacheInfoFile:
		cacheInfoDictionary = json.JSONDecoder().decode(cacheInfoFile.read())

	return _LanguageCacheInfo.FromDictionary(cacheInfoDictionary)

def _GetGamePackGenderedLanguageCacheFilePath (pack: Sims4Common.Pack, packageEntry: Package.PackageEntry) -> str:
	return os.path.join(_gameGenderedLanguageCacheFolderPath, pack.name, packageEntry.IdentifiersToString().replace(":", "-")) + ".json"

def _GetGamePackGenderedLanguageCacheInfoFilePath (pack: Sims4Common.Pack, packageEntry: Package.PackageEntry) -> str:
	return os.path.join(_gameGenderedLanguageCacheFolderPath, pack.name, packageEntry.IdentifiersToString().replace(":", "-")) + "-info.json"

def _DoPatches () -> None:
	_DoLocalizationStringHashPatch()
	_DoLocalizationCreateTokensPatch()

def _DoLocalizationStringHashPatch () -> None:
	Patcher.Patch(Localization_pb2.LocalizedString, "__hash__", _LocalizationStringHashPatch, patchType = Patcher.PatchTypes.Custom)

def _DoLocalizationCreateTokensPatch () -> None:
	Patcher.Patch(localization, "create_tokens", _CreateTokensPatch, patchType = Patcher.PatchTypes.Custom)

def _LocalizationStringHashPatch (originalCallable: typing.Callable, self) -> int:
	try:
		return id(self)
	except:
		Debug.Log("Failed to handle the game's '__hash__' method in a 'LocalizationString' object.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__, lockIdentifier = __name__ + ":" + str(Python.GetLineNumber()), lockThreshold = 2)
		return originalCallable(self)

# noinspection PyUnusedLocal
def _CreateTokensPatch (originalCallable: typing.Callable, tokens_msg, *tokens) -> None:
	try:
		# noinspection PyProtectedMember
		localizationString = tokens_msg._message

		if localizationString.hash == 0:
			# TODO log tokens applied before hash?
			return

		trueStringValues = _trueLocalizationStringValues.get(localizationString, None)  # type: typing.Optional[typing.Tuple[int, tuple]]

		if trueStringValues is not None:
			trueStringHash = trueStringValues[0]  # type: int
			trueStringTokens = trueStringValues[1] + tokens  # type: tuple
			hasTrueValues = True  # type: bool
		else:
			trueStringHash = localizationString.hash  # type: int
			trueStringTokens = tokens  # type: tuple
			hasTrueValues = False  # type: bool

		localizationStringText = GenderedLanguage.GetGenderedLocalizationStringText(trueStringHash)  # type: typing.Optional[str]

		def createTrueValueCleaner (deletingLocalizationString: Localization_pb2.LocalizedString, cleanerTimer: Timer.Timer) -> typing.Callable:
			def trueValueCleaner () -> None:
				_trueLocalizationStringValues.pop(deletingLocalizationString, None)

				try:
					_trueLocalizationStringValueDeletionTimers.remove(cleanerTimer)
				except ValueError:
					pass

			return trueValueCleaner

		if localizationStringText is not None:
			correctedSTBLText = GenderedLanguage.CorrectGenderedSTBLText(trueStringHash, localizationStringText, trueStringTokens)

			if correctedSTBLText is not None:
				localizationString.hash = 2462885516  # The 'raw text' string. "{0.String}"

				while len(tokens_msg) != 0:
					tokens_msg.remove(tokens_msg[0])

				rawTextToken = Localization_pb2.LocalizedStringToken()  # type: Localization_pb2.LocalizedStringToken
				# noinspection PyUnresolvedReferences
				rawTextToken.type = Localization_pb2.LocalizedStringToken.RAW_TEXT
				rawTextToken.raw_text = correctedSTBLText

				tokens_msg.append(rawTextToken)

				_trueLocalizationStringValues[localizationString] = trueStringHash, trueStringTokens

				if not hasTrueValues:
					trueValueDeletionTimer = Timer.Timer(_trueLocalizationStringValueDeletionInterval, lambda *args, **kwargs: None)
					trueValueDeletionTimer.Callback = createTrueValueCleaner(localizationString, trueValueDeletionTimer)
					trueValueDeletionTimer.start()
					_trueLocalizationStringValueDeletionTimers.append(trueValueDeletionTimer)

				return
			else:
				_trueLocalizationStringValues[localizationString] = trueStringHash, trueStringTokens

				if not hasTrueValues:
					trueValueDeletionTimer = Timer.Timer(_trueLocalizationStringValueDeletionInterval, lambda *args, **kwargs: None)
					trueValueDeletionTimer.Callback = createTrueValueCleaner(localizationString, trueValueDeletionTimer)
					trueValueDeletionTimer.start()
					_trueLocalizationStringValueDeletionTimers.append(trueValueDeletionTimer)
	except:
		Debug.Log("Failed to handle the game's 'create tokens' function.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__, lockIdentifier = __name__ + ":" + str(Python.GetLineNumber()), lockThreshold = 2)

	return originalCallable(tokens_msg, *tokens)

_languageCacheFolderPath = os.path.join(This.Mod.PersistentPath, "Language Cache")  # type: str
_gameLanguageCacheFolderPath = os.path.join(_languageCacheFolderPath, "Game")  # type: str

_genderedLanguageCacheFolderPath = os.path.join(This.Mod.PersistentPath, "Gendered Language Cache")  # type: str
_gameGenderedLanguageCacheFolderPath = os.path.join(_genderedLanguageCacheFolderPath, "Game")  # type: str

_trueLocalizationStringValues = dict()  # type: typing.Dict[Localization_pb2.LocalizedString, typing.Tuple[int, tuple]]
_trueLocalizationStringValueDeletionTimers = list()  # type: typing.List[Timer.Timer]
_trueLocalizationStringValueDeletionInterval = 60  # type: int

_Setup()
