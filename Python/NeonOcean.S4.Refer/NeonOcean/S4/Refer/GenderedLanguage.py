from __future__ import annotations

import numbers
import re
import typing

from NeonOcean.S4.Main import Debug
from NeonOcean.S4.Main.Tools import Exceptions, Python, Types
from NeonOcean.S4.Refer import PronounSets, LanguageHandlers, PronounSettings, This
from protocolbuffers import Localization_pb2
from sims import sim_info

class CachedGenderTagPairMatch:
	def __init__ (self, genderTagPairMatch):
		self.FirstTag, self.FirstTagGender, self.FirstTagTokenIndexString, self.FirstTagText, \
		self.SecondTag, self.SecondTagGender, self.SecondTagTokenIndexString, self.SecondTagText = genderTagPairMatch.groups()  # type: str

		self.FirstTagTextLower = self.FirstTagText.lower()  # type: str
		self.SecondTagTextLower = self.SecondTagText.lower()  # type: str

		self.FirstTagTokenIndex = int(self.FirstTagTokenIndexString)  # type: int
		self.SecondTagTokenIndex = int(self.SecondTagTokenIndexString)  # type: int

		self.MatchStartPosition = genderTagPairMatch.start()  # type: int
		self.MatchEndPosition = genderTagPairMatch.end()  # type: int

class _UnsupportedLocalizationStringException(Exception):
	pass

def GetGenderedLocalizationStringText (localizationStringID: int) -> typing.Optional[str]:
	"""
	Get the text of a localization string. This will return none if the entry doesn't exist or it doesn't have gendered language in it (like {F0.Her}).
	"""

	if not isinstance(localizationStringID, int):
		raise Exceptions.IncorrectTypeException(localizationStringID, "localizationStringID", (int,))

	return _genderedLocalizationStrings.get(localizationStringID, None)

def GetLocalizationStringText (localizationStringID: int) -> typing.Optional[str]:
	"""
	Get the text of a localization string This will return none if the entry doesn't exist.
	"""

	if not isinstance(localizationStringID, int):
		raise Exceptions.IncorrectTypeException(localizationStringID, "localizationStringID", (int,))

	return _allLocalizationStrings.get(localizationStringID, None)

def ResolveSTBLText (text: str, tokens: typing.Sequence) -> typing.Optional[str]:
	"""
	Get the true text this STBL string combined with these tokens. This will return none if the text could not be resolved, or if the current language
	is not supported. Not all texts can be resolved because this system doesn't handle every tag that the game can handle.
	"""

	if not isinstance(text, str):
		raise Exceptions.IncorrectTypeException(text, "text", (str,))

	if not isinstance(tokens, typing.Sequence):
		raise Exceptions.IncorrectTypeException(tokens, "tokens", (typing.Sequence,))

	currentLanguageHandler = LanguageHandlers.GetCurrentLanguageHandler()  # type: typing.Optional[typing.Type[LanguageHandlers.LanguageHandlerBase]]

	if currentLanguageHandler is None:
		return None

	try:
		resolvedText = _ResolveRegularTags(text, tokens, currentLanguageHandler)

		if re.match(SingleTagPattern, resolvedText) is not None:
			raise _UnsupportedLocalizationStringException("Found a tag that was never resolved.")

	except _UnsupportedLocalizationStringException:
		Debug.Log("Could not resolve an unsupported localization string.\nText: %s" % text, This.Mod.Namespace, Debug.LogLevels.Warning, group = This.Mod.Namespace, owner = __name__, lockIdentifier = __name__ + ":" + str(Python.GetLineNumber()), lockThreshold = 2)
		return None

	return resolvedText

def CorrectGenderedSTBLText (textKey: int, text: str, tokens: typing.Sequence) -> typing.Optional[str]:
	"""
	Correct this text for these tokens. This will return none if the default, unmodified text should be used instead.
	"""

	if not isinstance(textKey, int):
		raise Exceptions.IncorrectTypeException(textKey, "textKey", (int,))

	if not isinstance(text, str):
		raise Exceptions.IncorrectTypeException(text, "text", (str,))

	if not isinstance(tokens, typing.Sequence):
		raise Exceptions.IncorrectTypeException(tokens, "tokens", (typing.Sequence,))

	currentLanguageHandler = LanguageHandlers.GetCurrentLanguageHandler()  # type: typing.Optional[typing.Type[LanguageHandlers.LanguageHandlerBase]]

	if currentLanguageHandler is None:
		return None

	tokenHasCustomGenderedLanguage = False  # type: bool

	for token in tokens:  # type: typing.Union[typing.Any, sim_info.SimInfo]
		if isinstance(token, sim_info.SimInfo):
			tokenSetSelection = PronounSettings.PronounSetSelection.Get(str(token.id))  # type: str

			if tokenSetSelection == "":
				continue

			tokenHasCustomGenderedLanguage = True

	if not tokenHasCustomGenderedLanguage:
		return None

	correctedText = _CorrectGenderedTagPairs(textKey, text, tokens, currentLanguageHandler)  # type: str

	if correctedText is None:
		return None

	resolvedCorrectedText = ResolveSTBLText(correctedText, tokens)

	return resolvedCorrectedText

