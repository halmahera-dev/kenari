from ibm_watsonx_orchestrate.cli.config import Config
import os
import shutil
import pytest

TEST_CONFIG_FILE_FOLDER = os.path.join(os.path.dirname(__file__), "./resources/configs/temp")
TEST_CONFIG_FILE_NAME = "test_config.yaml"
TEST_FILE_PATH = os.path.join(TEST_CONFIG_FILE_FOLDER, TEST_CONFIG_FILE_NAME)


@pytest.fixture()
def get_test_config():
    yield Config(
        config_file_folder=TEST_CONFIG_FILE_FOLDER, config_file=TEST_CONFIG_FILE_NAME
    )

    # Cleanup
    shutil.rmtree(TEST_CONFIG_FILE_FOLDER)


def test_initialise_create_file(get_test_config):
    cfg = get_test_config

    assert cfg is not None
    assert os.path.exists(TEST_FILE_PATH) == True


def test_initialise_create_file_already_exists(get_test_config):
    cfg = get_test_config

    new_cfg = Config(
        config_file_folder=TEST_CONFIG_FILE_FOLDER, config_file=TEST_CONFIG_FILE_NAME
    )

    assert cfg is not None
    assert new_cfg is not None
    assert os.path.exists(TEST_FILE_PATH) == True
    assert len(os.listdir(TEST_CONFIG_FILE_FOLDER)) == 1


def test_config_write(get_test_config):
    cfg = get_test_config

    cfg.write("test_section", "test_option", "test_value")

    with open(TEST_FILE_PATH, "r") as f:
        config_lines = f.readlines()
        assert "test_section:\n" in config_lines
        assert "  test_option: test_value\n" in config_lines


def test_config_write_existing_section(get_test_config):
    cfg = get_test_config

    cfg.write("test_section", "test_option", "test_value")

    cfg.write("test_section", "test_option2", "test_value2")

    with open(TEST_FILE_PATH, "r") as f:
        config_lines = f.readlines()
        assert "test_section:\n" in config_lines
        assert "  test_option: test_value\n" in config_lines
        assert "  test_option2: test_value2\n" in config_lines


def test_config_read_exists(get_test_config):
    cfg = get_test_config

    cfg.write("test_section", "test_option", "test_value")

    stored_value = cfg.read("test_section", "test_option")
    assert stored_value == "test_value"


def test_config_read_section_does_not_exists(get_test_config):
    cfg = get_test_config

    cfg.write("test_section", "test_option", "test_value")

    stored_value = cfg.read("fake", "test_option")
    assert stored_value is None


def test_config_read_option_does_not_exists(get_test_config):
    cfg = get_test_config

    cfg.write("test_section", "test_option", "test_value")

    stored_value = cfg.read("test_section", "fake")
    assert stored_value is None


def test_config_save(get_test_config):
    cfg = get_test_config

    cfg.save(
        {
            "test_save_section": {
                "test_save_option_string": "test_save_str",
                "test_save_option_int": 4,
                "test_save_option_arr": [1, 2, "test"],
                "test_save_option_dict": {"key": "value"},
                "test_save_option_bool": True,
            },
            "test_save_section2": {
                "test_save_option_string": "test_save_str2",
                "test_save_option_int": -4,
                "test_save_option_arr": [-1, False, "test2"],
                "test_save_option_dict": {"key": "value"},
                "test_save_option_bool": False,
            },
        }
    )

    assert cfg.read("test_save_section", "test_save_option_string") == "test_save_str"
    assert cfg.read("test_save_section", "test_save_option_int") == 4
    assert cfg.read("test_save_section", "test_save_option_arr") == [1, 2, "test"]
    assert cfg.read("test_save_section", "test_save_option_dict") == {"key": "value"}
    assert cfg.read("test_save_section", "test_save_option_bool") == True

    assert cfg.read("test_save_section2", "test_save_option_string") == "test_save_str2"
    assert cfg.read("test_save_section2", "test_save_option_int") == -4
    assert cfg.read("test_save_section2", "test_save_option_arr") == [
        -1,
        False,
        "test2",
    ]
    assert cfg.read("test_save_section2", "test_save_option_dict") == {"key": "value"}
    assert cfg.read("test_save_section2", "test_save_option_bool") == False


def test_config_save_existing_section(get_test_config):
    cfg = get_test_config

    cfg.write("test_save_section", "test_save_write_option_int", 8)

    cfg.save(
        {
            "test_save_section": {
                "test_save_option_string": "test_save_str",
                "test_save_option_int": 4,
                "test_save_option_arr": [1, 2, "test"],
                "test_save_option_dict": {"key": "value"},
                "test_save_option_bool": True,
            },
            "test_save_section2": {
                "test_save_option_string": "test_save_str2",
                "test_save_option_int": -4,
                "test_save_option_arr": [-1, False, "test2"],
                "test_save_option_dict": {"key": "value"},
                "test_save_option_bool": False,
            },
        }
    )

    assert cfg.read("test_save_section", "test_save_write_option_int") == 8

    assert cfg.read("test_save_section", "test_save_option_string") == "test_save_str"
    assert cfg.read("test_save_section", "test_save_option_int") == 4
    assert cfg.read("test_save_section", "test_save_option_arr") == [1, 2, "test"]
    assert cfg.read("test_save_section", "test_save_option_dict") == {"key": "value"}
    assert cfg.read("test_save_section", "test_save_option_bool") == True

    assert cfg.read("test_save_section2", "test_save_option_string") == "test_save_str2"
    assert cfg.read("test_save_section2", "test_save_option_int") == -4
    assert cfg.read("test_save_section2", "test_save_option_arr") == [
        -1,
        False,
        "test2",
    ]
    assert cfg.read("test_save_section2", "test_save_option_dict") == {"key": "value"}
    assert cfg.read("test_save_section2", "test_save_option_bool") == False
