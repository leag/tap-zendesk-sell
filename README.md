# Zendesk Sell CRM Singer tap

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

<!--

Developer TODO: Update the below as needed to correctly describe the install procedure. For instance, if you do not have a PyPI repo, or if you want users to directly install from your git repo, you can modify this step as appropriate.

## Installation

Install from PyPI:

```bash
pipx install tap-zendesk-sell
```

Install from GitHub:

```bash
pipx install git+https://github.com/ORG_NAME/tap-zendesk-sell.git@main
```

-->

## Configuration

### Accepted Config Options

<!--
Developer TODO: Provide a list of config options accepted by the tap.

This section can be created by copy-pasting the CLI output from:

```
tap-zendesk-sell --about --format=markdown
```
-->

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-zendesk-sell --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

<!--
Developer TODO: If your tap requires special access on the source system, or any special authentication requirements, provide those here.
-->

## Usage

You can easily run `tap-zendesk-sell` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-zendesk-sell --version
tap-zendesk-sell --help
tap-zendesk-sell --config CONFIG --discover > ./catalog.json
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

Prerequisites:

- Python 3.9+
- [uv](https://docs.astral.sh/uv/)

```bash
uv sync
```

### Create and Run Tests

Create tests within the `tests` subfolder and
  then run:

```bash
uv run pytest
```

You can also test the `tap-zendesk-sell` CLI interface directly using `uv run`:

```bash
uv run tap-zendesk-sell --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

<!--
Developer TODO:
Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any "TODO" items listed in
the file.
-->

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano project
meltano init my-project
cd my-project
# Add the tap and target plugins to your project
meltano add extractor tap-zendesk-sell --from-ref ../tap-zendesk-sell
meltano add loader target-jsonl
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-zendesk-sell --version

# OR run a test ELT pipeline:
meltano run tap-zendesk-sell target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.

## Capabilities

-   `catalog`
-   `state`
-   `discover`
-   `about`
-   `stream-maps`

## Settings

| Setting      | Required | Default | Description                                       |
| :----------- | :------: | :-----: | :------------------------------------------------ |
| access_token |   True   |  None   | The token to authenticate against the API service |
| device_uuid  |  False   |  None   | The device's universally unique identifier (UUID) |

## Event Stream

This tap uses the Zendesk Sell [Sync API](https://developer.zendesk.com/api-reference/sales-crm/sync/introduction/) to generate an **Event Stream**.

The state of a the stream is saved in the server, referenced by a **device_uuid**, this device_uuid is also sent as state for the event stream.

To do a full table sync of the events stream, you need to generate a new **device_uuid**, this can be done by not setting a **device_uuid** in the config (it autogenerates a new one) or by setting a new **device_uuid**, and not sending any state for the stream.

## Copyright and license

Copyright 2022 Luis Atala.
Licensed under the [Apache License, Version 2.0](LICENSE).
