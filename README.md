# NAMEPING

<div align="center">

<img src="https://raw.githubusercontent.com/gmarciani/nameping/main/resources/brand/banner.png" alt="nameping-banner" width="500">

[![PyPI version](https://img.shields.io/pypi/v/nameping.svg)](https://pypi.org/project/nameping)
[![Python versions](https://img.shields.io/pypi/pyversions/nameping.svg)](https://pypi.org/project/nameping)
[![License](https://img.shields.io/github/license/gmarciani/nameping.svg)](https://github.com/gmarciani/nameping/blob/main/LICENSE)
[![Build status](https://img.shields.io/github/actions/workflow/status/gmarciani/nameping/test.yaml?branch=main)](https://github.com/gmarciani/nameping/actions)
[![Tests](https://img.shields.io/github/actions/workflow/status/gmarciani/nameping/test.yaml?branch=main&label=tests)](https://github.com/gmarciani/nameping/actions)
[![Coverage](https://img.shields.io/codecov/c/github/gmarciani/nameping)](https://codecov.io/gh/gmarciani/nameping)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Downloads](https://img.shields.io/pypi/dm/nameping.svg)](https://pypi.org/project/nameping)

</div>

Check name availability across domains and business registries.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Commands](#commands)
- [Issues](#issues)
- [License](#license)

## Features

- Check domain name availability via WHOIS lookup across multiple TLDs
- Check company name availability in the Delaware Division of Corporations registry
- Batch processing from comma-separated input or file (one name per line)
- Output in JSON, YAML, CSV, or markdown table format (console and file)

## Installation

```shell
pip install nameping
```

## Usage

### Check domain availability

```shell
# Single name, default TLD (com)
nameping check-domain --names myproject

# Multiple names and TLDs
nameping check-domain --names "alpha,bravo,charlie" --tld com,net,io

# From a file, checking only entries 10 through 20
nameping check-domain --file names.txt --from 10 --to 20

# Save results as Makrdown table, excluding taken domains
nameping check-domain --file names.txt --tld com --output results.md --output-format csv --exclude-taken
```

### Check company name availability

```shell
# Single name in Delaware (default registry)
nameping check-company --names myproject

# Multiple names and company types
nameping check-company --names "alpha,bravo" --company-type llc,corp

# Specify registry explicitly
nameping check-company --file names.txt --registries delaware --output results.json
```

## Documentation

Check out the official documentation [here](https://gmarciani.github.io/nameping).

## Issues

Please report any issues or feature requests on the [GitHub Issues](https://github.com/gmarciani/nameping/issues) page.

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/gmarciani/nameping/blob/main/LICENSE) file for details.
