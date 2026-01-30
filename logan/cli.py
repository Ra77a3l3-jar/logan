def main():
    with open("sample_logs/access.log") as f:
        line = f.readline()
        print(line)


if __name__ == "__main__":
    main()
