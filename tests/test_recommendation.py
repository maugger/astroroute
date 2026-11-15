import pytest

from astroroute.core.models import MissionPreferences


def test_mission_preferences_require_a_positive_total_weight():
    with pytest.raises(ValueError, match="preference weight"):
        MissionPreferences(
            delta_v_weight=0,
            transfer_time_weight=0,
            sensitivity_weight=0,
        )
