import requests
import json
import sys


def send_verification_code(country_code: str, national_number: str, bearer_token: str) -> dict:
    """Wysyła kod weryfikacyjny SMS na podany numer telefonu."""

    url = "https://super-account.spapp.zabka.pl"

    headers = {
        "host": "super-account.spapp.zabka.pl",
        "content-type": "application/json",
        "accept": "multipart/mixed;deferSpec=20220824,application/graphql-response+json,application/json",
        "apollographql-client-version": "4.41.0+14656",
        "authorization": f"Bearer {bearer_token}",
        "priority": "u=3, i",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "pl-PL,pl;q=0.9",
        "x-apollo-operation-type": "mutation",
        "x-client-key": "l6u0R9biQcbEvZy5UybJxw",
        "apollographql-client-name": "pl.zabka.apb2c-apollo-ios",
        "user-agent": "SuperApp/14656 CFNetwork/3890.100.1 Darwin/27.0.0",
        "x-apollo-operation-name": "SendCode",
    }

    payload = {
        "extensions": {
            "clientLibrary": {
                "name": "apollo-ios",
                "version": "1.25.3"
            }
        },
        "operationName": "SendCode",
        "query": "mutation SendCode($input: SendVerificationCodeInput!) { sendVerificationCode(input: $input) { __typename retryAfterSeconds } }",
        "variables": {
            "input": {
                "phoneNumber": {
                    "countryCode": country_code,
                    "nationalNumber": national_number
                }
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    return response


def main():
    print("=" * 50)
    print("  Żabka SuperApp - Wysyłanie kodu SMS")
    print("=" * 50)
    print()

    # Numer telefonu
    country_code = input("Kod kraju (domyślnie 48): ").strip() or "48"
    national_number = input("Numer telefonu (np. 669536491): ").strip()

    if not national_number:
        print("[BŁĄD] Numer telefonu jest wymagany!")
        sys.exit(1)

    # Bearer token
    bearer_token = input("Bearer token: ").strip()

    if not bearer_token:
        print("[BŁĄD] Bearer token jest wymagany!")
        sys.exit(1)

    print()
    print(f"Wysyłanie kodu na +{country_code} {national_number}...")
    print()

    try:
        response = send_verification_code(country_code, national_number, bearer_token)

        print(f"Status HTTP: {response.status_code}")
        print(f"Headers odpowiedzi:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        print()
        print("Odpowiedź (body):")
        try:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"[BŁĄD] Wystąpił błąd połączenia: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
