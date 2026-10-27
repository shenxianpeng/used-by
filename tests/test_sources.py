import pytest
import requests

from used_by.sources import (
    get_deps_dev_count,
    get_deps_dev_default_version,
    read_count,
)

DEPS_DEV = "https://api.deps.dev"


@pytest.fixture
def fake_api(mocker):
    """Patch requests.get to answer from ``fake_api.responses``: url -> (status, json)."""
    responses = {}

    def fake_get(url, timeout=None):
        status, payload = responses.get(url, (404, None))
        response = mocker.MagicMock(status_code=status)
        response.json.return_value = payload
        if status >= 400:
            response.raise_for_status.side_effect = requests.HTTPError(f"{status}")
        return response

    mock_get = mocker.patch("requests.get", side_effect=fake_get)
    mock_get.responses = responses
    return mock_get


def package_json(*versions, default=None):
    return {
        "versions": [
            {"versionKey": {"version": v}, "isDefault": v == default} for v in versions
        ]
    }


# read_count


@pytest.mark.parametrize("value", [None, "12", 1.5, True])
def test_read_count_rejects_non_integers(value):
    with pytest.raises(ValueError, match="Could not read the count from somewhere"):
        read_count(value, "somewhere")


def test_read_count_accepts_zero():
    assert read_count(0, "somewhere") == 0


# deps.dev


def test_deps_dev_default_version(fake_api):
    fake_api.responses[f"{DEPS_DEV}/v3/systems/pypi/packages/requests"] = (
        200,
        package_json("2.31.0", "2.32.3", default="2.32.3"),
    )
    assert get_deps_dev_default_version("pypi", "requests") == "2.32.3"
    fake_api.assert_called_once_with(
        f"{DEPS_DEV}/v3/systems/pypi/packages/requests", timeout=10
    )


def test_deps_dev_default_version_missing(fake_api):
    fake_api.responses[f"{DEPS_DEV}/v3/systems/pypi/packages/requests"] = (
        200,
        package_json("2.31.0"),
    )
    with pytest.raises(ValueError, match="pass --package-version"):
        get_deps_dev_default_version("pypi", "requests")


def test_deps_dev_unknown_package(fake_api):
    with pytest.raises(ValueError, match="deps.dev has no pypi package named 'nope'"):
        get_deps_dev_count("pypi", "nope")


def test_deps_dev_count_uses_default_version_and_escapes_names(fake_api):
    # Scoped npm names contain "@" and "/", which must be escaped in the path.
    fake_api.responses[f"{DEPS_DEV}/v3/systems/npm/packages/%40types%2Fnode"] = (
        200,
        package_json("26.6.5", default="26.6.5"),
    )
    fake_api.responses[
        f"{DEPS_DEV}/v3alpha/systems/npm/packages/%40types%2Fnode/versions/26.6.5:dependents"
    ] = (200, {"dependentCount": 406323, "directDependentCount": 1})

    count, link = get_deps_dev_count("npm", "@types/node")

    assert count == 406323
    assert link == "https://deps.dev/npm/%40types%2Fnode/26.6.5/dependents"


def test_deps_dev_count_with_given_version_skips_lookup(fake_api):
    fake_api.responses[
        f"{DEPS_DEV}/v3alpha/systems/maven/packages/org.apache.commons%3Acommons-lang3/versions/3.21.0:dependents"
    ] = (200, {"dependentCount": 2870})

    count, link = get_deps_dev_count(
        "maven", "org.apache.commons:commons-lang3", "3.21.0"
    )

    assert count == 2870
    assert fake_api.call_count == 1
    assert link.endswith("/maven/org.apache.commons%3Acommons-lang3/3.21.0/dependents")


def test_deps_dev_count_without_dependents_data(fake_api):
    with pytest.raises(ValueError, match="no dependents data for nuget Foo 1.0"):
        get_deps_dev_count("nuget", "Foo", "1.0")


def test_deps_dev_count_missing_number_is_an_error(fake_api):
    fake_api.responses[
        f"{DEPS_DEV}/v3alpha/systems/pypi/packages/requests/versions/1.0:dependents"
    ] = (200, {})
    with pytest.raises(ValueError, match="from deps.dev"):
        get_deps_dev_count("pypi", "requests", "1.0")


def test_deps_dev_server_error_is_raised(fake_api):
    fake_api.responses[f"{DEPS_DEV}/v3/systems/pypi/packages/requests"] = (500, None)
    with pytest.raises(requests.HTTPError):
        get_deps_dev_count("pypi", "requests")