def TextIsGendered (text: str) -> typing.Type[bool, typing.List[CachedGenderTagPairMatch]]:
	"""
	Get whether or not this text contains the tags such as '{F0.She}{M0.He}'.
	"""

	if not isinstance(text, str):
		raise Exceptions.IncorrectTypeException(text, "text", (str,))

	genderedTagPairMatches = list()  # type: typing.List[CachedGenderTagPairMatch]

	for genderedTagPairMatch in re.finditer(GenderedTagPairPattern, text):
		genderedTagPairMatchText = genderedTagPairMatch.group()  # type: str

		if genderedTagPairMatchText.count("{") > 2 or genderedTagPairMatchText.count("{") > 2:
			verifyTermCountMatch = re.search(HasTooManyGenderedTermsPattern, genderedTagPairMatchText)

			if verifyTermCountMatch is not None and genderedTagPairMatchText != verifyTermCountMatch.group():
				continue

		cachedGenderedTagPairMatch = CachedGenderTagPairMatch(genderedTagPairMatch)  # type: CachedGenderTagPairMatch

		if cachedGenderedTagPairMatch.FirstTagGender == "U" or cachedGenderedTagPairMatch.SecondTagGender == "U":
			continue  # Make sure the tags don't start with a 'U'. 'U' is only used for lists of sims where they are not all the same gender.

		if cachedGenderedTagPairMatch.FirstTagGender == cachedGenderedTagPairMatch.SecondTagGender:
			continue  # Makes sure that the two side by side gender tags are male and female. Filters out {M0.Him}{M0.Him}, if such an stbl entry exists.

		if cachedGenderedTagPairMatch.FirstTagTokenIndex != cachedGenderedTagPairMatch.SecondTagTokenIndex:
			continue  # Makes sure that the two side by side gender tags are for the same sim. Filters out {M0.Him}{F1.Her}, if such an stbl entry exists.

		if cachedGenderedTagPairMatch.FirstTagText.lower() == cachedGenderedTagPairMatch.SecondTagText.lower():
			continue  # Handles cases where gender tags exist, but each tag's text is actually identical. Filters out entries such as {M0.Host}{F0.Host}.

		genderedTagPairMatches.append(cachedGenderedTagPairMatch)

	return len(genderedTagPairMatches) != 0, genderedTagPairMatches

def _GetGenderTagPairIdentifier (femaleTagText: str, maleTagText: str, tagLanguageHandler: typing.Type[LanguageHandlers.LanguageHandlerBase]) -> str:
	standardizedFemaleTagText = tagLanguageHandler.GetGenderTagTextIdentifierPart(femaleTagText).replace("|", "")  # type: str
	standardizedMaleTagText = tagLanguageHandler.GetGenderTagTextIdentifierPart(maleTagText).replace("|", "")  # type: str

	return standardizedFemaleTagText + "|" + standardizedMaleTagText

