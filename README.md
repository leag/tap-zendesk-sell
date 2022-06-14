# Zendesk Sell CRM Singer tap

Built with the [Meltano SDK](https://sdk.meltano.com) for Singer Taps and Targets. using the official [Python API Client](https://github.com/zendesk/basecrm-python)

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
