# Used By

[![main](https://github.com/shenxianpeng/used-by/actions/workflows/main.yml/badge.svg)](https://github.com/shenxianpeng/used-by/actions/workflows/main.yml)
[![used-by](https://img.shields.io/static/v1?label=Used%20by&message=0&color=informational&logo=slickpic)](https://github.com/shenxianpeng/used-by/network/dependents) <!-- used by badge -->
[![pre-commit](https://github.com/shenxianpeng/used-by/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/shenxianpeng/used-by/actions/workflows/pre-commit.yml)

Generate Used By badge from GitHub dependents information.


> [!WARNING]
> We only support Linux runners using a Debian based Linux OS (like Ubuntu and many others) and MacOS.

## Usage

### Run as GitHub Action

Create a new GitHub Actions workflow in your project, e.g. at [.github/workflows/used-by.yml](.github/workflows/used-by.yml)

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

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v6
        with:
          add-paths: "README.md" # the file path to commit
          commit-message: "chore: update used-by badge by github-actions[bot]"
          title: "chore: automatically update used-by badge"
          base: main
          labels: documentation
          delete-branch: true
```

> [!IMPORTANT]
> To create pull request with `peter-evans/create-pull-request@v6` requires changing [Workflow permissions](https://github.com/peter-evans/create-pull-request?tab=readme-ov-file#workflow-permissions) to **Read and write permissions** and enabling  **Allow GitHub Actions to create and approve pull requests**.

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

Copy following content to show Used By badge in your repository README.

[![used-by](https://img.shields.io/static/v1?label=Used%20by&message=0&color=informational&logo=slickpic)](https://github.com/shenxianpeng/used-by/network/dependents) <!-- used by badge -->

**Markdown**

```
[![used-by](https://img.shields.io/static/v1?label=Used%20by&message=0&color=informational&logo=slickpic)](https://github.com/shenxianpeng/used-by/network/dependents) <!-- used by badge -->
```

**reStructuredText**

```
.. image:: https://img.shields.io/static/v1?label=Used%20by&message=0&color=informational&logo=slickpic
    :target: https://github.com/shenxianpeng/used-by/network/dependents
    :alt: used-by
```

## License

[MIT](LICENSE) © 2024-present Xianpeng Shen
