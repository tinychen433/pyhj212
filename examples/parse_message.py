"""Example: Parse an HJ 212-2017 message string."""

from pyhj212.protocol.parser import Parser


def main() -> None:
    """Demonstrate parsing a raw HJ 212-2017 message."""
    raw = "##0857QN=20260902083001000;ST=31;CN=2051;PW=123456;MN=YSRDAQ07ST00002713;Flag=5;CP=&&PNO=000000004;DataTime=20260902082000;RtdInterval=300;RestartTime=20260902064138;a34004-Avg=3.000;a34002-Avg=4.000;ys0017-Avg=5.000;ys0019-Avg=5.000;ys0018-Avg=-99.000;ys0020-Avg=-99.000;ys0021-Avg=5.000;a05024-Avg=-99.00;a21026-Avg=-99.00;a21004-Avg=-99.0;a21005-Avg=-99.000;a99054-Avg=-99.000;ys0025-Avg=0.000;ys0026-Avg=0.000;ys0023-Avg=0.000;ys0024-Avg=0.000;ys0027-Avg=0.000;ys0028-Avg=0.000;ys0029-Avg=0.000;ys0030-Avg=0.000;ys0031-Avg=0.000;ys0032-Avg=0.000;a01012-Rtd=36.0;a01014-Rtd=30.4;a01001-Rtd=24.4;a01002-Rtd=59.6;ys0111-Rtd=24.4;ys0007-Rtd=116.489983;ys0008-Rtd=39.902966;ys0034-Rtd=-99.000;a01006-Rtd=-99.000;a01007-Avg=-99.0;a01008-Avg=-99;ys0009-Rtd=31;ys0013-Rtd=0;ys0010-Rtd=0;ys0011-Rtd=75;ys0012-Rtd=50;ys0002-Rtd=162.005;ys0014-Rtd=89860473102590002828&&A141\r\n"

    parser = Parser()
    message = parser.parse(raw)

    print(f"Header: {message.header}")
    print(f"Data: {message.data}")
    print(f"CRC: {message.crc}")


if __name__ == "__main__":
    main()
