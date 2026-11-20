"""Example: Parse CP (Command Parameter) fields."""

import json

from pyhj212 import parse_cp, encode_cp


def main() -> None:
    """Demonstrate parsing and encoding CP field strings."""
    cp_string = "DataTime=20261118134500;tn0112-Rtd=228.200,tn0112-Flag=N;tn0110-Rtd=229.100,tn0110-Flag=N"

    # Parse
    fields = parse_cp(cp_string)

    print(json.dumps([f.to_dict() for f in fields], indent=2))

    # Encode back
    print()
    print("Roundtrip:", encode_cp(fields) == cp_string)

    # Without Flag attribute
    cp_no_flag = "DataTime=20261118134500;tn0112-Rtd=228.200;tn0110-Rtd=229.100"

    print()
    print("=" * 60)
    print("Without Flag attribute")
    print("=" * 60)
    fields2 = parse_cp(cp_no_flag)
    print(json.dumps([f.to_dict() for f in fields2], indent=2))


if __name__ == "__main__":
    main()
