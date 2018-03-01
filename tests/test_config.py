import configparser
import os


def test_config():
    default_config = configparser.ConfigParser()
    default_config.read("config.ini.default")

    my_config = configparser.ConfigParser()
    my_config.read("config.ini")

    # All default configs should be set
    for section in default_config.sections():
        assert my_config[section]
        for option in default_config.options(section):
            assert my_config.get(section, option)

    # Addtional checks
    assert os.path.isfile(my_config["DEFAULT"]["MORPH_ENG"])
    assert os.path.isfile(my_config["DEFAULT"]["MORPH_GER"])
