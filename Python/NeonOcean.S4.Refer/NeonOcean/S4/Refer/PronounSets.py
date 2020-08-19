import typing

from NeonOcean.S4.Main.Tools import Exceptions
from NeonOcean.S4.Refer import LanguageHandlers, Settings

def GetPronounSet (setIdentifier: str, targetLanguageHandler: typing.Type[LanguageHandlers.LanguageHandlerBase]) -> typing.Optional[dict]:
	if not isinstance(setIdentifier, str):
		raise Exceptions.IncorrectTypeException(setIdentifier, "setIdentifier", (str,))

	return GetAllPronounSets(targetLanguageHandler).get(setIdentifier, None)

def GetAllPronounSets (targetLanguageHandler: typing.Optional[typing.Type[LanguageHandlers.LanguageHandlerBase]]) -> dict:
	allSets = dict()  # type: dict
	allSets.update(GetCustomPronounSets())

	if targetLanguageHandler is not None:
		allSets.update(targetLanguageHandler.GetStandardPronounSets())

	return allSets

def GetCustomPronounSets () -> dict:
	customSets = dict()  # type: dict
	customSets.update(Settings.CustomPronounSets.Get())

	return customSets
