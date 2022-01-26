# Zendesk Sell CRM singer tap

Built with the [Meltano SDK](https://sdk.meltano.com) for Singer Taps and Targets. using the official [Python API Client](https://github.com/zendesk/basecrm-python)

## Capabilities

- `catalog`
- `state`
- `discover`
- `about`
- `stream-maps`

## Settings

| Setting      | Required | Default | Description                                       |
| :----------- | :------: | :-----: | :------------------------------------------------ |
| access_token |   True   |  None   | The token to authenticate against the API service |
| device_uuid  |   True   |  None   | The device's universally unique identifier (UUID) |

## Event Stream

This tap uses the Zendesk Sell [Sync API](https://developers.getbase.com/docs/rest/articles/sync/) to create the Event stream. the state is saved in the server, by a device uuid.
To do a full table sync of events, you need to change the device_uuid to a new one.

## Copyright and license

Copyright 2022 Luis Atala.
Licensed under the [Apache License, Version 2.0](LICENSE).

