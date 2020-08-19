from __future__ import annotations

import typing

from NeonOcean.S4.Main.Tools import Exceptions, Version
from NeonOcean.S4.Main import Language
from NeonOcean.S4.Refer.PronounSettings import Base as SettingsBase, Dialogs as SettingsDialogs
from NeonOcean.S4.Refer import PronounSets, LanguageHandlers, This

from sims4 import localization

class PronounSetSelectionSetting(SettingsBase.Setting):
	Type = str

	@classmethod
	def Verify (cls, value: str, lastChangeVersion: Version.Version = None) -> str:
		if not isinstance(value, str):
			raise Exceptions.IncorrectTypeException(value, "value", (str,))

		if not isinstance(lastChangeVersion, Version.Version) and lastChangeVersion is not None:
			raise Exceptions.IncorrectTypeException(lastChangeVersion, "lastChangeVersion", (Version.Version, "None"))

		return value

	@classmethod
	def GetDefaultText (cls) -> localization.LocalizedString:
		return cls.GetValueText(cls.Default)

	@classmethod
	def GetValueText(cls, value: str) -> localization.LocalizedString:
		if value == "":
			return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Pronoun_Set_Selection.Default", fallbackText = "Pronoun_Set_Selection.Default")
		elif value == "0":
			return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Pronoun_Set_Selection.Female", fallbackText = "Pronoun_Set_Selection.Female")
		elif value == "1":
			return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Pronoun_Set_Selection.Male", fallbackText = "Pronoun_Set_Selection.Male")

		currentLanguageHandler = LanguageHandlers.GetCurrentLanguageHandler()  # type: typing.Optional[LanguageHandlers.LanguageHandlerBase]
		allPronounSets = PronounSets.GetAllPronounSets(currentLanguageHandler)  # type: dict

		selectedPronounSet = allPronounSets.get(value, None)  # type: dict

		if selectedPronounSet is None:
			return Language.CreateLocalizationString("")

		selectedPronounSetTitle = selectedPronounSet.get("Title", None)  # type: str

		if selectedPronounSetTitle is None:
			return Language.CreateLocalizationString("")

		return Language.CreateLocalizationString(selectedPronounSetTitle)

class PronounSetSelectionDialogSetting(PronounSetSelectionSetting):
	Dialog = SettingsDialogs.PronounSetSelectionDialog

class PronounFallbackSetting(SettingsBase.Setting):
	Type = str

	@classmethod
	def Verify (cls, value: str, lastChangeVersion: Version.Version = None) -> str:
		if not isinstance(value, str):
			raise Exceptions.IncorrectTypeException(value, "value", (str,))

		if not isinstance(lastChangeVersion, Version.Version) and lastChangeVersion is not None:
			raise Exceptions.IncorrectTypeException(lastChangeVersion, "lastChangeVersion", (Version.Version, "None"))

		validValues = {
			"",
			"0",
			"1"
		}  # type: typing.Set[str]

		if not value in validValues:
			raise ValueError("'%s' is not a valid gendered language fallback." % value)

		return value

	@classmethod
	def GetDefaultText (cls) -> localization.LocalizedString:
		return cls.GetValueText(cls.Default)

	@classmethod
	def GetValueText(cls, value: str) -> localization.LocalizedString:
		if value == "":
			return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Pronoun_Fallback.Default", fallbackText = "Pronoun_Fallback.Default")
		elif value == "0":
			return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Pronoun_Fallback.Female", fallbackText = "Pronoun_Fallback.Female")
		elif value == "1":
			return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Pronoun_Fallback.Male", fallbackText = "Pronoun_Fallback.Male")

		return Language.CreateLocalizationString("")

class PronounFallbackDialogSetting(PronounFallbackSetting):
	Dialog = SettingsDialogs.PronounFallbackDialog