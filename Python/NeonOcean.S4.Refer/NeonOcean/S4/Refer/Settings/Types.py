from __future__ import annotations

from NeonOcean.S4.Main import Language
from NeonOcean.S4.Main.Tools import Exceptions, Version
from NeonOcean.S4.Refer.Settings import Base as SettingsBase, Dialogs as SettingsDialogs
from sims4 import localization

class CustomPronounSetsSetting(SettingsBase.Setting):
	Type = dict

	@classmethod
	def Verify (cls, value: dict, lastChangeVersion: Version.Version = None) -> dict:
		if not isinstance(value, dict):
			raise Exceptions.IncorrectTypeException(value, "value", (dict,))

		if not isinstance(lastChangeVersion, Version.Version) and lastChangeVersion is not None:
			raise Exceptions.IncorrectTypeException(lastChangeVersion, "lastChangeVersion", (Version.Version, "None"))

		return value

	@classmethod
	def GetValueText (cls, value: dict) -> localization.LocalizedString:
		if not isinstance(value, dict):
			raise Exceptions.IncorrectTypeException(value, "value", (dict,))

		return Language.CreateLocalizationString("")

class CustomPronounSetsDialogSetting(CustomPronounSetsSetting):
	Dialog = SettingsDialogs.CustomPronounSetsDialog
