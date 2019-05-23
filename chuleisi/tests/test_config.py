import pytest

import chuleisi.config
from chuleisi.utils import get_cpu_count


def test_defaults():
    number_of_workers = get_cpu_count()
    config = chuleisi.config.Config()

    assert not config.main.verbose
    assert config.main.number_of_workers == number_of_workers


def test_get_nonexistent_option():
    config = chuleisi.config.Config()

    with pytest.raises(chuleisi.config.NoSuchConfigurationError) as exc_info:
        config.main.gauche

    assert f"No such configuration option: 'gauche'" in str(exc_info.value)
