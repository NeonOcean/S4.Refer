from NeonOcean.S4.Refer.Settings import Types as SettingsTypes

class CustomPronounSets(SettingsTypes.CustomPronounSetsDialogSetting):
	IsSetting = True  # type: bool

	Key = "Custom_Pronoun_Sets"  # type: str
	Default = dict()  # type: dict
