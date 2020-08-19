from __future__ import annotations, annotations

import types
import typing

from NeonOcean.S4.Main.Tools import Events, Exceptions
from NeonOcean.S4.Refer.PronounSettings import Base as SimSettingsBase, Types as SettingsTypes

class PronounSetSelection(SettingsTypes.PronounSetSelectionDialogSetting):
	IsSetting = True  # type: bool

	Key = "Pronoun_Set_Selection"  # type: str
	Default = ""  # type: str

class PronounFallback(SettingsTypes.PronounFallbackDialogSetting):
	IsSetting = True  # type: bool

	Key = "Pronoun_Fallback"  # type: str
	Default = ""  # type: str

	@classmethod
	def IsHidden (cls, simID: str) -> bool:
		if not isinstance(simID, str):
			raise Exceptions.IncorrectTypeException(simID, "simID", (str,))

		hiddenSetSelectionValues = {
			"",
			"0",
			"1"
		}  # type: typing.Set[str]

		return PronounSetSelection.Get(simID) in hiddenSetSelectionValues

	ListPriority = -10

def GetAllSettings () -> typing.List[typing.Type[SimSettingsBase.Setting]]:
	return SimSettingsBase.GetAllSettings()

def Update () -> None:
	SimSettingsBase.Update()

def RegisterOnUpdateCallback (updateCallback: typing.Callable[[types.ModuleType, SimSettingsBase.UpdateEventArguments], None]) -> None:
	SimSettingsBase.RegisterOnUpdateCallback(updateCallback)

def UnregisterOnUpdateCallback (updateCallback: typing.Callable[[types.ModuleType, SimSettingsBase.UpdateEventArguments], None]) -> None:
	SimSettingsBase.UnregisterOnUpdateCallback(updateCallback)

def RegisterOnLoadCallback (loadCallback: typing.Callable[[types.ModuleType, Events.EventArguments], None]) -> None:
	SimSettingsBase.RegisterOnLoadCallback(loadCallback)

def UnregisterOnLoadCallback (loadCallback: typing.Callable[[types.ModuleType, Events.EventArguments], None]) -> None:
	SimSettingsBase.UnregisterOnLoadCallback(loadCallback)
