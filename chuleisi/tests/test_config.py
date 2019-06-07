import pytest

import chuleisi.config
from chuleisi.utils import get_cpu_count


def test_defaults():
    number_of_workers = get_cpu_count()
    config = chuleisi.config.Config()

    assert not config.main.verbose
    assert config.main.number_of_workers == number_of_workers
    assert config.redis.host == 'localhost'
    assert config.redis.port == 6379

    assert str(config) == '\n'.join([
        '[main]',
        'verbose = false',
        f'number_of_workers = {number_of_workers}',
        '',
        '[redis]',
        'host = "localhost"',
        'port = 6379',
    ])


def test_get_nonexistent_option():
    config = chuleisi.config.Config()

    with pytest.raises(chuleisi.config.NoSuchConfigurationError) as exc_info:
        config.main.gauche

    assert f"No such configuration option: 'gauche'" in str(exc_info.value)


def test_override(make_config):
    config = make_config({
        'main': {'number_of_workers': 1},
        'redis': {'port': 42},
    })

    assert not config.main.verbose
    assert config.main.number_of_workers == 1
    assert config.redis.host == 'localhost'
    assert config.redis.port == 42

    assert str(config) == '\n'.join([
        '[main]',
        'verbose = false',
        'number_of_workers = 1',
        '',
        '[redis]',
        'host = "localhost"',
        'port = 42',
    ])


def test_override_with_nonexistent_file():
    config = chuleisi.config.Config.from_file('/no/such/file')

    # Ensure we got the defaults
    assert config == chuleisi.config.Config()


@pytest.mark.parametrize('value', [
    42,
    'true',
])
def test_override_verbose_invalid(make_config, value):
    with pytest.raises(chuleisi.config.InvalidConfigurationError) as exc_info:
        make_config({'main': {'verbose': value}})

    assert ('Invalid [main] configuration:\n'
            f'* verbose: {value!r} is not a boolean') in str(exc_info.value)


@pytest.mark.parametrize('value', [
    False,
    True,
    '42',
])
def test_override_number_of_workers_invalid(make_config, value):
    with pytest.raises(chuleisi.config.InvalidConfigurationError) as exc_info:
        make_config({'main': {'number_of_workers': value}})

    assert ('Invalid [main] configuration:\n'
            f'* number_of_workers: {value!r} is not an integer') in str(exc_info.value)


@pytest.mark.parametrize('value', [
    -1,
    0,
])
def test_override_number_of_workers_negative_or_zero(make_config, value):
    with pytest.raises(chuleisi.config.InvalidConfigurationError) as exc_info:
        make_config({'main': {'number_of_workers': value}})

    assert ('Invalid [main] configuration:\n'
            f'* number_of_workers: {value!r} is not a strictly positive integer'
            ) in str(exc_info.value)


@pytest.mark.parametrize('value', [
    False,
    True,
    42,
])
def test_override_redis_host_invalid(make_config, value):
    with pytest.raises(chuleisi.config.InvalidConfigurationError) as exc_info:
        make_config({'redis': {'host': value}})

    assert ('Invalid [redis] configuration:\n'
            f'* host: {value!r} is not a string') in str(exc_info.value)


def test_override_redis_host_empty(make_config):
    with pytest.raises(chuleisi.config.InvalidConfigurationError) as exc_info:
        make_config({'redis': {'host': ''}})

    assert ('Invalid [redis] configuration:\n'
            f"* host: '' is empty") in str(exc_info.value)


@pytest.mark.parametrize('value', [
    False,
    True,
    'foo',
])
def test_override_redis_port_invalid(make_config, value):
    with pytest.raises(chuleisi.config.InvalidConfigurationError) as exc_info:
        make_config({'redis': {'port': value}})

    assert ('Invalid [redis] configuration:\n'
            f'* port: {value!r} is not an integer') in str(exc_info.value)


@pytest.mark.parametrize('value', [
    -1,
    0,
])
def test_override_redis_port_not_positive(make_config, value):
    with pytest.raises(chuleisi.config.InvalidConfigurationError) as exc_info:
        make_config({'redis': {'port': value}})

    assert ('Invalid [redis] configuration:\n'
            f'* port: {value!r} is not a strictly positive integer') in str(exc_info.value)
