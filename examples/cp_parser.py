"""Example: Parse CP (Command Parameter) fields."""

from pyhj212.cp.parser import CPParser


def main() -> None:
    """Demonstrate parsing CP field strings."""
    cp_string = "w01001-Rtd=12.5;w01002-Rtd=34.0;w01003-Rtd=5.67"

    parser = CPParser()
    fields = parser.parse(cp_string)

    for field in fields:
        print(f"{field.key} = {field.value}")


if __name__ == "__main__":
    main()
