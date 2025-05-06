# `tap-zendesk-sell`

Zendesk Sell tap class.

Built with the [Meltano Singer SDK](https://sdk.meltano.com).

## Capabilities

* `catalog`
* `state`
* `discover`
* `about`
* `stream-maps`
* `schema-flattening`
* `batch`

## Supported Python Versions

* 3.9
* 3.10
* 3.11
* 3.12
* 3.13

## Settings

| Setting | Required | Default | Description |
|:--------|:--------:|:-------:|:------------|
| access_token | True     | None    | Provides access to Zendesk Sell API |
| device_uuid | False    | None    | Identifier used accross sync sessions |
| stream_maps | False    | None    | Config object for stream maps capability. For more information check out [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html). |
| stream_map_config | False    | None    | User-defined config values to be used within map expressions. |
| faker_config | False    | None    | Config for the [`Faker`](https://faker.readthedocs.io/en/master/) instance variable `fake` used within map expressions. Only applicable if the plugin specifies `faker` as an additional dependency (through the `singer-sdk` `faker` extra or directly). |
| faker_config.seed | False    | None    | Value to seed the Faker generator for deterministic output: https://faker.readthedocs.io/en/master/#seeding-the-generator |
| faker_config.locale | False    | None    | One or more LCID locale strings to produce localized output for: https://faker.readthedocs.io/en/master/#localization |
| flattening_enabled | False    | None    | 'True' to enable schema flattening and automatically expand nested properties. |
| flattening_max_depth | False    | None    | The max depth to flatten schemas. |
| batch_config | False    | None    | Configuration for BATCH message capabilities. |
| batch_config.encoding | False    | None    | Specifies the format and compression of the batch files. |
| batch_config.encoding.format | False    | None    | Format to use for batch files. |
| batch_config.encoding.compression | False    | None    | Compression format to use for batch files. |
| batch_config.storage | False    | None    | Defines the storage layer to use when writing batch files |
| batch_config.storage.root | False    | None    | Root path to use when writing batch files. |
| batch_config.storage.prefix | False    | None    | Prefix to use when writing batch files. |

## Event Stream

This tap uses the Zendesk Sell [Sync API](https://developer.zendesk.com/api-reference/sales-crm/sync/introduction/) to generate an **Event Stream**.

The state of a the stream is saved in the server, referenced by a **device_uuid**, this device_uuid is also sent as state for the event stream.

To do a full table sync of the events stream, you need to generate a new **device_uuid**, this can be done by not setting a **device_uuid** in the config (it autogenerates a new one) or by setting a new **device_uuid**, and not sending any state for the stream.

## Copyright and license

Copyright 2022 Luis Atala.
Licensed under the [Apache License, Version 2.0](LICENSE).
