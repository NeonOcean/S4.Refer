from __future__ import annotations

import numbers
import os
import typing

import game_services
import paths
from NeonOcean.S4.Main import Debug, Language
from NeonOcean.S4.Main.Tools import Exceptions, Version
from NeonOcean.S4.Main.UI import Dialogs as UIDialogs
from NeonOcean.S4.Refer import GenderedLanguage, LanguageHandlers, This
from sims4 import common as Sims4Common
from ui import ui_dialog

class EnglishLanguageHandler(LanguageHandlers.LanguageHandlerBase):
	IsLanguageHandler = True  # type: bool

	HandlingLanguage = LanguageHandlers.Language.English  # type: LanguageHandlers.Language

	GameIdentifier = "en-us"  # type: str

	TheyThemSetIdentifier = "4CAA6EA8-3D59-4F6B-8842-ABB7F5A5AC27"  # type: str
	TheyThemSetTitle = "They / Them"  # type: str

	ZeZirSetIdentifier = "A5149C53-6B7E-4E26-AA6E-A38DD8AC8743"  # type: str
	ZeZirTitle = "Ze / Zir"

	ZeHirSetIdentifier = "FB11090A-EC13-4437-832C-B0E0C78B89F9"  # type: str
	ZeHirTitle = "Ze / Hir"

	XeXemSetIdentifier = "055ECB20-EFD0-477A-91EC-927C947F7E60"  # type: str
	XeXemTitle = "Xe / Xem"

	EyEmSetIdentifier = "34B839A1-0ADC-42A8-A2E7-6161D6804945"  # type: str
	EyEmTitle = "Ey / Em"

	ItSetIdentifier = "2C7EC16C-D1BB-496A-987A-D3D95981FB48"  # type: str
	ItTitle = "It"

	STBLInstanceIDPrefix = "00"  # type: str

	GameLocalizationPackageFileName = "Strings_ENG_US.package"  # type: str

	AskToDoTheyAreFixDialogTitle = Language.String(This.Mod.Namespace + ".Language_Handlers.English.Ask_To_Do_They_Are_Fix_Dialog.Title", fallbackText = "Ask_To_Do_They_Are_Fix_Dialog.Title")
	AskToDoTheyAreFixDialogText = Language.String(This.Mod.Namespace + ".Language_Handlers.English.Ask_To_Do_They_Are_Fix_Dialog.Text", fallbackText = "Ask_To_Do_They_Are_Fix_Dialog.Text")
	AskToDoTheyAreFixDialogYesButton = Language.String(This.Mod.Namespace + ".Language_Handlers.English.Ask_To_Do_They_Are_Fix_Dialog.Yes_Button", fallbackText = "Ask_To_Do_They_Are_Fix_Dialog.Yes_Button")
	AskToDoTheyAreFixDialogNoButton = Language.String(This.Mod.Namespace + ".Language_Handlers.English.Ask_To_Do_They_Are_Fix_Dialog.No_Button", fallbackText = "Ask_To_Do_They_Are_Fix_Dialog.No_Button")
	
	@classmethod
	def GetHandlerVersion (cls) -> Version.Version:
		return This.Mod.Version

	@classmethod
	def GetMinimumCacheHandlerVersion (cls) -> typing.Optional[Version.Version]:
		return None

	@classmethod
	def GetGenderTagTextIdentifierPart (cls, tagText: str) -> str:
		if not isinstance(tagText, str):
			raise Exceptions.IncorrectTypeException(tagText, "tagText", (str,))

		standardizeTagText = tagText.lower().strip(" ")  # type: str

		return {
			"she's": "she’s",  # Standardize apostrophe characters.
			"he's": "he’s",
			"she'll": "she’ll",
			"he'll": "he’ll",
			"she'd": "she’d",
			"he'd": "he’d",
			"mr": "mr.",  # Standardize mr and ms. Some of game's mr and ms tags don't have trailing dots, while others do. This handles that inconsistency.
			"ms": "ms."
		}.get(standardizeTagText, standardizeTagText)

	@classmethod
	def FixGenderTagUsageInconsistency (cls, text: str, cachedGenderTagPairMatches: typing.List[GenderedLanguage.CachedGenderTagPairMatch]) -> str:
		fixedText = ""  # type: str

		unfixedTextStartPosition = None  # type: typing.Optional[int]

		girlBoyTagTexts = {
			"girl",
			"boy"
		}  # type: typing.Set[str]

		for cachedPairMatch in cachedGenderTagPairMatches:  # type: GenderedLanguage.CachedGenderTagPairMatch
			nextUnfixedTextStartPosition = cachedPairMatch.MatchEndPosition  # type: int

			if cachedPairMatch.FirstTagTextLower in girlBoyTagTexts and cachedPairMatch.SecondTagTextLower in girlBoyTagTexts:
				textAfterGenderTag = text[cachedPairMatch.MatchEndPosition: cachedPairMatch.MatchEndPosition + 6]  # type: str  # 6 is the number of characters in 'friend'.

				if textAfterGenderTag.lower() == "friend":
					fixedText += text[unfixedTextStartPosition: cachedPairMatch.MatchStartPosition] + \
								 ("{%s%s.%s%s}{%s%s.%s%s}" % (
									 cachedPairMatch.FirstTagGender, cachedPairMatch.FirstTagTokenIndexString, cachedPairMatch.FirstTagText, textAfterGenderTag,
									 cachedPairMatch.SecondTagGender, cachedPairMatch.SecondTagTokenIndexString, cachedPairMatch.SecondTagText, textAfterGenderTag
								 ))

					unfixedTextStartPosition = nextUnfixedTextStartPosition + 6
					continue

			fixedText += text[unfixedTextStartPosition: cachedPairMatch.MatchEndPosition]
			unfixedTextStartPosition = nextUnfixedTextStartPosition
			continue

		fixedText += text[unfixedTextStartPosition:]

		return fixedText

	@classmethod
	def GetStandardPronounSets (cls) -> dict:
		standardSets = dict()  # type: dict
		standardSets.update(cls._CreateTheyThemSet())
		standardSets.update(cls._CreateZeZirSet())
		standardSets.update(cls._CreateZeHirSet())
		standardSets.update(cls._CreateXeXemSet())
		standardSets.update(cls._CreateEyEmSet())
		standardSets.update(cls._CreateItSet())
		return standardSets

	@classmethod
	def GetReservedPronounSetIdentifiers (cls) -> list:
		return [
			cls.TheyThemSetIdentifier,
			cls.ZeZirSetIdentifier,
			cls.ZeHirSetIdentifier,
			cls.XeXemSetIdentifier,
			cls.EyEmSetIdentifier,
			cls.ItSetIdentifier
		]

	@classmethod
	def IsHandlingLanguageSTBLFile (cls, stblInstanceHexID: str) -> bool:
		if not isinstance(stblInstanceHexID, str):
			raise Exceptions.IncorrectTypeException(stblInstanceHexID, "stblInstanceHexID", (str,))

		return stblInstanceHexID.startswith(cls.STBLInstanceIDPrefix)

	@classmethod
	def GetPackLocalizationPackageFilePaths (cls, pack: Sims4Common.Pack) -> typing.List[str]:
		if not isinstance(pack, Sims4Common.Pack):
			raise Exceptions.IncorrectTypeException(pack, "pack", (Sims4Common.Pack,))

		if game_services.service_manager is None or game_services.service_manager.client_manager is None:
			return list()

		if pack in LanguageHandlers.NoLocalizationPackagePacks:
			return list()

		gameRootPath = os.path.dirname(os.path.dirname(  # "C:\Program Files (x86)\Origin Games\The Sims 4\Game\Bin" > "C:\Program Files (x86)\Origin Games\The Sims 4"
			os.path.normpath(os.path.abspath(paths.APP_ROOT))  # "C:\Program Files (x86)\Origin Games\The Sims 4\Game\Bin\" > "C:\Program Files (x86)\Origin Games\The Sims 4\Game\Bin" - This is something that is done to this path in the paths module.
		))  # type: str

		if pack == Sims4Common.Pack.BASE_GAME:
			baseGameLocalizationPackageFilePath = os.path.join(gameRootPath, "Data", "Client", cls.GameLocalizationPackageFileName)  # type: str

			if not os.path.exists(baseGameLocalizationPackageFilePath):
				Debug.Log("Could not find the base game's localization package file.\nExpected Location: %s" % baseGameLocalizationPackageFilePath, This.Mod.Namespace, Debug.LogLevels.Warning, group = This.Mod.Namespace, owner = __name__)
				return list()

			return [baseGameLocalizationPackageFilePath]

		else:
			packLocalizationPackageFilePath = os.path.join(gameRootPath, pack.name.upper(), cls.GameLocalizationPackageFileName)  # type: str # TODO revert

			if not os.path.exists(packLocalizationPackageFilePath):
				Debug.Log("Could not find a pack's localization package file.\nPack: %s\nExpected Location: %s" % (pack.name, packLocalizationPackageFilePath), This.Mod.Namespace, Debug.LogLevels.Warning, group = This.Mod.Namespace, owner = __name__)
				return list()

			return [packLocalizationPackageFilePath]

	@classmethod
	def GetCustomPronounSetEditableGenderTagPairs (cls) -> typing.List[str]:
		"""
		Get a list of gender tag pairs that are editable when creating a custom pronoun set.
		"""

		return [
			"she|he",
			"her|him",
			"her|his",
			"hers|his",
			"she’s|he’s",
			"she’ll|he’ll",
			"she’d|he’d",
			"herself|himself"
		]

	@classmethod
	def GetCustomPronounSetStandardValues (cls) -> typing.Dict[str, str]:
		"""
		Get the standard values that custom pronoun sets should have.
		"""

		return {
			"ms.|mr.": "mx.",
			"girlfriend|boyfriend": "partner",
			"sister|brother": "sibling",
			"mother|father": "parent",
			"grandmother|grandfather": "grandparent",
			"granddaughter|grandson": "grandchild",
			"wife|husband": "partner",
			"daughter|son": "child",
			"step-daughter|step-son": "step-child",
			"step-mother|step-father": "step-parent",
			"stepsister|stepbrother": "step-sibling",
			"great-granddaughter|great-grandson": "great-grandchild",
			"great-grandmother|great-grandfather": "great-grandparent",
			"half-sister|half-brother": "half-sibling",
		}

	@classmethod
	def GetMoneyString (cls, moneyAmount: numbers.Number) -> str:
		return "§%s" % str(moneyAmount)

	@classmethod
	def GetSimFullNameString (cls, simFirstName: str, simLastName: str) -> str:
		if not simLastName.isspace():
			return "%s %s" % (simFirstName, simLastName)
		else:
			return simFirstName

	@classmethod
	def AskToApplyAndFixCustomPronounSetPair(cls, modifyingSet: dict, modifyingPairIdentifier: str, chosenPairValue: str, callback: typing.Callable[[bool], None]) -> None:
		try:
			if modifyingPairIdentifier == "she’s|he’s":
				chosenPairValueLower = chosenPairValue.lower().replace("'", "’")

				if chosenPairValueLower == "they’re" or chosenPairValueLower == "they’ve":
					def createFixPronounIsContractionCallback () -> typing.Callable[[bool], None]:

						def fixPronounIsContractionCallback (doFix: bool) -> None:
							if doFix:
								modifyingSet[modifyingPairIdentifier] = cls._GetTheyThemSetPronounIsContraction()

							callback(doFix)

						return fixPronounIsContractionCallback

					cls._AskToDoTheyThemFix(createFixPronounIsContractionCallback())
					return
			else:
				callback(False)
		except:
			Debug.Log("Failed to apply or ask to apply a fix to a custom pronoun set pair.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)
			callback(False)


	@classmethod
	def _CreateTheyThemSet (cls) -> dict:
		# noinspection SpellCheckingInspection
		creatingSet = {
			cls.TheyThemSetIdentifier: {
				"Title": cls.TheyThemSetTitle,
				"Set": {
					"she|he": "they",
					"her|him": "them",
					"her|his": "their",
					"hers|his": "theirs",
					"she’s|he’s": cls._GetTheyThemSetPronounIsContraction(),
					"she’ll|he’ll": "they’ll",
					"she’d|he’d": "they’d",
					"herself|himself": "themself",
					"ms.|mr.": "mx.",
					"girlfriend|boyfriend": "partner",
					"sister|brother": "sibling",
					"mother|father": "parent",
					"grandmother|grandfather": "grandparent",
					"granddaughter|grandson": "grandchild",
					"wife|husband": "partner",
					"daughter|son": "child",
					"step-daughter|step-son": "step-child",
					"step-mother|step-father": "step-parent",
					"stepsister|stepbrother": "step-sibling",
					"great-granddaughter|great-grandson": "great-grandchild",
					"great-grandmother|great-grandfather": "great-grandparent",
					"half-sister|half-brother": "half-sibling",
				}
			}
		}

		return creatingSet

	@classmethod
	def _GetTheyThemSetPronounIsContraction (cls) -> typing.Union[None, int, str, dict]:
		return {
			"Cases": {
				# Base game
				3848466204: ["they’re"],
				3315035175: ["they’re"],
				1624609554: ["they’re"],
				4227368516: ["they’re"],
				3466820587: ["they’re"],
				2288915427: ["they’re"],
				3169408581: ["they’re"],
				2678019203: ["they’ve"],
				3330177454: ["they’ve", "they’ve"],
				1827704107: ["they’re"],
				2578737338: ["they’ve"],
				3492028680: ["they’re"],
				1333238331: ["they’ve"],
				515967586: ["they’ve", "they’ve"],
				3561336254: ["they’re"],
				3704738005: ["they’re"],
				465738403: ["they’re"],
				3226398757: ["they’re"],
				3141825038: ["they’ve"],
				2104253335: ["they’re"],
				3228515647: ["they’re"],
				755536319: ["they’re"],
				218063767: ["they’re"],
				2381004192: ["they’ve"],
				526003011: ["they’re"],
				260030352: ["they’re"],
				1570293922: ["they’re"],
				425395394: ["they’re"],
				2162386291: ["they’ve"],
				2657241850: ["they’re"],
				2899699152: ["they’re", "they’ve"],
				274559984: ["they’re"],
				2192147899: ["they’ve"],
				281927073: ["they’re"],
				1637670727: ["they’ve"],
				4276505725: ["they’ve"],
				1519601547: ["they’re"],
				3556521145: ["they’ve"],
				229207012: ["they’re", "they’re"],
				1378797210: ["they’re"],
				1945427369: ["they’ve", "they’re"],
				762148562: ["they’re"],
				490246009: ["they’re"],
				2195308598: ["they’re"],
				1787343902: ["they’re", "they’ve"],
				4181546333: ["they’re"],
				3170322154: ["they’re"],
				146307187: ["they’ve"],
				2828163811: ["they’re"],
				527186830: ["they’re"],
				879197290: ["they’re"],
				1308055271: ["they’re"],
				326337872: ["they’re"],
				1446312658: ["they’ve"],
				3471668398: ["they’re"],
				421326762: ["they’re"],
				1882135755: ["they’re"],
				530741329: ["they’ve"],
				642195893: ["they’re"],
				765309846: ["they’ve"],
				689897592: ["they’ve"],
				381123135: ["they’ve"],
				3036917095: ["they’ve"],
				3616413496: ["they’re"],
				2635592640: ["they’ve"],
				1638234967: ["they’re"],
				256767393: ["they’re"],
				1409130717: ["they’re", "they’ve"],
				1143457402: ["they’ve"],
				3914469433: ["they’re"],
				3381386026: ["they’re"],
				482107880: ["they’ve"],
				3570446735: ["they’re"],
				2308263534: ["they’re"],
				2606364627: ["they’re"],
				2704319052: ["they’ve"],
				528741600: ["they’re"],
				884298658: ["they’re"],
				3433334323: ["they’re"],
				2032866090: ["they’re"],
				1304979815: ["they’ve"],
				3046188260: ["they’re", "they’re"],
				2135613228: ["they’re"],
				2067337094: ["they’re"],
				3657472333: ["they’re"],
				900908594: ["they’ve"],
				2525873244: ["they’re"],
				2799360804: ["they’re"],
				2229212067: ["they’re"],
				1450177386: ["they’ve"],
				1042303010: ["they’re"],
				1333533282: ["they’ve"],
				2824793300: ["they’re"],
				576298777: ["they’re"],
				202995658: ["they’ve"],
				2914066380: ["they’re"],
				3463186294: ["they’ve"],
				2353379673: ["they’re"],
				1949298448: ["they’re"],
				2908419715: ["they’re"],
				2730851378: ["they’re"],
				53049609: ["they’re"],
				1879120390: ["they’ve"],
				3960410444: ["they’re"],
				1048614018: ["they’re"],
				2272745476: ["they’re"],
				327268175: ["they’ve"],
				2861103239: ["they’re"],
				1259997717: ["they’re"],
				1248988049: ["they’ve"],
				524550395: ["they’re"],
				2146515970: ["they’ve"],
				2432123903: ["they’ve", "they’re"],
				1527763005: ["they’re"],
				388163329: ["they’re", "they’re"],
				3560232075: ["they’re"],
				3398058508: ["they’re"],
				793974509: ["they’ve"],
				4255087623: ["they’re"],

				# EP01
				1662158783: ["they’re"],

				# EP04
				854349599: ["they’re"],
				3541862656: ["they’re"],

				# EP06
				1474885875: ["they’ve", "they’re"],
				1220195416: ["they’ve"],
				3803402225: ["they’re"],
				467930270: ["they’re", "they’re", "they’ve"],
				3425777175: ["they’re", "they’ve"],
				4051813452: ["they’re"],
				2837713442: ["they’re"],
				2915358164: ["they’ve", "they’re"],
				1388826329: ["they’re"],
				1989470220: ["they’ve"],
				1692166899: ["they’re"],
				1829982328: ["they’re"],
				2399145537: ["they’re"],
				1021820828: ["they’re"],
				3813596509: ["they’re"],
				1776187394: ["they’re"],
				1063470410: ["they’re"],
				2722379016: ["they’re"],
				455203967: ["they’re"],
				3349965145: ["they’re"],
				979735164: ["they’re"],
				3272738715: ["they’re"],
				2941426802: ["they’re"],
				2709371049: ["they’re"],
				1106539124: ["they’re"],
				518024581: ["they’re"],
				256472513: ["they’re"],
				741211455: ["they’re"],
				2385622025: ["they’re"],
				383194337: ["they’re"],
				279240105: ["they’re"],
				2500858723: ["they’ve"],
				357674073: ["they’re"],
				3304244932: ["they’re"],
				3463122932: ["they’re"],
				25995852: ["they’re"],
				78585291: ["they’re"],
				1126985834: ["they’re"],
				1823306900: ["they’ve"],
				1088216950: ["they’re"],
				1412561533: ["they’ve"],
				1037909830: ["they’re"],
				3577957337: ["they’re"],
				2115736118: ["they’re"],
				223668276: ["they’re"],
				2873568945: ["they’re"],
				4005536516: ["they’ve"],
				4289836499: ["they’ve", None, "they’re"],
				1269785600: ["they’re"],
				4013355759: ["they’re", "they’ve"],
				3216902865: ["they’ve"],
				1669566961: ["they’ve", "they’ve"],
				60213487: [None, None, "they’re"],
				1906335606: ["they’re", "they’re"],
				1627066167: ["they’ve"],
				1282045627: ["they’re"],
				3665016674: ["they’ve"],
				173055719: [None],
				1648700187: ["they’re", "they’ve", "they’ve"],
				299471275: ["they’re", "they’ve", "they’ve", "they’ve"],
				746070453: ["they’re", "they’ve", "they’ve"],
				3257836685: ["they’re", "they’ve"],
				2404242656: ["they’re", "they’ve"],
				570100257: ["they’re"],
				2742046835: ["they’re", "they’re"],
				3633050323: ["they’ve"],

				# EP07
				3683304988: ["they’re"],
				4083831262: ["they’re"],
				2566275947: ["they’re"],
				132224273: ["they’re"],
				1022143122: ["they’re"],
				4239362667: ["they’re"],
				155977711: ["they’re"],

				# EP08
				731208129: ["they’re"],
				2165543469: ["they’re"],
				3812823502: ["they’re"],
				2091981419: ["they’re"],
				122260999: ["they’re"],
				4190474701: ["they’re"],
				3072030183: ["they’re"],
				1421972396: ["they’re"],
				2321907389: ["they’re"],

				# EP10
				1026766317: ["they’ve"],
				4141109267: ["they’re"],
				829066520: ["they’re"],
				1655784957: ["they’ve"],
				4124333197: ["they’re"],
				4167129096: ["they’re"],
				1621259442: ["they’re"],
				2657358867: ["they’re"],
				1677419905: ["they’re", "they’ve"],
				1633334723: ["they’re"],
				1597935695: ["they’re"],
				2078949162: ["they’re"],
				3052483502: ["they’re"],
				581190033: ["they’re", "they’re", "they’re"],
				1190606639: ["they’re"],
				4124192543: ["they’re"],
				2129713926: ["they’re"],
				774846671: ["they’re"],
				1030449092: ["they’re"],

				# GP06
				106949386: ["they’re"],
				1145245963: ["they’ve"],
				2043703112: ["they’ve"],
				639201188: ["they’ve"],

				# SP06
				3465508511: ["they’ve"],
				1617138310: ["they’ve"],
				819621328: ["they’re"],
				2434216330: ["they’re"],
				2096424560: ["they’re"],
				2170973686: ["they’ve"],

				# SP11
				3637497501: ["they’re"],
			}
		}

	@classmethod
	def _CreateZeZirSet (cls) -> dict:
		# noinspection SpellCheckingInspection
		creatingSet = {
			cls.ZeZirSetIdentifier: {
				"Title": cls.ZeZirTitle,
				"Set": {
					"she|he": "ze",
					"her|him": "zir",
					"her|his": "zir",
					"hers|his": "zirs",
					"she’s|he’s": "ze’s",
					"she’ll|he’ll": "ze’ll",
					"she’d|he’d": "ze’d",
					"herself|himself": "zirself",
					"ms.|mr.": "mx.",
					"girlfriend|boyfriend": "partner",
					"sister|brother": "sibling",
					"mother|father": "parent",
					"grandmother|grandfather": "grandparent",
					"granddaughter|grandson": "grandchild",
					"wife|husband": "partner",
					"daughter|son": "child",
					"step-daughter|step-son": "step-child",
					"step-mother|step-father": "step-parent",
					"stepsister|stepbrother": "step-sibling",
					"great-granddaughter|great-grandson": "great-grandchild",
					"great-grandmother|great-grandfather": "great-grandparent",
					"half-sister|half-brother": "half-sibling",
				}
			}
		}

		return creatingSet

	@classmethod
	def _CreateZeHirSet (cls) -> dict:
		# noinspection SpellCheckingInspection
		creatingSet = {
			cls.ZeHirSetIdentifier: {
				"Title": cls.ZeHirTitle,
				"Set": {
					"she|he": "ze",
					"her|him": "hir",
					"her|his": "hir",
					"hers|his": "hirs",
					"she’s|he’s": "ze’s",
					"she’ll|he’ll": "ze’ll",
					"she’d|he’d": "ze’d",
					"herself|himself": "hirself",
					"ms.|mr.": "mx.",
					"girlfriend|boyfriend": "partner",
					"sister|brother": "sibling",
					"mother|father": "parent",
					"grandmother|grandfather": "grandparent",
					"granddaughter|grandson": "grandchild",
					"wife|husband": "partner",
					"daughter|son": "child",
					"step-daughter|step-son": "step-child",
					"step-mother|step-father": "step-parent",
					"stepsister|stepbrother": "step-sibling",
					"great-granddaughter|great-grandson": "great-grandchild",
					"great-grandmother|great-grandfather": "great-grandparent",
					"half-sister|half-brother": "half-sibling",
				}
			}
		}

		return creatingSet

	@classmethod
	def _CreateXeXemSet (cls) -> dict:
		# noinspection SpellCheckingInspection
		creatingSet = {
			cls.XeXemSetIdentifier: {
				"Title": cls.XeXemTitle,
				"Set": {
					"she|he": "xe",
					"her|him": "xem",
					"her|his": "xyr",
					"hers|his": "xyrs",
					"she’s|he’s": "xe’s",
					"she’ll|he’ll": "xe’ll",
					"she’d|he’d": "xe’d",
					"herself|himself": "xyrself",
					"ms.|mr.": "mx.",
					"girlfriend|boyfriend": "partner",
					"sister|brother": "sibling",
					"mother|father": "parent",
					"grandmother|grandfather": "grandparent",
					"granddaughter|grandson": "grandchild",
					"wife|husband": "partner",
					"daughter|son": "child",
					"step-daughter|step-son": "step-child",
					"step-mother|step-father": "step-parent",
					"stepsister|stepbrother": "step-sibling",
					"great-granddaughter|great-grandson": "great-grandchild",
					"great-grandmother|great-grandfather": "great-grandparent",
					"half-sister|half-brother": "half-sibling",
				}
			}
		}

		return creatingSet

	@classmethod
	def _CreateEyEmSet (cls) -> dict:
		# noinspection SpellCheckingInspection
		creatingSet = {
			cls.EyEmSetIdentifier: {
				"Title": cls.EyEmTitle,
				"Set": {
					"she|he": "ey",
					"her|him": "em",
					"her|his": "eir",
					"hers|his": "eirs",
					"she’s|he’s": "ey’s",
					"she’ll|he’ll": "ey’ll",
					"she’d|he’d": "ey’d",
					"herself|himself": "emself",
					"ms.|mr.": "mx.",
					"girlfriend|boyfriend": "partner",
					"sister|brother": "sibling",
					"mother|father": "parent",
					"grandmother|grandfather": "grandparent",
					"granddaughter|grandson": "grandchild",
					"wife|husband": "partner",
					"daughter|son": "child",
					"step-daughter|step-son": "step-child",
					"step-mother|step-father": "step-parent",
					"stepsister|stepbrother": "step-sibling",
					"great-granddaughter|great-grandson": "great-grandchild",
					"great-grandmother|great-grandfather": "great-grandparent",
					"half-sister|half-brother": "half-sibling",
				}
			}
		}

		return creatingSet

	@classmethod
	def _CreateItSet (cls) -> dict:
		# noinspection SpellCheckingInspection
		creatingSet = {
			cls.ItSetIdentifier: {
				"Title": cls.ItTitle,
				"Set": {
					"she|he": "it",
					"her|him": "it",
					"her|his": "its",
					"hers|his": "its",
					"she’s|he’s": "it’s",
					"she’ll|he’ll": "it’ll",
					"she’d|he’d": "it’d",
					"herself|himself": "itself",
					"ms.|mr.": "mx.",
					"girlfriend|boyfriend": "partner",
					"sister|brother": "sibling",
					"mother|father": "parent",
					"grandmother|grandfather": "grandparent",
					"granddaughter|grandson": "grandchild",
					"wife|husband": "partner",
					"daughter|son": "child",
					"step-daughter|step-son": "step-child",
					"step-mother|step-father": "step-parent",
					"stepsister|stepbrother": "step-sibling",
					"great-granddaughter|great-grandson": "great-grandchild",
					"great-grandmother|great-grandfather": "great-grandparent",
					"half-sister|half-brother": "half-sibling",
				}
			}
		}

		return creatingSet

	@classmethod
	def _AskToDoTheyThemFix (cls, callback: typing.Callable[[bool], None]) -> None:
		def createDialogCallback () -> typing.Callable:
			def dialogCallback (shownDialog: ui_dialog.UiDialogOkCancel) -> None:
				callback(shownDialog.accepted)

			return dialogCallback

		dialogArguments = {
			"title": cls.AskToDoTheyAreFixDialogTitle.GetCallableLocalizationString(),
			"text": cls.AskToDoTheyAreFixDialogText.GetCallableLocalizationString(),
			"text_ok": cls.AskToDoTheyAreFixDialogYesButton.GetCallableLocalizationString(),
			"text_cancel": cls.AskToDoTheyAreFixDialogNoButton.GetCallableLocalizationString()
		}  # type: typing.Dict[str, ...]

		UIDialogs.ShowOkCancelDialog(callback = createDialogCallback(), queue = False, **dialogArguments)