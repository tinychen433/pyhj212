"""Example: Parse CP (Command Parameter) fields."""

import json

from pyhj212.cp.parser import CPParser


def main() -> None:
    """Demonstrate parsing CP field strings."""
    cp_string = "DataTime=20261118134500;tn0112-Rtd=228.200,tn0112-Flag=N;tn0110-Rtd=229.100,tn0110-Flag=N;tn0109-Rtd=1.000,tn0109-Flag=N;tn0105-Rtd=0.000,tn0105-Flag=N;tn0107-Rtd=0.0,tn0107-Flag=N;tn0111-Rtd=230.000,tn0111-Flag=N;tn0108-Rtd=0.0,tn0108-Flag=N;tn0101-Rtd=0.000,tn0101-Flag=N;tn0103-Rtd=0.000,tn0103-Flag=N;tn0102-Rtd=0.000,tn0102-Flag=N;tn0106-Rtd=0.000,tn0106-Flag=N"

    parser = CPParser()
    fields = parser.parse(cp_string)

    print(json.dumps([f.to_dict() for f in fields], indent=2))

    # --- Without Flag attribute ---
    cp_no_flag = "DataTime=20261118134500;tn0112-Rtd=228.200;tn0110-Rtd=229.100;tn0109-Rtd=1.000;tn0105-Rtd=0.000;tn0107-Rtd=0.0;tn0111-Rtd=230.000;tn0108-Rtd=0.0;tn0101-Rtd=0.000;tn0103-Rtd=0.000;tn0102-Rtd=0.000;tn0106-Rtd=0.000"

    print()
    print("=" * 60)
    print("Without Flag attribute")
    print("=" * 60)
    fields2 = parser.parse(cp_no_flag)
    print(json.dumps([f.to_dict() for f in fields2], indent=2))


if __name__ == "__main__":
    main()
