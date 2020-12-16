from __future__ import annotations

import enum_lib
import numbers
import typing

import game_services
import services
from NeonOcean.S4.Main import Debug, Director, Language as MainLanguage
from NeonOcean.S4.Main.Tools import Exceptions, Python, Version
from NeonOcean.S4.Main.UI import Notifications
from NeonOcean.S4.Refer import GenderedLanguage, This
from server import client
from sims4 import common as Sims4Common
from ui import ui_dialog_notification

class Language(enum_lib.IntFlag):
	English = 0  # type: Language
	ChineseSimplified = 1  # type: Language
	ChineseTraditional = 2  # type: Language
	Czech = 3  # type: Language
	Danish = 4  # type: Language
	Dutch = 5  # type: Language
	Finnish = 6  # type: Language
	French = 7  # type: Language
	German = 8  # type: Language
	Greek = 9  # type: Language
	Hungarian = 10  # type: Language
	Italian = 11  # type: Language
	Japanese = 12  # type: Language
	Korean = 13  # type: Language
	Norwegian = 14  # type: Language
	Polish = 15  # type: Language
	PortuguesePortugal = 16  # type: Language
	PortugueseBrazil = 17  # type: Language
	Russian = 18  # type: Language
	SpanishSpain = 19  # type: Language
	SpanishMexico = 20  # type: Language
	Swedish = 21  # type: Language
	Thai = 22  # type: Language

class LanguageHandlerBase:
	IsLanguageHandler = False  # type: bool  # Set this to true for classes that inherits this base and are a fully fledged language handler.

	HandlingLanguage = Language.English  # type: Language

	GameIdentifier = ""  # type: str  # The string returned by The Sims 4's "get_locale" function located in the services module.

	def __init_subclass__ (cls, **kwargs):
		if cls.IsLanguageHandler:
			RegisterLanguageHandler(cls)

	@classmethod
	def GetHandlerVersion (cls) -> Version.Version:
		"""
		Get the current version of this handler. This can return the handler's mod's version.
		"""

		raise NotImplementedError()

	@classmethod
	def GetMinimumCacheHandlerVersion (cls) -> typing.Optional[Version.Version]:
		"""
		Get the lowest handler version that we can read cached gendered language files from. All cache files made by handlers lower than this version will
		be ignored. Let this return none to have no minimum version.
		"""

		raise NotImplementedError()

	@classmethod
	def GetGenderTagTextIdentifierPart (cls, tagText: str) -> str:
		"""
		Get a single gender tag's identifier part when given the tag's text. This should be used to standardize inconsistencies within a gender tag.
		For example, the English language handler return's "She’d" when "She'd" is inputted as the game developers are inconsistent in which apostrophe
		character they use.

		A gender tag's text is only run through this method when we are trying to get the appropriate replacement for this tag in from sim's selected
		gendered language set.
		"""

		raise NotImplementedError()

	# noinspection PyUnresolvedReferences
	@classmethod
	def FixGenderTagUsageInconsistency (cls, text: str, genderTagMatches: typing.List[GenderedLanguage.CachedGenderTagPairMatch]) -> str:
		"""
		Fix an STBL entry's gender tag use inconsistency. For example, this will change the less common "{F0.Girl}{M0.Boy}friend" to
		"{F0.Girlfriend}{M0.Boyfriend}", in order to prevent issues with the regular "{F0.Girl}{M0.Boy}" tags.
		:param text: The STBL string that we are looking to fix. This should already be tested to confirm the text has valid gender tags.
		:type text: str

		:param genderTagMatches: A list of regex match objects that point to all sets of gender tags in the text. The regex matches are expected to
		have 8 groups, 4 for each gender tags in a set.
		Example of expected tag groups:
		genderTagMatches.groups()[0] == {F0.She}
		genderTagMatches.groups()[1] == F
		genderTagMatches.groups()[2] == 0
		genderTagMatches.groups()[3] == She
		genderTagMatches.groups()[4] == {M0.He}
		genderTagMatches.groups()[5] == M
		genderTagMatches.groups()[6] == 0
		genderTagMatches.groups()[7] == He
		:type genderTagMatches: list
		"""

		raise NotImplementedError()

	@classmethod
	def GetStandardPronounSets (cls) -> dict:
		"""
		Get this language's standard pronoun sets.
		"""

		raise NotImplementedError()

	@classmethod
	def GetReservedPronounSetIdentifiers (cls) -> list:
		"""
		Get gendered language set identifiers reserved for this language's standard pronoun sets.
		"""

		raise NotImplementedError()

	@classmethod
	def IsHandlingLanguageSTBLFile (cls, stblInstanceHexID: str) -> bool:
		"""
		Get whether or not this STBl file's hexadecimal instance id is for this handler's language file.
		"""

		raise NotImplementedError()

	@classmethod
	def GetPackLocalizationPackageFilePaths (cls, pack: Sims4Common.Pack) -> typing.List[str]:
		"""
		Get the handling language's localization package file paths for this pack.
		"""

		raise NotImplementedError()

	@classmethod
	def GetCustomPronounSetEditableGenderTagPairs (cls) -> typing.List[str]:
		"""
		Get a list of gender tag pairs that are editable when creating a custom pronoun set.
		"""

		raise NotImplementedError()

	@classmethod
	def GetCustomPronounSetStandardValues (cls) -> typing.Dict[str, str]:
		"""
		Get the standard values that custom pronoun sets should have.
		"""

		raise NotImplementedError()

	@classmethod
	def GetMoneyString (cls, moneyAmount: numbers.Number) -> str:
		"""
		Add the simoleon symbol to this money amount. This should return something like "§52".
		"""

		raise NotImplementedError()

	@classmethod
	def GetSimFullNameString (cls, simFirstName: str, simLastName: str) -> str:
		"""
		Assemble a sim's full name from their first and last name. A sim's last name can some times be empty.
		"""

		raise NotImplementedError()

	"""


	"""
	@classmethod
	def AskToApplyAndFixCustomPronounSetPair (cls, modifyingSet: dict, modifyingPairIdentifier: str, chosenPairValue: str, callback: typing.Callable[[bool], None]) -> None:
		"""
		Show a dialog asking to do an appropriate fix to a custom pronoun set's pair value. If the user allows the fix, this function should also apply the
		fix by modifying the 'modifyingSet' parameter. The callback parameter should be always called regardless of what the player chooses and should take a
		single argument, true if a fix was applied and false if not.
		"""

		pass

