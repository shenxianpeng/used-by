# Used By

[![Used by](https://img.shields.io/static/v1?label=Used%20by&message=3&color=informational&logo=slickpic)](https://github.com/shenxianpeng/used-by/network/dependents)<!-- used by badge -->
[![main](https://github.com/shenxianpeng/used-by/actions/workflows/main.yml/badge.svg)](https://github.com/shenxianpeng/used-by/actions/workflows/main.yml)
[![pre-commit](https://github.com/shenxianpeng/used-by/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/shenxianpeng/used-by/actions/workflows/pre-commit.yml)
[![codecov](https://codecov.io/github/shenxianpeng/used-by/graph/badge.svg?token=QDO4MCI87B)](https://codecov.io/github/shenxianpeng/used-by)

Create and update Used By badge by leveraging GitHub's dependencies information via a pull request.

## Usage

### Run as GitHub Action

Create a new GitHub Actions workflow in your project, e.g. at `.github/workflows/used-by.yml`

```yaml
    steps:
      - uses: actions/checkout@v4
      - uses: shenxianpeng/used-by@main # or tag
        with:
          repo: '${{ github.repository }}' # current repository
          update-badge: 'true'

      # create pull request if changed
      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v6
        with:
          add-paths: "README.md" # the file path to commit
          commit-message: "chore: update used-by badge by github-actions[bot]"
          title: "chore: automatic update used-by badge"
          base: main
          labels: documentation
          delete-branch: true
```

> [!IMPORTANT]
> To create pull request with `peter-evans/create-pull-request@v6` requires changing [Workflow permissions](https://github.com/peter-evans/create-pull-request?tab=readme-ov-file#workflow-permissions) to **Read and write permissions** and enabling  **Allow GitHub Actions to create and approve pull requests**.

## Required Inputs

### `repo`:
* Description: GitHub repository name. e.g. shenxianpeng/used-by. Defaults to shenxianpeng/used-by.
* Default: 'shenxianpeng/used-by'

## Optional Inputs

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
* Description: The badge display color. Defaults to slickpic.
* Default: 'slickpic'

### `update-badge`:
* Description: The badge display color. Defaults to false.
* Default: 'false'

For supported values of `badge-label`, `badge-color` and `badge-logo`, see https://shields.io/badges/static-badge

### Install `used-by` CLI

```bash
pip install git+https://github.com/shenxianpeng/used-by.git@main
```

### Help of `used-by` CLI

```bash
used-by --help
usage: used-by [-h] [--repo REPO] [--file-path FILE_PATH] [--badge-label BADGE_LABEL] [--badge-color BADGE_COLOR] [--badge-logo BADGE_LOGO] [--update-badge UPDATE_BADGE]

Generate a Used By badge from GitHub dependents information.

options:
  -h, --help            show this help message and exit
  --repo REPO           GitHub repository name (e.g., shenxianpeng/used-by).
  --file-path FILE_PATH
                        The path to the file where the badge will be added. Defaults to README.md.
  --badge-label BADGE_LABEL
                        The badge display name. Defaults to Used by.
  --badge-color BADGE_COLOR
                        The badge display color. Defaults to informational.
  --badge-logo BADGE_LOGO
                        The badge display logo. Defaults to slickpic.
  --update-badge UPDATE_BADGE
                        Add or update badge if set. Defaults to False.
```

### Run `used-by` CLI

```bash
# generate markdown makeup text by default
$ used-by --repo shenxianpeng/used-by
```

## Add Used By badge in README

Copy following content to show Used By badge in your repository README.

[![Used by](https://img.shields.io/static/v1?label=Used%20by&message=3&color=informational&logo=slickpic)](https://github.com/shenxianpeng/used-by/network/dependents)<!-- used by badge -->

**Markdown**

```
[![Used by](https://img.shields.io/static/v1?label=Used%20by&message=3&color=informational&logo=slickpic)](https://github.com/shenxianpeng/used-by/network/dependents)<!-- used by badge -->
```

**reStructuredText**

```
.. image:: https://img.shields.io/static/v1?label=Used%20by&message=0&color=informational&logo=slickpic
    :target: https://github.com/shenxianpeng/used-by/network/dependents
    :alt: used-by
```

## License

[MIT](LICENSE) © 2024-present Xianpeng Shen
