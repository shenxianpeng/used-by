# Used By

[![Build](https://github.com/shenxianpeng/used-by/actions/workflows/build.yml/badge.svg)](https://github.com/shenxianpeng/used-by/actions/workflows/build.yml)
[![pre-commit](https://github.com/shenxianpeng/used-by/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/shenxianpeng/used-by/actions/workflows/pre-commit.yml)

Generate Used By badge from GitHub dependents information.

> [!WARNING]
> We only support Linux runners using a Debian based Linux OS (like Ubuntu and many others) and MacOS.

## Usage

### Run as GitHub Action

Create a new GitHub Actions workflow in your project, e.g. at .github/workflows/used-by.yml


```yaml
    steps:
      - uses: actions/checkout@v4
      - uses: shenxianpeng/used-by@v2
        id: usedby
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          repo: '${{ github.repository }}' # current repository
          update-badge: 'true'
```

### Install `used-by` CLI

```bash
pip install git+https://github.com/shenxianpeng/used-by.git@main
```

### Help of `used-by` CLI

```bash
used-by --help
usage: used-by [-h] [--repo REPO] [--doc-type DOC_TYPE]

Generate Used By badge from GitHub dependents information.

options:
  -h, --help           show this help message and exit
  --repo REPO          GitHub repository name. e.g. shenxianpeng/used-by
  --doc-type DOC_TYPE  Supports md(Markdown) and rst(reStructuredText). Defaults to `md`.
```

### Run `used-by` CLI

```bash
# generate markdown makeup text by default
$ used-by --repo shenxianpeng/used-by

# generate reStructuredText makeup text
used-by --repo shenxianpeng/used-by --doc-type rst
```

## Add Used By badge in README

Copy following markdown content to show Used By badge in your repository README.

You can add Used By badge to your repository README to show your users and contributors.

<!-- used by action -->
[![](https://img.shields.io/static/v1?label=Used%20by&message=517&color=informational&logo=slickpic)](https://github.com/cpp-linter/cpp-linter-action/network/dependents)
<!-- used by action -->

**Markdown**

```
[![](https://img.shields.io/static/v1?label=Used%20by&message=517&color=informational&logo=slickpic)](https://github.com/cpp-linter/cpp-linter-action/network/dependents)
```

**reStructuredText**

```
.. image:: https://img.shields.io/static/v1?label=Used%20by&message=516&color=informational&logo=slickpic
    :target: https://github.com/shenxianpeng/used-by/network/dependents
    :alt: used-by
```

## License

[MIT](LICENSE) © 2024-present Xianpeng Shen