def _CorrectGenderedTagPairs (textKey: int, text: str, tokens: typing.Sequence, languageHandler: typing.Type[LanguageHandlers.LanguageHandlerBase]) -> typing.Optional[str]:
	correctedText = ""  # type: str
	uncorrectedTextStartPosition = None  # type: typing.Optional[int]

	genderedTagGroupIndex = -1  # type: int

	def addDefaultText () -> None:
		nonlocal correctedText

		if tagToken.is_female:
			correctedText += text[uncorrectedTextStartPosition: tagPairStartPosition] + femaleText
		else:
			correctedText += text[uncorrectedTextStartPosition: tagPairStartPosition] + maleText

	def addFemaleText () -> None:
		nonlocal correctedText
		correctedText += text[uncorrectedTextStartPosition: tagPairStartPosition] + femaleText

	def addMaleText () -> None:
		nonlocal correctedText
		correctedText += text[uncorrectedTextStartPosition: tagPairStartPosition] + maleText

	def addSpecificText (addingText: str) -> None:
		nonlocal correctedText
		correctedText += text[uncorrectedTextStartPosition: tagPairStartPosition] + addingText

	def addGenderText (addingGenderTextIdentifier: typing.Union[None, int]) -> None:
		if addingGenderTextIdentifier is None:
			addDefaultText()
		elif addingGenderTextIdentifier == 0:  # Use the male tag.
			addFemaleText()
		elif addingGenderTextIdentifier == 1:  # Use the male tag.
			addMaleText()
		else:  # The number must be 0 or 1, anything else falls back to default.
			addDefaultText()

	for genderedTagPairMatch in re.finditer(GenderedTagPairPattern, text):
		genderedTagPairMatchText = genderedTagPairMatch.group()  # type: str

		if genderedTagPairMatchText.count("{") > 2 or genderedTagPairMatchText.count("{") > 2:
			verifyTermCountMatch = re.search(HasTooManyGenderedTermsPattern, genderedTagPairMatchText)

			if verifyTermCountMatch is not None and genderedTagPairMatchText != verifyTermCountMatch.group():
				continue

		firstTag, firstTagGender, firstTagTokenIndexString, firstTagText, \
		secondTag, secondTagGender, secondTagTokenIndexString, secondTagText = genderedTagPairMatch.groups()  # type: str

		firstTagTokenIndex = int(firstTagTokenIndexString)  # type: int
		secondTagTokenIndex = int(secondTagTokenIndexString)  # type: int

		tagPairStartPosition = genderedTagPairMatch.start()  # type: int
		tagPairEndPosition = genderedTagPairMatch.end()  # type: int
		nextUnfixedTextStartPosition = tagPairEndPosition  # type: int

		if firstTagGender == "U" or secondTagGender == "U":
			continue  # Make sure the tags don't start with a 'U'. 'U' is only used for lists of sims where they are not all the same gender.

		if firstTagGender == secondTagGender:
			continue  # Makes sure that the two side by side gender tags are male and female. Filters out {M0.Him}{M0.Him}, if such an stbl entry exists.

		if int(firstTagTokenIndex) != int(secondTagTokenIndex):
			continue  # Makes sure that the two side by side gender tags are for the same sim. Filters out {M0.Him}{F1.Her}, if such an stbl entry exists.

		genderedTagGroupIndex += 1

		try:
			tagToken = tokens[firstTagTokenIndex]  # type: typing.Union[sim_info.SimInfo, typing.Any]
		except IndexError:
			pass
		else:
			if isinstance(tagToken, sim_info.SimInfo):
				tagTokenSetSelection = PronounSettings.PronounSetSelection.Get(str(tagToken.id))  # type: str
				tagTokenSetSelection = tagTokenSetSelection.lower()  # type: str

				tagTokenFallbackString = PronounSettings.PronounFallback.Get(str(tagToken.id))  # type: str

				if tagTokenFallbackString == "":
					tagTokenFallback = None  # type: typing.Optional[int]
				else:
					tagTokenFallback = int(tagTokenFallbackString)  # type: typing.Optional[int]

				femaleText, maleText = ((firstTagText, secondTagText) if firstTagGender.lower() == "f" else (secondTagText, firstTagText))  # type: str, str

				if tagTokenSetSelection == "":  # Default selection
					addDefaultText()
				elif tagTokenSetSelection == "0":  # Female selection
					addFemaleText()
				elif tagTokenSetSelection == "1":  # Male selection
					addMaleText()
				else:
					allPronounSets = PronounSets.GetAllPronounSets(languageHandler)  # type: dict
					allPronounSets = { loweringSetIdentifier.lower(): loweringSetValue for loweringSetIdentifier, loweringSetValue in allPronounSets.items() }
					tagTokenSetContainer = allPronounSets.get(tagTokenSetSelection, None)  # type: typing.Optional[dict]

					if tagTokenSetContainer is None:
						addDefaultText()
					else:
						tagPairIdentifier = _GetGenderTagPairIdentifier(femaleText, maleText, languageHandler)  # type: str

						tagTokenSet = tagTokenSetContainer["Set"]

						tagTokenSetPairValue = tagTokenSet.get(tagPairIdentifier, None)  # type: typing.Union[None, int, str, dict]

						if tagTokenSetPairValue is None:  # Use default for this tag pair
							addGenderText(tagTokenFallback)
						elif isinstance(tagTokenSetPairValue, int):
							addGenderText(tagTokenSetPairValue)
						elif isinstance(tagTokenSetPairValue, str):
							if tagTokenSetPairValue == "" or tagTokenSetPairValue.isspace():
								addGenderText(tagTokenFallback)
							else:
								addSpecificText(tagTokenSetPairValue)
						elif isinstance(tagTokenSetPairValue, dict):
							tagTokenSetCasesDefault = tagTokenSetPairValue.get("Default", None)  # type: typing.Optional[str]
							tagTokenSetCases = tagTokenSetPairValue["Cases"]  # type: dict

							tagTokenSetChangeCase = tagTokenSetCases.get(textKey, None)  # type: typing.Optional[typing.List[str]]

							if tagTokenSetChangeCase is None:
								if tagTokenSetCasesDefault is not None:
									addSpecificText(tagTokenSetCasesDefault)
								else:
									addGenderText(tagTokenFallback)
							else:
								try:
									tagTokenSetChangeCaseText = tagTokenSetChangeCase[genderedTagGroupIndex]
								except IndexError:
									if tagTokenSetCasesDefault is not None:
										addSpecificText(tagTokenSetCasesDefault)
									else:
										addGenderText(tagTokenFallback)
								else:
									addSpecificText(tagTokenSetChangeCaseText)
						else:
							Debug.Log("Unknown gendered pair set value for '%s' in the set '%s'." % (tagPairIdentifier, tagTokenSetSelection), This.Mod.Namespace, Debug.LogLevels.Error, group = This.Mod.Namespace, owner = __name__, lockIdentifier = __name__ + ":" + str(Python.GetLineNumber()), lockThreshold = 2)
							addGenderText(tagTokenFallback)

		uncorrectedTextStartPosition = nextUnfixedTextStartPosition

	correctedText += text[uncorrectedTextStartPosition:]

	return correctedText

