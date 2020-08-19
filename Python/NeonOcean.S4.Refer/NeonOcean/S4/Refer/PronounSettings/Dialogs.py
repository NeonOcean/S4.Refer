from __future__ import annotations

import typing

from NeonOcean.S4.Main import Language, Websites
from NeonOcean.S4.Main.UI import Settings as UISettings, SettingsShared as UISettingsShared
from NeonOcean.S4.Refer import This, PronounSets, LanguageHandlers
from NeonOcean.S4.Refer.UI import Resources as ReferUIResources
from sims4 import localization, resources
from ui import ui_dialog

class PronounSetSelectionDialog(UISettings.DictionaryDialog):
	HostNamespace = This.Mod.Namespace  # type: str
	HostName = This.Mod.Name  # type: str

	def _GetDescriptionSettingText (self, setting: UISettingsShared.SettingStandardWrapper) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Pronoun_Settings.Values." + setting.Key + ".Description")

	def _GetDescriptionDocumentationURL (self, setting: UISettingsShared.SettingStandardWrapper) -> typing.Optional[str]:
		return Websites.GetNODocumentationModSettingURL(setting.Setting, This.Mod)

	def _GetDefaultRowText (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Pronoun_Set_Selection.Default", fallbackText = "Default")

	def _GetFemaleRowText (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Pronoun_Set_Selection.Female", fallbackText = "Female")

	def _GetMaleRowText (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Pronoun_Set_Selection.Male", fallbackText = "Male")

	def _GetSelectedRowDescription (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Pronoun_Set_Selection.Dialog.Selected_Row_Description", fallbackText = "Selected_Row_Description")

	def _GetNotSelectedRowDescription (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Pronoun_Set_Selection.Dialog.Not_Selected_Row_Description", fallbackText = "Not_Selected_Row_Description")

	def _GetSelectedRowIcon (self) -> typing.Any:
		return resources.ResourceKeyWrapper(ReferUIResources.PickerCheckIconKey)

	def _GetNotSelectedRowIcon (self) -> typing.Any:
		return resources.ResourceKeyWrapper(ReferUIResources.PickerBlankIconKey)

	def _CreateRows (self,
					 setting: UISettingsShared.SettingWrapper,
					 currentValue: typing.Any,
					 showDialogArguments: typing.Dict[str, typing.Any],
					 returnCallback: typing.Callable[[], None] = None,
					 *args, **kwargs) -> typing.List[UISettings.DialogRow]:

		rows = super()._CreateRows(setting, currentValue, showDialogArguments, returnCallback = returnCallback, *args, **kwargs)  # type: typing.List[UISettings.DialogRow]

		currentLanguageHandler = LanguageHandlers.GetCurrentLanguageHandler()  # type: typing.Optional[typing.Type[LanguageHandlers.LanguageHandlerBase]]

		def _createSelectionCallback (rowValue: str) -> typing.Callable:
			# noinspection PyUnusedLocal
			def selectionCallback (dialog: ui_dialog.UiDialog) -> None:
				self._ShowDialogInternal(setting, rowValue, showDialogArguments, returnCallback = returnCallback)

			return selectionCallback

		defaultSelectionValue = ""  # type: str
		defaultRowSelected = True if currentValue == defaultSelectionValue else False  # type: bool
		defaultRow = UISettings.DialogRow(
			10,
			_createSelectionCallback(defaultSelectionValue),
			self._GetDefaultRowText(),
			description = self._GetSelectedRowDescription() if defaultRowSelected else self._GetNotSelectedRowDescription(),
			icon = self._GetSelectedRowIcon() if defaultRowSelected else self._GetNotSelectedRowIcon(),
		)

		femaleSelectionValue = "0"  # type: str
		femaleRowSelected = True if currentValue == femaleSelectionValue else False  # type: bool
		femaleRow = UISettings.DialogRow(
			11,
			_createSelectionCallback(femaleSelectionValue),
			self._GetFemaleRowText(),
			description = self._GetSelectedRowDescription() if femaleRowSelected else self._GetNotSelectedRowDescription(),
			icon = self._GetSelectedRowIcon() if femaleRowSelected else self._GetNotSelectedRowIcon(),
		)

		maleSelectionValue = "1"  # type: str
		maleRowSelected = True if currentValue == maleSelectionValue else False  # type: bool
		maleRow = UISettings.DialogRow(
			12,
			_createSelectionCallback(maleSelectionValue),
			self._GetMaleRowText(),
			description = self._GetSelectedRowDescription() if maleRowSelected else self._GetNotSelectedRowDescription(),
			icon = self._GetSelectedRowIcon() if maleRowSelected else self._GetNotSelectedRowIcon(),
		)

		rows.append(defaultRow)
		rows.append(femaleRow)
		rows.append(maleRow)

		currentAdditionalSetOptionID = 100  # type: int

		for pronounSetIdentifier, pronounSet in PronounSets.GetAllPronounSets(currentLanguageHandler).items():
			pronounSetTitle = pronounSet.get("Title", None)  # type: typing.Optional[str]

			if pronounSetTitle is None:
				continue

			pronounSetSelected = True if currentValue == pronounSetIdentifier else False  # type: bool
			pronounSetRow = UISettings.DialogRow(
				currentAdditionalSetOptionID,
				_createSelectionCallback(pronounSetIdentifier),
				Language.CreateLocalizationString(pronounSetTitle),
				description = self._GetSelectedRowDescription() if pronounSetSelected else self._GetNotSelectedRowDescription(),
				icon = self._GetSelectedRowIcon() if pronounSetSelected else self._GetNotSelectedRowIcon(),
			)

			currentAdditionalSetOptionID += 1

			rows.append(pronounSetRow)


		return rows

class PronounFallbackDialog(UISettings.DictionaryDialog):
	HostNamespace = This.Mod.Namespace  # type: str
	HostName = This.Mod.Name  # type: str

	def _GetDescriptionSettingText (self, setting: UISettingsShared.SettingStandardWrapper) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Pronoun_Settings.Values." + setting.Key + ".Description")

	def _GetDescriptionDocumentationURL (self, setting: UISettingsShared.SettingStandardWrapper) -> typing.Optional[str]:
		return Websites.GetNODocumentationModSettingURL(setting.Setting, This.Mod)

	def _GetDefaultRowText (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Pronoun_Fallback.Default", fallbackText = "Default")

	def _GetFemaleRowText (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Pronoun_Fallback.Female", fallbackText = "Female")

	def _GetMaleRowText (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Pronoun_Fallback.Male", fallbackText = "Male")

	def _GetSelectedRowDescription (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Pronoun_Fallback.Dialog.Selected_Row_Description", fallbackText = "Selected_Row_Description")

	def _GetNotSelectedRowDescription (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Pronoun_Fallback.Dialog.Not_Selected_Row_Description", fallbackText = "Not_Selected_Row_Description")

	def _GetSelectedRowIcon (self) -> typing.Any:
		return resources.ResourceKeyWrapper(ReferUIResources.PickerCheckIconKey)

	def _GetNotSelectedRowIcon (self) -> typing.Any:
		return resources.ResourceKeyWrapper(ReferUIResources.PickerBlankIconKey)

	def _CreateRows (self,
					 setting: UISettingsShared.SettingWrapper,
					 currentValue: typing.Any,
					 showDialogArguments: typing.Dict[str, typing.Any],
					 returnCallback: typing.Callable[[], None] = None,
					 *args, **kwargs) -> typing.List[UISettings.DialogRow]:

		rows = super()._CreateRows(setting, currentValue, showDialogArguments, returnCallback = returnCallback, *args, **kwargs)  # type: typing.List[UISettings.DialogRow]

		def _createSelectionCallback (rowValue: str) -> typing.Callable:
			# noinspection PyUnusedLocal
			def selectionCallback (dialog: ui_dialog.UiDialog) -> None:
				self._ShowDialogInternal(setting, rowValue, showDialogArguments, returnCallback = returnCallback)

			return selectionCallback

		defaultSelectionValue = ""  # type: str
		defaultRowSelected = True if currentValue == defaultSelectionValue else False  # type: bool
		defaultRow = UISettings.DialogRow(
			10,
			_createSelectionCallback(defaultSelectionValue),
			self._GetDefaultRowText(),
			description = self._GetSelectedRowDescription() if defaultRowSelected else self._GetNotSelectedRowDescription(),
			icon = self._GetSelectedRowIcon() if defaultRowSelected else self._GetNotSelectedRowIcon(),
		)

		femaleSelectionValue = "0"  # type: str
		femaleRowSelected = True if currentValue == femaleSelectionValue else False  # type: bool
		femaleRow = UISettings.DialogRow(
			11,
			_createSelectionCallback(femaleSelectionValue),
			self._GetFemaleRowText(),
			description = self._GetSelectedRowDescription() if femaleRowSelected else self._GetNotSelectedRowDescription(),
			icon = self._GetSelectedRowIcon() if femaleRowSelected else self._GetNotSelectedRowIcon(),
		)

		maleSelectionValue = "1"  # type: str
		maleRowSelected = True if currentValue == maleSelectionValue else False  # type: bool
		maleRow = UISettings.DialogRow(
			12,
			_createSelectionCallback(maleSelectionValue),
			self._GetMaleRowText(),
			description = self._GetSelectedRowDescription() if maleRowSelected else self._GetNotSelectedRowDescription(),
			icon = self._GetSelectedRowIcon() if maleRowSelected else self._GetNotSelectedRowIcon(),
		)

		rows.append(defaultRow)
		rows.append(femaleRow)
		rows.append(maleRow)

		return rows
