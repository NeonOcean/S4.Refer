from __future__ import annotations

import types
import typing

from NeonOcean.S4.Main.Tools import Events
from NeonOcean.S4.Refer.Settings import Base as SettingsBase, Dialogs as SettingsDialogs, Types as SettingsTypes

class CustomPronounSets(SettingsTypes.CustomPronounSetsDialogSetting):
	IsSetting = True  # type: bool

	Key = "Custom_Pronoun_Sets"  # type: str
	Default = dict()  # type: dict

def GetSettingsFilePath () -> str:
	return SettingsBase.SettingsFilePath

def GetAllSettings () -> typing.List[typing.Type[SettingsBase.Setting]]:
	return list(SettingsBase.AllSettings)

def Load () -> None:
	SettingsBase.Load()

def Save () -> None:
	SettingsBase.Save()

def Update () -> None:
	SettingsBase.Update()

def RegisterOnUpdateCallback (updateCallback: typing.Callable[[types.ModuleType, SettingsBase.UpdateEventArguments], None]) -> None:
	SettingsBase.RegisterOnUpdateCallback(updateCallback)

def UnregisterOnUpdateCallback (updateCallback: typing.Callable[[types.ModuleType, SettingsBase.UpdateEventArguments], None]) -> None:
	SettingsBase.UnregisterOnUpdateCallback(updateCallback)

def RegisterOnLoadCallback (loadCallback: typing.Callable[[types.ModuleType, Events.EventArguments], None]) -> None:
	SettingsBase.RegisterOnLoadCallback(loadCallback)

def UnregisterOnLoadCallback (loadCallback: typing.Callable[[types.ModuleType, Events.EventArguments], None]) -> None:
	SettingsBase.UnregisterOnLoadCallback(loadCallback)
