import requests
import hashlib
from logger_config import get_logger

logger = get_logger(__name__)

pwnedpassword_api="https://api.pwnedpasswords.com/range/"

def get_pwned_passwords(password_to_check):
    # Prefix needs to be encoded as a hexadecimal string before making the request
    # Convert the prefix to a hexadecimal string
    pw_hexadecimal = hashlib.sha1(password_to_check.encode('utf-8')).hexdigest()

    # Split the SHA-1 hash into the first 5 characters (prefix) and the remaining characters (tail)
    pw_hex_first5digits, tails = pw_hexadecimal[:5], pw_hexadecimal[5:]


    # Make the request to the Pwned Passwords API using the prefix
    response = requests.get(pwnedpassword_api + pw_hex_first5digits)
    
    # Log the api call
    logger.info(f"API call made to: {pwnedpassword_api + pw_hex_first5digits}")

    if response.status_code != 200:
        logger.error(f"Error fetching data: {response.status_code} {response.content}")
        raise RuntimeError(f"Error fetching data: {response.status_code} {response.content}")
    else: 
        response_text = response.text

        # put response text into a dictionary with the tail as the key and the count as the value 
        pwned_dict = {}
        for line in response_text.splitlines():
            tail, count = line.split(':')
            pwned_dict[tail] = int(count)

        return pwned_dict.get(tails.upper(), 0)

def main(args):
    if len(args) != 2:
        print("Usage: python checkpassword.py <password_to_check>")
        return
    password_to_check = args[1]
    try:
        result = get_pwned_passwords(password_to_check)
        print(result)
  
    except RuntimeError as e:
        print(f"Runtime error occurred: {e}")

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))

