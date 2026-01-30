from parser import extract_status, extract_time
from enum import Enum

class Status(Enum):
    OK = 200
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    REQUEST_TIMEOUT = 408
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVALIBLE = 503

def main():
    ok = 0
    noContent = 0
    badRequest = 0
    unauthorized = 0
    forbidden = 0
    notFound = 0
    requestTimeout = 0
    tooManyRequests = 0
    internalServerError = 0
    badGateway = 0
    serviceUnavalible = 0
    
    with open("sample_logs/access.log") as f:
        for line in f:
            ts = extract_time(line)
            status = extract_status(line)
            print(ts)
            match status:
                case Status.OK.value:
                    ok += 1
                case Status.NO_CONTENT.value:
                    noContent += 1
                case Status.BAD_REQUEST.value:
                    badRequest += 1
                case Status.UNAUTHORIZED.value:
                    unauthorized += 1
                case Status.FORBIDDEN.value:
                    forbidden += 1
                case Status.NOT_FOUND.value:
                    notFound += 1
                case Status.REQUEST_TIMEOUT.value:
                    requestTimeout += 1
                case Status.TOO_MANY_REQUESTS.value:
                    tooManyRequests += 1
                case Status.INTERNAL_SERVER_ERROR.value:
                    internalServerError += 1
                case Status.BAD_GATEWAY.value:
                    badGateway += 1
                case Status.SERVICE_UNAVALIBLE.value:
                    serviceUnavalible += 1
                case _:
                    print("Code not controlled")
    

        print("-"*20)
        print(f"OK error: {ok}")
        print(f"No content error: {noContent}")
        print(f"Bad request error: {badRequest}")
        print(f"Unauthorized error: {unauthorized}")
        print(f"Forbidden error: {forbidden}")
        print(f"Not found error: {notFound}")
        print(f"Request timeout error: {requestTimeout}")
        print(f"Too many requests error: {tooManyRequests}")
        print(f"Internal server error: {internalServerError}")
        print(f"Bad gateway error: {badGateway}")
        print(f"Service unavaible error: {serviceUnavalible}")
        print("-"*20)


if __name__ == "__main__":
    main()
