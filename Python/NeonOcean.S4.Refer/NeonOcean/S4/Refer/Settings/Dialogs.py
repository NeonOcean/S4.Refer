from __future__ import annotations

import typing
import uuid

from NeonOcean.S4.Main import Debug, Language, This
from NeonOcean.S4.Main.UI import Dialogs as UIDialogs, Settings as UISettings, SettingsShared as UISettingsShared
from NeonOcean.S4.Refer import LanguageHandlers, PronounSets, This
from NeonOcean.S4.Refer.UI import Resources as ReferUIResources
from sims4 import collections, localization, resources
from ui import ui_dialog, ui_dialog_generic, ui_text_input

class CustomPronounSetsDialog(UISettings.DictionaryDialog):
	HostNamespace = This.Mod.Namespace  # type: str
	HostName = This.Mod.Name  # type: str

	def _GetDescriptionText (self, setting: UISettingsShared.SettingWrapper) -> localization.LocalizedString:
		return Language.CreateLocalizationString("")

	def _GetCustomSetRowDescription (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Dialog.Custom_Set_Row_Description", fallbackText = "Custom_Set_Row_Description")

	def _GetNewSetRowText (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Dialog.New_Set_Row_Text", fallbackText = "New_Set_Row_Text")

	def _GetNewSetRowDescription (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Dialog.New_Set_Row_Description", fallbackText = "New_Set_Row_Description")

	def _GetCustomSetRowIcon (self) -> localization.LocalizedString:
		return resources.ResourceKeyWrapper(ReferUIResources.PickerPencilIconKey)

	def _GetNewSetRowIcon (self) -> typing.Any:
		return resources.ResourceKeyWrapper(ReferUIResources.PickerPlusIconKey)

	def _CreateRows (self,
					 setting: UISettingsShared.SettingWrapper,
					 currentValue: typing.Any,
					 showDialogArguments: typing.Dict[str, typing.Any],
					 returnCallback: typing.Callable[[], None] = None,
					 *args, **kwargs) -> typing.List[UISettings.DialogRow]:

		rows = super()._CreateRows(setting, currentValue, showDialogArguments, returnCallback = returnCallback, *args, **kwargs)  # type: typing.List[UISettings.DialogRow]

		currentLanguageHandler = LanguageHandlers.GetCurrentLanguageHandler()  # type: LanguageHandlers.LanguageHandlerBase

		def generateNewValidSetID () -> str:
			newSetID = uuid.uuid4()  # type: uuid.UUID
			newSetIDString = str(newSetID)  # type: str

			if not newSetIDString in currentValue:
				return newSetIDString
			else:
				return generateNewValidSetID()

		def createNewSetCallback () -> typing.Callable:
			# noinspection PyUnusedLocal
			def selectionCallback (dialog: ui_dialog.UiDialog) -> None:
				newSetIDString = generateNewValidSetID()

				newPronounSetSet = currentLanguageHandler.GetCustomPronounSetStandardValues()  # type: typing.Dict[str, str]

				currentValue[newSetIDString] = {
					"Title": "New Pronoun Set",
					"Set": newPronounSetSet
				}

				setting.Set(currentValue)

				self._ShowDialogInternal(setting, currentValue, showDialogArguments, returnCallback = returnCallback)

			return selectionCallback

		def editSetCallback (editingPronounSetIdentifier: str) -> typing.Callable:
			# noinspection PyUnusedLocal
			def editPronounSetCallback () -> None:
				self.ShowDialog(setting, returnCallback = returnCallback, **showDialogArguments)

			# noinspection PyUnusedLocal
			def selectionCallback (dialog: ui_dialog.UiDialog) -> None:
				if hasattr(setting.Setting, "EditPronounSetDialog"):
					setting.Setting.EditPronounSetDialog().ShowDialog(setting, editPronounSetCallback, editingPronounSetIdentifier = editingPronounSetIdentifier)
				else:
					Debug.Log("Cannot edit pronoun set as the custom pronoun set setting has no EditPronounSetDialog attribute.", This.Mod.Namespace, Debug.LogLevels.Warning, group = This.Mod.Namespace, owner = __name__)
					self._ShowDialogInternal(setting, currentValue, showDialogArguments, returnCallback = returnCallback)

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
				editSetCallback(pronounSetIdentifier),
				Language.CreateLocalizationString(pronounSetTitle),
				description = self._GetCustomSetRowDescription(),
				icon = self._GetCustomSetRowIcon(),
			)

			currentAdditionalSetOptionID += 1

			rows.append(pronounSetRow)

		return rows

class EditPronounSetDialog(UISettings.DictionaryDialog):
	HostNamespace = This.Mod.Namespace  # type: str
	HostName = This.Mod.Name  # type: str

	def _GetDescriptionText (self, setting: UISettingsShared.SettingWrapper) -> localization.LocalizedString:
		return Language.CreateLocalizationString("")

	def _GetDeleteSetRowText (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Edit_Pronoun_Set_Dialog.Delete_Set_Row.Text", fallbackText = "Delete_Set_Row.Text")

	def _GetDeleteSetRowDescription (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Edit_Pronoun_Set_Dialog.Delete_Set_Row.Description", fallbackText = "Delete_Set_Row.Description")

	def _GetEditTitleRowText (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Edit_Pronoun_Set_Dialog.Edit_Title_Row.Text", fallbackText = "Edit_Title_Row.Text")

	def _GetEditablePairSpecialAlternativeText (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Edit_Pronoun_Set_Dialog.Editable_Pair_Row.Special_Alternative", fallbackText = "Editable_Pair_Row.Special_Alternative")

	def _GetDeleteSetRowIcon (self) -> localization.LocalizedString:
		return resources.ResourceKeyWrapper(ReferUIResources.PickerTrashCanIconKey)

	def _GetEditTitleRowIcon (self) -> localization.LocalizedString:
		return resources.ResourceKeyWrapper(ReferUIResources.PickerPencilIconKey)

	def _GetEditablePairRowIcon (self) -> localization.LocalizedString:
		return resources.ResourceKeyWrapper(ReferUIResources.PickerTextIconKey)

	def _GetEditTitleDialogTitle (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Edit_Title_Dialog.Title", fallbackText = "Edit_Title_Dialog.Title")

	def _GetEditTitleDialogText (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Edit_Title_Dialog.Text", fallbackText = "Edit_Title_Dialog.Text")

	def _GetEditTitleDialogOkButton (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Edit_Title_Dialog.Ok_Button", fallbackText = "Edit_Title_Dialog.Ok_Button")

	def _GetEditTitleDialogCancelButton (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Edit_Title_Dialog.Cancel_Button", fallbackText = "Edit_Title_Dialog.Cancel_Button")

	def _GetDeleteSetConfirmDialogTitle (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Delete_Set_Confirm_Dialog.Title", fallbackText = "Delete_Set_Confirm_Dialog.Title")

	def _GetDeleteSetConfirmDialogText (self, deletingSetTitle: str) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Delete_Set_Confirm_Dialog.Text", deletingSetTitle, fallbackText = "Delete_Set_Confirm_Dialog.Text")

	def _GetDeleteSetConfirmDialogOkButton (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Delete_Set_Confirm_Dialog.Ok_Button", fallbackText = "Delete_Set_Confirm_Dialog.Ok_Button")

	def _GetDeleteSetConfirmDialogCancelButton (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Delete_Set_Confirm_Dialog.Cancel_Button", fallbackText = "Delete_Set_Confirm_Dialog.Cancel_Button")

	def _GetEditPairDialogTitle (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Edit_Pair_Dialog.Title", fallbackText = "Edit_Pair_Dialog.Title")

	def _GetEditPairDialogText (self, femaleLanguage: str, maleLanguage: str) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Edit_Pair_Dialog.Text", femaleLanguage, maleLanguage, fallbackText = "Edit_Pair_Dialog.Text")

	def _GetEditPairDialogOkButton (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Edit_Pair_Dialog.Ok_Button", fallbackText = "Edit_Pair_Dialog.Ok_Button")

	def _GetEditPairDialogCancelButton (self) -> localization.LocalizedString:
		return Language.GetLocalizationStringByIdentifier(This.Mod.Namespace + ".Settings.Types.Custom_Pronoun_Sets.Edit_Pair_Dialog.Cancel_Button", fallbackText = "Edit_Pair_Dialog.Cancel_Button")

	def _ShowDeleteSetConfirmDialog (self,
									 editingSetTitle: str,
									 setting: UISettingsShared.SettingWrapper,
									 currentValue: typing.Any,
									 showDialogArguments: typing.Dict[str, typing.Any],
									 returnCallback: typing.Callable[[], None] = None,
									 *args, **kwargs) -> None:

		editingPronounSetIdentifier = showDialogArguments["editingPronounSetIdentifier"]  # type: str

		def deleteSetConfirmDialog (shownDeleteSetConfirmDialog: ui_dialog_generic.UiDialogTextInputOkCancel) -> None:
			if shownDeleteSetConfirmDialog.accepted:
				currentValue.pop(editingPronounSetIdentifier, None)

				setting.Set(currentValue)

				if returnCallback is not None:
					returnCallback()
			else:
				self._ShowDialogInternal(setting, currentValue, showDialogArguments = showDialogArguments, returnCallback = returnCallback, *args, **kwargs)

		dialogArguments = {
			"title": Language.MakeLocalizationStringCallable(self._GetDeleteSetConfirmDialogTitle()),
			"text": Language.MakeLocalizationStringCallable(self._GetDeleteSetConfirmDialogText(editingSetTitle)),
			"text_ok": Language.MakeLocalizationStringCallable(self._GetDeleteSetConfirmDialogOkButton()),
			"text_cancel": Language.MakeLocalizationStringCallable(self._GetDeleteSetConfirmDialogCancelButton()),
		}

		UIDialogs.ShowOkCancelDialog(callback = deleteSetConfirmDialog, queue = False, **dialogArguments)

	def _ShowEditTitleDialog (self,
							  editingPronounSetContainer: dict,
							  setting: UISettingsShared.SettingWrapper,
							  currentValue: typing.Any,
							  showDialogArguments: typing.Dict[str, typing.Any],
							  returnCallback: typing.Callable[[], None] = None,
							  *args, **kwargs) -> None:

		def editPairDialogCallback (shownEditPairDialog: ui_dialog_generic.UiDialogTextInputOkCancel) -> None:
			if shownEditPairDialog.accepted:
				editingSetNextTitle = shownEditPairDialog.text_input_responses.get(textInputKey, editingSetCurrentTitle)  # type: str
				editingPronounSetContainer["Title"] = editingSetNextTitle

			self._ShowDialogInternal(setting, currentValue, showDialogArguments = showDialogArguments, returnCallback = returnCallback, *args, **kwargs)

		editingSetCurrentTitle = editingPronounSetContainer.get("Title", "New Pronoun Set")  # type: str

		textInputKey = "Input"  # type: str

		textInputLockedArguments = {
			"sort_order": 0,
		}

		textInput = ui_text_input.UiTextInput.TunableFactory(locked_args = textInputLockedArguments).default  # type: ui_text_input.UiTextInput
		textInputInitialValue = Language.MakeLocalizationStringCallable(Language.CreateLocalizationString(editingSetCurrentTitle))

		textInput.initial_value = textInputInitialValue

		textInputs = collections.make_immutable_slots_class([textInputKey])
		textInputs = textInputs({
			textInputKey: textInput
		})

		dialogArguments = {
			"title": Language.MakeLocalizationStringCallable(self._GetEditTitleDialogTitle()),
			"text": Language.MakeLocalizationStringCallable(self._GetEditTitleDialogText()),
			"text_ok": Language.MakeLocalizationStringCallable(self._GetEditTitleDialogOkButton()),
			"text_cancel": Language.MakeLocalizationStringCallable(self._GetEditTitleDialogCancelButton()),
			"text_inputs": textInputs
		}

		UIDialogs.ShowOkCancelInputDialog(callback = editPairDialogCallback, queue = False, **dialogArguments)

	def _ShowEditPairDialog (self,
							 editingPronounSet: dict,
							 editingPairIdentifier: str,
							 editingPairCurrentValue: str,
							 setting: UISettingsShared.SettingWrapper,
							 currentValue: typing.Any,
							 showDialogArguments: typing.Dict[str, typing.Any],
							 returnCallback: typing.Callable[[], None] = None,
							 *args, **kwargs) -> None:

		def editPairDialogCallback (shownEditPairDialog: ui_dialog_generic.UiDialogTextInputOkCancel) -> None:
			try:
				if shownEditPairDialog.accepted:
					editingPairNextValue = shownEditPairDialog.text_input_responses.get(textInputKey, editingPairCurrentValue)  # type: str
					editingPairNextValue = editingPairNextValue.lower()
					editingPronounSet[editingPairIdentifier] = editingPairNextValue

					# noinspection PyUnusedLocal
					def askToApplyAndFixCallback (appliedFix: bool) -> None:
						self._ShowDialogInternal(setting, currentValue, showDialogArguments = showDialogArguments, returnCallback = returnCallback, *args, **kwargs)

					currentLanguageHandler = LanguageHandlers.GetCurrentLanguageHandler()  # type: LanguageHandlers.LanguageHandlerBase
					currentLanguageHandler.AskToApplyAndFixCustomPronounSetPair(editingPronounSet, editingPairIdentifier, editingPairNextValue, askToApplyAndFixCallback)
				else:
					self._ShowDialogInternal(setting, currentValue, showDialogArguments = showDialogArguments, returnCallback = returnCallback, *args, **kwargs)
			except:
				Debug.Log("Failed to run an edit pair dialog callback.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)

		editingPairParts = editingPairIdentifier.split("|")  # type: typing.List[str]

		if len(editingPairParts) != 2:
			femaleLanguage = maleLanguage = ""  # type: str
		else:
			femaleLanguage = editingPairParts[0].capitalize()  # type: str
			maleLanguage = editingPairParts[1].capitalize()  # type: str

		textInputKey = "Input"  # type: str

		textInputLockedArguments = {
			"sort_order": 0,
		}

		textInput = ui_text_input.UiTextInput.TunableFactory(locked_args = textInputLockedArguments).default  # type: ui_text_input.UiTextInput
		textInputInitialValue = Language.MakeLocalizationStringCallable(Language.CreateLocalizationString(editingPairCurrentValue.capitalize()))

		textInput.initial_value = textInputInitialValue

		textInputs = collections.make_immutable_slots_class([textInputKey])
		textInputs = textInputs({
			textInputKey: textInput
		})

		dialogArguments = {
			"title": Language.MakeLocalizationStringCallable(self._GetEditPairDialogTitle()),
			"text": Language.MakeLocalizationStringCallable(self._GetEditPairDialogText(femaleLanguage, maleLanguage)),
			"text_ok": Language.MakeLocalizationStringCallable(self._GetEditPairDialogOkButton()),
			"text_cancel": Language.MakeLocalizationStringCallable(self._GetEditPairDialogCancelButton()),
			"text_inputs": textInputs
		}

		UIDialogs.ShowOkCancelInputDialog(callback = editPairDialogCallback, queue = False, **dialogArguments)

	def _CreateRows (self,
					 setting: UISettingsShared.SettingWrapper,
					 currentValue: typing.Any,
					 showDialogArguments: typing.Dict[str, typing.Any],
					 returnCallback: typing.Callable[[], None] = None,
					 *args, **kwargs) -> typing.List[UISettings.DialogRow]:

		rows = super()._CreateRows(setting, currentValue, showDialogArguments, returnCallback = returnCallback, *args, **kwargs)  # type: typing.List[UISettings.DialogRow]

		currentLanguageHandler = LanguageHandlers.GetCurrentLanguageHandler()  # type: LanguageHandlers.LanguageHandlerBase

		editingPronounSetIdentifier = showDialogArguments["editingPronounSetIdentifier"]  # type: str

		editingPronounSetContainer = currentValue.get(editingPronounSetIdentifier, None)

		if editingPronounSetContainer is None:
			editingPronounSet = dict()

			editingPronounSetContainer = {
				"Title": "New Pronoun Set",
				"Set": editingPronounSet
			}

			currentValue[editingPronounSetIdentifier] = editingPronounSetContainer
		else:
			editingPronounSet = editingPronounSetContainer.get("Set", None)

			if editingPronounSet is None:
				editingPronounSet = dict()
				editingPronounSetContainer["Set"] = editingPronounSet

		editingPronounSetTitle = editingPronounSetContainer["Title"]  # type: str

		def createDeleteSetCallback () -> typing.Callable:
			# noinspection PyUnusedLocal
			def deleteSetCallback (dialog: ui_dialog.UiDialog) -> None:
				try:
					self._ShowDeleteSetConfirmDialog(editingPronounSetTitle, setting, currentValue, showDialogArguments, returnCallback = returnCallback, *args, **kwargs)
				except:
					Debug.Log("Failed to run the delete set row callback.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)

			return deleteSetCallback



		def createEditTitleCallback () -> typing.Callable:
			# noinspection PyUnusedLocal
			def editTitleCallback (dialog: ui_dialog.UiDialog) -> None:
				try:
					self._ShowEditTitleDialog(editingPronounSetContainer, setting, currentValue, showDialogArguments = showDialogArguments, returnCallback = returnCallback)
				except:
					Debug.Log("Failed to run the edit title row callback.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)

			return editTitleCallback

		# noinspection PyUnusedLocal
		def createEditPairCallback (editingPairIdentifier: str) -> typing.Callable:
			# noinspection PyUnusedLocal
			def editPairCallback (dialog: ui_dialog.UiDialog) -> None:
				try:
					editingPairValue = editingPronounSet.get(editingPairIdentifier, "")

					if not isinstance(editingPairValue, str):
						editingPairValue = ""

					self._ShowEditPairDialog(editingPronounSet, editingPairIdentifier, editingPairValue, setting, currentValue, showDialogArguments = showDialogArguments, returnCallback = returnCallback)
				except:
					Debug.Log("Failed to run the edit pair row callback.", This.Mod.Namespace, Debug.LogLevels.Exception, group = This.Mod.Namespace, owner = __name__)

			return editPairCallback
		
		deleteSetRow = UISettings.DialogRow(
			4,
			createDeleteSetCallback(),
			self._GetDeleteSetRowText(),
			description = self._GetDeleteSetRowDescription(),
			icon = self._GetDeleteSetRowIcon()
		)

		rows.append(deleteSetRow)
		
		editTitleRow = UISettings.DialogRow(
			5,
			createEditTitleCallback(),
			self._GetEditTitleDialogTitle(),
			description = Language.CreateLocalizationString(editingPronounSetTitle),
			icon = self._GetEditTitleRowIcon(),
		)

		rows.append(editTitleRow)

		currentGenderTagPairOptionID = 100  # type: int

		for editablePairIdentifier in currentLanguageHandler.GetCustomPronounSetEditableGenderTagPairs():  # type: str
			editablePairParts = editablePairIdentifier.split("|")  # type: typing.List[str]

			if len(editablePairParts) != 2:
				continue

			editablePairRowText = editablePairParts[0].capitalize() + " / " + editablePairParts[1].capitalize()  # type: str

			editablePairValue = editingPronounSet.get(editablePairIdentifier, "")

			if isinstance(editablePairValue, str):
				editablePairRowDescription = Language.CreateLocalizationString(editablePairValue.capitalize())  # type: localization.LocalizedString
			else:
				editablePairRowDescription = self._GetEditablePairSpecialAlternativeText()  # type: localization.LocalizedString

			editablePairRow = UISettings.DialogRow(
				currentGenderTagPairOptionID,
				createEditPairCallback(editablePairIdentifier),
				Language.CreateLocalizationString(editablePairRowText),
				description = editablePairRowDescription,
				icon = self._GetEditablePairRowIcon(),
			)

			currentGenderTagPairOptionID += 1

			rows.append(editablePairRow)

		return rows
