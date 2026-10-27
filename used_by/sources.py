"""Dependents counts from sources other than GitHub's dependents page.

Each function returns ``(count, link)``: the number to show on the badge and
the page the badge should link to.
"""

from urllib.parse import quote

import requests

DEPS_DEV_ECOSYSTEMS = ("npm", "pypi", "maven", "cargo")
DEPS_DEV_API = "https://api.deps.dev"


def _escape(value: str) -> str:
    """Escape a value for one URL path segment, e.g. "@scope/pkg"."""
    return quote(value, safe="")


def get_json(url: str, not_found_message: str):
    response = requests.get(url, timeout=10)
    if response.status_code == 404:
        raise ValueError(not_found_message)
    response.raise_for_status()
    return response.json()


def read_count(value, where: str) -> int:
    # Never fall back to 0: a missing number must not reset the badge.
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"Could not read the count from {where}; got {value!r}.")
    return value


def get_deps_dev_default_version(ecosystem: str, package: str) -> str:
    data = get_json(
        f"{DEPS_DEV_API}/v3/systems/{ecosystem}/packages/{_escape(package)}",
        f"deps.dev has no {ecosystem} package named {package!r}.",
    )
    for version in data.get("versions", []):
        if version.get("isDefault"):
            return version["versionKey"]["version"]
    raise ValueError(
        f"deps.dev has no default version for the {ecosystem} package "
        f"{package!r}; pass --package-version."
    )


def get_deps_dev_count(ecosystem: str, package: str, version=None):
    """Packages that depend on one version of a package, according to deps.dev.

    deps.dev counts dependents per version, so the default version (the one
    deps.dev shows first, usually the latest release) is used unless a version
    is given.
    """
    version = version or get_deps_dev_default_version(ecosystem, package)
    path = f"{ecosystem}/packages/{_escape(package)}/versions/{_escape(version)}"
    data = get_json(
        f"{DEPS_DEV_API}/v3alpha/systems/{path}:dependents",
        f"deps.dev has no dependents data for {ecosystem} {package} {version}.",
    )
    count = read_count(data.get("dependentCount"), "deps.dev")
    link = (
        f"https://deps.dev/{ecosystem}/{_escape(package)}/{_escape(version)}/dependents"
    )
    return count, link
