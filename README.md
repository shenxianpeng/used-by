# Used By

[![Used by](https://img.shields.io/static/v1?label=Used%20by&message=10&color=informational&logo=slickpic)](https://github.com/shenxianpeng/used-by/network/dependents)<!-- used by badge -->
[![main](https://github.com/shenxianpeng/used-by/actions/workflows/main.yml/badge.svg)](https://github.com/shenxianpeng/used-by/actions/workflows/main.yml)
[![pre-commit](https://github.com/shenxianpeng/used-by/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/shenxianpeng/used-by/actions/workflows/pre-commit.yml)
[![codecov](https://codecov.io/github/shenxianpeng/used-by/graph/badge.svg?token=QDO4MCI87B)](https://codecov.io/github/shenxianpeng/used-by)

Create and update a Used By badge via a pull request, counted from one of these sources:

| `source` | What is counted | Badge links to |
|---|---|---|
| `github` (default) | Repositories that depend on a GitHub repository ([dependency graph](https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/about-the-dependency-graph)) | `github.com/<repo>/network/dependents` |
| `deps.dev` | Packages that depend on an npm, PyPI, Maven or Cargo package, according to [deps.dev](https://deps.dev) | the deps.dev dependents page |
| `jenkins` | Jenkins controllers that have a plugin installed, according to [plugins.jenkins.io](https://plugins.jenkins.io) | the plugin page |

## Usage

### Run as GitHub Action

Create a new GitHub Actions workflow in your project, e.g. at `.github/workflows/used-by.yml`

```yaml
    steps:
      - uses: actions/checkout@v7
      - uses: shenxianpeng/used-by@main # or tag
        with:
          repo: '${{ github.repository }}' # current repository
          update-badge: 'true'

      # create pull request if changed
      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v8
        with:
          add-paths: "README.md" # the file path to commit
          commit-message: "chore: update used-by badge by github-actions[bot]"
          title: "chore: automatic update used-by badge"
          base: main
          labels: documentation
          delete-branch: true
```

> [!IMPORTANT]
> To create pull request with `peter-evans/create-pull-request@v8` requires changing [Workflow permissions](https://github.com/peter-evans/create-pull-request?tab=readme-ov-file#workflow-permissions) to **Read and write permissions** and enabling  **Allow GitHub Actions to create and approve pull requests**.

### Count from deps.dev or Jenkins

Set `source` and `package` (plus `ecosystem` for deps.dev) instead of `repo`:

```yaml
      # Jenkins plugin installations
      - uses: shenxianpeng/used-by@main
        with:
          source: jenkins
          package: explain-error # plugin id
          badge-label: Installs
          update-badge: 'true'

      # Packages depending on a PyPI package
      - uses: shenxianpeng/used-by@main
        with:
          source: deps.dev
          ecosystem: pypi # npm, pypi, maven or cargo
          package: requests
          update-badge: 'true'
```

> [!NOTE]
> - deps.dev counts dependents **per version**. The version deps.dev marks as default (usually the latest release) is used unless `package-version` is set, so the count can dip right after a release until deps.dev has indexed it; `max-drop` keeps the old number when that happens.
> - Jenkins installation counts come from the monthly Jenkins usage statistics, so they change at most once a month.

## Inputs

### `source`:
* Description: Where the count comes from: `github`, `deps.dev` or `jenkins`.
* Default: 'github'

### `repo`:
* Description: GitHub repository name. e.g. shenxianpeng/used-by. Used with source `github`.
* Default: 'shenxianpeng/used-by'

### `package`:
* Description: Package name for source `deps.dev` (e.g. `requests`, `@types/node`, `org.apache.commons:commons-lang3`), or plugin id for source `jenkins` (e.g. `explain-error`).
* Default: ''

### `ecosystem`:
* Description: Package ecosystem for source `deps.dev`: `npm`, `pypi`, `maven` or `cargo`.
* Default: ''

### `package-version`:
* Description: Package version for source `deps.dev`. Defaults to the version deps.dev marks as default.
* Default: ''

### `file-path`:
* Description: The path to file. Defaults to README.md.
* Default: 'README.md'

### `badge-label`:
* Description: The badge display name. Defaults to Used by.
* Default: 'Used by'

### `badge-color`:
* Description: The badge display color. Defaults to informational.
* Default: 'informational'

### `badge-logo`:
* Description: The badge display logo. Defaults to slickpic.
* Default: 'slickpic'

### `update-badge`:
* Description: Update an existing badge whose count changed ('true' or 'false'); a missing badge is always added. Defaults to false.
* Default: 'false'

### `max-drop`:
* Description: Skip the update when the count drops by more than this percentage (0-100), which usually means the source returned bad data. A warning is printed instead. Use 100 to accept any drop. Defaults to 50.
* Default: '50'

For supported values of `badge-label`, `badge-color` and `badge-logo`, see https://shields.io/badges/static-badge

### Install `used-by` CLI

```bash
pip install used-by
```

### Help of `used-by` CLI

```bash
used-by --help
usage: used-by [-h] [--source {github,deps.dev,jenkins}] [--repo REPO]
               [--package PACKAGE] [--ecosystem {npm,pypi,maven,cargo}]
               [--package-version PACKAGE_VERSION] [--file-path FILE_PATH]
               [--badge-label BADGE_LABEL] [--badge-color BADGE_COLOR]
               [--badge-logo BADGE_LOGO] [--update-badge UPDATE_BADGE]
               [--max-drop MAX_DROP]

Generate a Used By badge from GitHub dependents, deps.dev dependents or
Jenkins plugin installations.

options:
  -h, --help            show this help message and exit
  --source {github,deps.dev,jenkins}
                        Where the count comes from: GitHub dependents of
                        --repo, deps.dev dependents of --package in
                        --ecosystem, or Jenkins installations of the plugin
                        --package. Defaults to github.
  --repo REPO           GitHub repository name (e.g., shenxianpeng/used-by).
                        Required for --source github.
  --package PACKAGE     Package name for --source deps.dev (e.g., requests),
                        or plugin id for --source jenkins (e.g., explain-
                        error).
  --ecosystem {npm,pypi,maven,cargo}
                        Package ecosystem for --source deps.dev.
  --package-version PACKAGE_VERSION
                        Package version for --source deps.dev, which counts
                        dependents per version. Defaults to the version
                        deps.dev marks as default.
  --file-path FILE_PATH
                        The path to the file where the badge will be added.
                        Defaults to README.md.
  --badge-label BADGE_LABEL
                        The badge display name. Defaults to Used by.
  --badge-color BADGE_COLOR
                        The badge display color. Defaults to informational.
  --badge-logo BADGE_LOGO
                        The badge display logo. Defaults to slickpic.
  --update-badge UPDATE_BADGE
                        Add or update badge if set. Defaults to False.
  --max-drop MAX_DROP   Do not update the badge when the count drops by more
                        than this percentage, which usually means the source
                        returned bad data. Use 100 to accept any drop.
                        Defaults to 50.
```

### Run `used-by` CLI

```bash
# GitHub dependents of a repository (the default source)
$ used-by --repo shenxianpeng/used-by

# Jenkins plugin installations
$ used-by --source jenkins --package explain-error

# Packages that depend on an npm package, according to deps.dev
$ used-by --source deps.dev --ecosystem npm --package @types/node
```

## Add Used By badge in README

Copy following content to show Used By badge in your repository README.

[![Used by](https://img.shields.io/static/v1?label=Used%20by&message=10&color=informational&logo=slickpic)](https://github.com/shenxianpeng/used-by/network/dependents)<!-- used by badge -->

**Markdown**

```
[![Used by](https://img.shields.io/static/v1?label=Used%20by&message=10&color=informational&logo=slickpic)](https://github.com/shenxianpeng/used-by/network/dependents)<!-- used by badge -->
```

**reStructuredText**

```
.. image:: https://img.shields.io/static/v1?label=Used%20by&message=0&color=informational&logo=slickpic
    :target: https://github.com/shenxianpeng/used-by/network/dependents
    :alt: used-by
```

## License

[MIT](LICENSE) © 2024-present Xianpeng Shen
