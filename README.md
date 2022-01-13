# Zendesk Sell tap

Built with the [Meltano SDK](https://sdk.meltano.com) for Singer Taps and Targets.

## Capabilities

* `catalog`
* `state`
* `discover`
* `about`
* `stream-maps`

## Settings

| Setting     | Required | Default | Description |
|:------------|:--------:|:-------:|:------------|
| access_token| True     | None    | The token to authenticate against the API service |
| device_uuid | True     | None    | The device's universally unique identifier (UUID) |

A full list of supported settings and capabilities is available by running: `tap-zendesk_sell --about`