def _ResolveRegularTags (text: str, tokens: typing.Sequence, languageHandler: typing.Type[LanguageHandlers.LanguageHandlerBase]) -> typing.Optional[str]:
	# This doesn't completely replace the game's stbl formatting system.

	correctedText = ""  # type: str
	uncorrectedTextStartPosition = None  # type: typing.Optional[int]

	def addText (addingText: str) -> None:
		nonlocal correctedText

		if tagToken.is_female:
			correctedText += text[uncorrectedTextStartPosition: tagStartPosition] + addingText
		else:
			correctedText += text[uncorrectedTextStartPosition: tagStartPosition] + addingText

	def addTokenText (addingLocalizationToken) -> None:
		nonlocal correctedText

		tokenTypeHandler = tokenTypeHandlers.get(addingLocalizationToken.type, None)

		if tokenTypeHandler is not None:
			tokenTypeHandler(addingLocalizationToken)

	def addSimTokenText (addingLocalizationToken) -> None:
		if tagText == "SimFirstName":
			addText(addingLocalizationToken.first_name)
		elif tagText == "SimLastName":
			addText(addingLocalizationToken.last_name)
		elif tagText == "SimName":
			simName = None  # type: typing.Optional[str]

			if addingLocalizationToken.full_name_key != 0:
				simName = GetLocalizationStringText(addingLocalizationToken.full_name_key)  # type: typing.Optional[str]

			if simName is None:
				simName = languageHandler.GetSimFullNameString(addingLocalizationToken.first_name, addingLocalizationToken.last_name)

			addText(simName)

	def addStringTokenText (addingLocalizationToken) -> None:
		if tagText == "String":
			resolvedStringToken = ResolveSTBLText(addingLocalizationToken.text_string, addingLocalizationToken.text_string.tokens)  # type: typing.Optional[str]

			if resolvedStringToken is not None:
				addText(resolvedStringToken)
		else:
			raise _UnsupportedLocalizationStringException("The tag '%s' is an unknown tag for a localization string token." % tagText)

	def addRawTextTokenText (addingLocalizationToken) -> None:
		if tagText == "String":
			addText(addingLocalizationToken.raw_text)
		else:
			raise _UnsupportedLocalizationStringException("The tag '%s' is an unknown tag for a raw text token." % tagText)

	def addNumberTokenText (addingLocalizationToken) -> None:
		if tagText == "Number":
			addText(str(addingLocalizationToken.number))
		elif tagText == "Money":
			addText(languageHandler.GetMoneyString(tagToken))
		else:
			raise _UnsupportedLocalizationStringException("The tag '%s' is an unknown tag for a number token." % tagText)

	def addObjectTokenText (addingLocalizationToken) -> None:
		if tagText == "ObjectName":
			if addingLocalizationToken.custom_name != "":
				addingText = addingLocalizationToken.custom_name
			else:
				addingText = GetLocalizationStringText(addingLocalizationToken.catalog_name_key)
		elif tagText == "ObjectDescription":
			if addingLocalizationToken.custom_description != "":
				addingText = addingLocalizationToken.custom_description
			else:
				addingText = GetLocalizationStringText(addingLocalizationToken.catalog_description_key)
		elif tagText == "ObjectCatalogName":
			addingText = GetLocalizationStringText(addingLocalizationToken.catalog_name_key)
		elif tagText == "ObjectCatalogDescription":
			addingText = GetLocalizationStringText(addingLocalizationToken.catalog_description_key)
		else:
			raise _UnsupportedLocalizationStringException("The tag '%s' is an unknown tag for an object token." % tagText)

		if addingText is not None:
			addText(addingText)

	# noinspection PyUnresolvedReferences
	tokenTypeHandlers = {
		Localization_pb2.LocalizedStringToken.SIM: addSimTokenText,
		Localization_pb2.LocalizedStringToken.STRING: addStringTokenText,
		Localization_pb2.LocalizedStringToken.RAW_TEXT: addRawTextTokenText,
		Localization_pb2.LocalizedStringToken.NUMBER: addNumberTokenText,
		Localization_pb2.LocalizedStringToken.OBJECT: addObjectTokenText
	}

	for regularTagMatch in re.finditer(SingleTagRegularPattern, text):
		tag, tagTokenIndexString, tagText = regularTagMatch.groups()  # type: str

		tagTokenIndex = int(tagTokenIndexString)  # type: int

		tagStartPosition = regularTagMatch.start()  # type: int
		tagEndPosition = regularTagMatch.end()  # type: int
		nextUnfixedTextStartPosition = tagEndPosition  # type: int

		try:
			tagToken = tokens[tagTokenIndex]
		except IndexError:
			pass
		else:
			if hasattr(tagToken, "populate_localization_token"):
				temporaryLocalizationToken = Localization_pb2.LocalizedStringToken()
				# noinspection PyUnresolvedReferences
				temporaryLocalizationToken.type = Localization_pb2.LocalizedStringToken.INVALID
				tagToken.populate_localization_token(temporaryLocalizationToken)

				# noinspection PyTypeChecker
				addTokenText(temporaryLocalizationToken)
			elif isinstance(tagToken, numbers.Number):
				if tagText == "Number":  # Tags like these are case sensitive in the base game so they are here as well.
					addText(str(tagToken))
				elif tagText == "Money":
					addText(languageHandler.GetMoneyString(tagToken))
				else:
					raise _UnsupportedLocalizationStringException("The tag '%s' is an unknown tag for a number token." % tagText)
			elif isinstance(tagToken, str):
				if tagText == "String":
					addText(tagToken)
				else:
					raise _UnsupportedLocalizationStringException("The tag '%s' is an unknown tag for a raw text token." % tagText)
			elif isinstance(tagToken, Localization_pb2.LocalizedString):
				# noinspection PyUnresolvedReferences
				tagTokenText = _allLocalizationStrings.get(tagToken.hash, None)  # type: typing.Optional[str]

				if tagTokenText is not None:
					addText(tagTokenText)
			else:
				raise _UnsupportedLocalizationStringException("Unsupported token type '%s'." % Types.GetFullName(tagToken))

		uncorrectedTextStartPosition = nextUnfixedTextStartPosition

	correctedText += text[uncorrectedTextStartPosition:]

	return correctedText

SingleTagPattern = re.compile("({([^\}]+)\})")

SingleTagRegularPattern = re.compile("({([0-9])+\.([^\}]+)\})")

SingleTagGenderedPattern = re.compile("({([FMU])([0-9])+\.([^\}]+)\})")

GenderedTagPairPattern = re.compile("({([FMU])([0-9])+\.([^\}]+)\})"
									"\s*"
									"({([FMU])([0-9])+\.([^\}]+)\})"
									"(?:\s*{[FMU][0-9]+\.[^\}]+\})*")

HasTooManyGenderedTermsPattern = re.compile("{[FMU][0-9]+\.[^\}]+\}"
											"\s*"
											"{[FMU][0-9]+\.[^\}]+\}",
											re.RegexFlag.IGNORECASE)  # Used to test an entry to see if the matched section has too many gendered terms in a row. This is only used if more than 2 open brackets and 2 closed brackets exist in the original match.

_allLocalizationStrings = dict()  # type: typing.Dict[int, str]
_genderedLocalizationStrings = dict()  # type: typing.Dict[int, str]
