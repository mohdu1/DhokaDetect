from urllib.parse import urlparse
import difflib
import ipaddress
import json


def detect_typosquatting(url):
    parsed = urlparse(url)
    domain = parsed.hostname

    if domain and domain.startswith("www."):
        domain = domain[4:]

    if not domain:
        return {
            "typosquatting": False,
            "matched_brand": None,
            "similarity": 0.0
        }

    brands = [
        "google.com",
        "microsoft.com",
        "amazon.com",
        "paypal.com",
        "paytm.com",
        "sbi.co.in",
        "hdfcbank.com",
        "icicibank.com"
    ]

    # Check whether a known brand name appears in the domain
    for brand in brands:
        brand_name = brand.split(".")[0]

        if brand_name in domain and domain != brand:
            return {
                "typosquatting": True,
                "matched_brand": brand,
                "similarity": 1.0
            }

    # Check for domains that closely resemble a known brand
    best_brand = None
    best_similarity = 0.0

    for brand in brands:
        similarity = difflib.SequenceMatcher(
            None, domain, brand
        ).ratio()

        if similarity > best_similarity:
            best_similarity = similarity
            best_brand = brand

    is_suspicious = (
        best_similarity >= 0.80
        and domain != best_brand
    )

    return {
        "typosquatting": is_suspicious,
        "matched_brand": best_brand if is_suspicious else None,
        "similarity": round(best_similarity, 2)
    }


def extract_features(url):
    parsed = urlparse(url)

    features = {
        "url_length": len(url),
        "special_characters": sum(
            1 for char in url if char in "@-_?=&%"
        ),
        "subdomain_count": len(parsed.hostname.split(".")) - 2
        if parsed.hostname else 0,
        "uses_https": parsed.scheme == "https"
    }

    return features


def calculate_risk_score(url):
    parsed = urlparse(url)

    score = 0.0
    reasons = []

    # No HTTPS
    if parsed.scheme != "https":
        score += 0.20
        reasons.append("No HTTPS")

    # Very long URL
    if len(url) > 100:
        score += 0.15
        reasons.append("Very long URL")

    # Special characters
    special_count = sum(
        1 for char in url if char in "@-_?=&%"
    )

    if special_count >= 5:
        score += 0.15
        reasons.append("Many special characters")

    # IP address
    try:
        ipaddress.ip_address(parsed.hostname)
        score += 0.25
        reasons.append("IP address used as domain")
    except ValueError:
        pass

    # Suspicious keywords
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
    found_keywords = []

    for keyword in suspicious_keywords:
        if keyword in url_lower:
            found_keywords.append(keyword)

    if found_keywords:
        score += 0.15
        reasons.append(
            "Suspicious keywords: " + ", ".join(found_keywords)
        )

    # Typosquatting
    typo_result = detect_typosquatting(url)

    if typo_result["typosquatting"]:
        score += 0.25
        reasons.append(
            "Possible typosquatting of "
            + typo_result["matched_brand"]
        )

    score = min(score, 1.0)

    return {
        "risk_score": round(score, 2),
        "reasons": reasons
    }


if __name__ == "__main__":
    test_url = input("Enter a URL: ")

    result = calculate_risk_score(test_url)

    output = {
        "url": test_url,
        "risk_score": result["risk_score"],
        "reasons": result["reasons"]
    }

    print(json.dumps(output, indent=2))