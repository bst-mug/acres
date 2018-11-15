from configparser import ConfigParser
import os


def test_config():
    # Default is not interpolated with environment variables, because we use only the keys
    default_config = ConfigParser()
    default_config.read("config.ini.default")

    # Real config should be interpolated, otherwise we get an InterpolationMissingOptionError
    my_config = ConfigParser(os.environ)
    my_config.read("config.ini")

    # All default configs should be set
    for section in default_config.sections():
        assert my_config[section]
        for option in default_config.options(section):
            assert my_config.get(section, option)

    # Addtional checks
    assert os.path.isfile(my_config["DEFAULT"]["MORPH_ENG"])
    assert os.path.isfile(my_config["DEFAULT"]["MORPH_GER"])
