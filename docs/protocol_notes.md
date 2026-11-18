# Protocol Notes

## HJ 212-2017 Message Format

```
##LLLL<Header>&&<Data><CRC>\r\n
```

| Part | Description |
|------|-------------|
| `##` | Start delimiter |
| `LLLL` | Data length (4 digits, zero-padded) |
| `<Header>` | Semicolon-separated key-value pairs |
| `&&` | Data separator |
| `<Data>` | Message payload (CP fields, etc.) |
| `<CRC>` | CRC-16 checksum (4 hex chars, uppercase) |
| `\r\n` | End delimiter |

## Header Fields

| Field | Required | Description |
|-------|----------|-------------|
| PN | Yes | Pollutant number / Station ID |
| CN | Yes | Command number |
| PW | Yes | Password (6 characters) |
| MN | Yes | Monitoring station number |
| ST | Yes | System type |
| Flag | Yes | Message flag |
| PNO | Yes | Packet number |

## CRC-16 Parameters

- Polynomial: `0xA001`
- Initial value: `0xFFFF`
- Input encoding: ASCII
- Output: 4-digit uppercase hex

## CP Field Format

CP fields use `;` as the primary separator and `=` between key and value:

```
w01001-Rtd=12.5;w01002-Rtd=34.0
```

## Notes

- Data length counts characters between `##` and CRC, excluding delimiters.
- Flag field bits indicate encryption and packaging status.
- Unknown header fields should be preserved in raw form.
- Parsing errors must not be silently discarded.
