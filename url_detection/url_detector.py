from urllib.parse import urlparse
import ipaddress


def analyze_url(url):
    parsed = urlparse(url)

    result = {
        "url": url,
        "is_https": parsed.scheme == "https",
        "domain": parsed.netloc,
        "suspicious": False,
        "reasons": []
    }

    # Check if URL has HTTPS
    if parsed.scheme != "https":
        result["suspicious"] = True
        result["reasons"].append("URL does not use HTTPS")

    # Check for @ symbol
    if "@" in url:
        result["suspicious"] = True
        result["reasons"].append("URL contains @ symbol")
            # Check if domain is an IP address
    try:
        ipaddress.ip_address(parsed.hostname)
        result["suspicious"] = True
        result["reasons"].append("URL uses an IP address instead of a domain")
    except ValueError:
        pass

    # Check for very long URLs
    if len(url) > 100:
        result["suspicious"] = True
        result["reasons"].append("URL is unusually long")
            # Check for suspicious keywords
    suspicious_keywords = [
        "login",
        "verify",
        "update",
        "secure",
        "account",
        "bank",
        "kyc",
        "payment",
        "refund"
    ]

    url_lower = url.lower()

    for keyword in suspicious_keywords:
        if keyword in url_lower:
            result["suspicious"] = True
            result["reasons"].append(
                f"URL contains suspicious keyword: {keyword}"
            )

    return result


if __name__ == "__main__":
    test_url = input("Enter a URL: ")
    result = analyze_url(test_url)

    print("\nURL Analysis")
    print("------------")
    print("URL:", result["url"])
    print("Domain:", result["domain"])
    print("HTTPS:", result["is_https"])
    print("Suspicious:", result["suspicious"])

    if result["reasons"]:
        print("Reasons:")
        for reason in result["reasons"]:
            print("-", reason)