class _Announcer(Director.Announcer):
	_onLoadingScreenAnimationFinished = False
	@classmethod
	def OnLoadingScreenAnimationFinished(cls, zoneReference) -> None:
		if cls._onLoadingScreenAnimationFinished:
			return

		if GetCurrentLanguageHandler() is None:
			_ShowInvalidLanguageNotification()

		cls._onLoadingScreenAnimationFinished = True

def GetCurrentLanguageHandler () -> typing.Optional[LanguageHandlerBase]:
	"""
	Get the game's current language's handler. This will raise an exception if the client manager does not yet exist. This will return none if the current
	language is not supported.
	"""

	if game_services.service_manager is None or game_services.service_manager.client_manager is None:
		raise Exception("Cannot retrieve the current language as the client manager does not yet exist.")

	firstClient = game_services.service_manager.client_manager.get_first_client()  # type: client.Client

	if firstClient is None:
		raise Exception("Tried to get the current language, but we cannot retrieve it right now.")

	gameLocal = services.get_locale()  # type: str
	gameLocalLower = gameLocal.lower()

	try:
		for languageHandler in _registeredLanguageHandlers:  # type: LanguageHandlerBase
			if languageHandler.GameIdentifier.lower() == gameLocalLower:
				return languageHandler
	except KeyError:
		Debug.Log("Current language is unsupported '%s'." % gameLocal, This.Mod.Namespace, Debug.LogLevels.Warning, group = This.Mod.Namespace, owner = __name__, lockIdentifier = __name__ + ":" + str(Python.GetLineNumber()), lockThreshold = 1)
		return None

	return None

def RegisterLanguageHandler (languageHandler: typing.Type[LanguageHandlerBase]) -> None:
	if not isinstance(languageHandler, type):
		raise Exceptions.IncorrectTypeException(languageHandler, "languageHandler", (type,))

	if isinstance(languageHandler, LanguageHandlerBase):
		raise Exceptions.DoesNotInheritException("languageHandler", (LanguageHandlerBase,))

	_registeredLanguageHandlers.append(languageHandler)

def _ShowInvalidLanguageNotification () -> None:
	notificationArguments = {
		"title": InvalidLanguageNotificationTitle.GetCallableLocalizationString(),
		"text": InvalidLanguageNotificationText.GetCallableLocalizationString(),
		"expand_behavior": ui_dialog_notification.UiDialogNotification.UiDialogNotificationExpandBehavior.FORCE_EXPAND,
		"urgency": ui_dialog_notification.UiDialogNotification.UiDialogNotificationUrgency.URGENT
	}

	Notifications.ShowNotification(**notificationArguments)

NoLocalizationPackagePacks = {
	Sims4Common.Pack.FP01
}  # type: typing.Set[Sims4Common.Pack]

InvalidLanguageNotificationTitle = MainLanguage.String(This.Mod.Namespace + ".Invalid_Language_Notification.Title")  # type: MainLanguage.String
InvalidLanguageNotificationText = MainLanguage.String(This.Mod.Namespace + ".Invalid_Language_Notification.Text")  # type: MainLanguage.String

_registeredLanguageHandlers = list()  # type: typing.List[typing.Type[LanguageHandlerBase]]

