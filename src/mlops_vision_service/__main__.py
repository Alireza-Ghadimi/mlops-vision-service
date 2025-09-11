from .core import add


def main() -> None:
    result = add(2, 3)
    print(f"mlops-vision-service is up. add(2, 3) = {result}")


if __name__ == "__main__":
    main()
