from __future__ import annotations

from NeonOcean.S4.Main import This
from NeonOcean.S4.Main.UI import Settings as UISettings

class CustomPronounSetsDialog(UISettings.StandardDialog):
	HostNamespace = This.Mod.Namespace  # type: str
	HostName = This.Mod.Name  # type: str
