from __future__ import annotations

import typing

from NeonOcean.S4.Main import Language, This, Websites
from NeonOcean.S4.Main.UI import Settings as UISettings, SettingsShared as UISettingsShared
from NeonOcean.S4.Refer import PronounSets, This
from NeonOcean.S4.Refer.UI import Resources as ReferUIResources
from sims4 import localization, resources
from ui import ui_dialog

class CustomPronounSetsDialog(UISettings.DictionaryDialog):
	HostNamespace = This.Mod.Namespace  # type: str
	HostName = This.Mod.Name  # type: str

	def _GetDescriptionSettingText (self, setting: UISettingsShared.SettingStandardWrapper) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Pronoun_Settings.Values." + setting.Key + ".Description")

	def _GetDescriptionDocumentationURL (self, setting: UISettingsShared.SettingStandardWrapper) -> typing.Optional[str]:
		return Websites.GetNODocumentationModSettingURL(setting.Setting, This.Mod)

	def _GetCustomSetRowDescription (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Dialog.Custom_Set_Row_Description", fallbackText = "Selected_Row_Description")

	def _GetNewSetRowText (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Dialog.New_Set_Row_Text", fallbackText = "New_Set_Row_Text")

	def _GetNewSetRowDescription (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Dialog.New_Set_Row_Description", fallbackText = "New_Set_Row_Description")

	def _GetCustomSetRowIcon (self) -> localization.LocalizedString:
		return resources.ResourceKeyWrapper(ReferUIResources.PickerPlusIconKey)

	def _GetNewSetRowIcon (self) -> typing.Any:
		return resources.ResourceKeyWrapper(ReferUIResources.PickerPlusIconKey)

	def _CreateRows (self,
					 setting: UISettingsShared.SettingWrapper,
					 currentValue: typing.Any,
					 showDialogArguments: typing.Dict[str, typing.Any],
					 returnCallback: typing.Callable[[], None] = None,
					 *args, **kwargs) -> typing.List[UISettings.DialogRow]:

		rows = super()._CreateRows(setting, currentValue, showDialogArguments, returnCallback = returnCallback, *args, **kwargs)  # type: typing.List[UISettings.DialogRow]

		def createNewSetCallback () -> typing.Callable:
			# noinspection PyUnusedLocal
			def selectionCallback (dialog: ui_dialog.UiDialog) -> None:
				pass  # TODO

			# self._ShowDialogInternal(setting, rowValue, showDialogArguments, returnCallback = returnCallback)

			return selectionCallback

		def createSetCallback (rowValue: str) -> typing.Callable:
			# noinspection PyUnusedLocal
			def selectionCallback (dialog: ui_dialog.UiDialog) -> None:
				self._ShowDialogInternal(setting, rowValue, showDialogArguments, returnCallback = returnCallback)

			return selectionCallback

		newSetRow = UISettings.DialogRow(
			10,
			createNewSetCallback(),
			self._GetNewSetRowText(),
			description = self._GetNewSetRowDescription(),
			icon = self._GetNewSetRowIcon(),
		)

		rows.append(newSetRow)

		currentAdditionalSetOptionID = 100  # type: int

		for pronounSetIdentifier, pronounSet in PronounSets.GetCustomPronounSets().items():
			pronounSetTitle = pronounSet.get("Title", None)  # type: typing.Optional[str]

			if pronounSetTitle is None:
				continue

			pronounSetRow = UISettings.DialogRow(
				currentAdditionalSetOptionID,
				createSetCallback(pronounSetIdentifier),
				Language.CreateLocalizationString(pronounSetTitle),
				description = self._GetCustomSetRowDescription(),
				icon = self._GetCustomSetRowIcon(),
			)

			currentAdditionalSetOptionID += 1

			rows.append(pronounSetRow)

		return rows
