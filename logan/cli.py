from parser import extract_status

def main():
    with open("sample_logs/access.log") as f:
        line = f.readline()
        print(line)

    status = extract_status(line)
    print(f"Status code: {status}")


if __name__ == "__main__":
    main()
