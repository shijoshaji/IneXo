CURRENCIES = {
    'INR': {'symbol': '₹', 'locale': 'en_IN', 'format': 'lakhs'},
    'USD': {'symbol': '$', 'locale': 'en_US', 'format': 'millions'},
    'EUR': {'symbol': '€', 'locale': 'en_IE', 'format': 'millions'},
    'GBP': {'symbol': '£', 'locale': 'en_GB', 'format': 'millions'},
    'JPY': {'symbol': '¥', 'locale': 'ja_JP', 'format': 'millions'},
    'AUD': {'symbol': 'A$', 'locale': 'en_AU', 'format': 'millions'},
    'CAD': {'symbol': 'C$', 'locale': 'en_CA', 'format': 'millions'},
    'CHF': {'symbol': 'CHF', 'locale': 'de_CH', 'format': 'millions'},
    'CNY': {'symbol': '¥', 'locale': 'zh_CN', 'format': 'millions'},
    'AED': {'symbol': 'د.إ', 'locale': 'ar_AE', 'format': 'millions'}
}

def format_currency(amount, currency_code='INR'):
    """Format currency with symbol and commas (Rounded to nearest Integer)"""
    currency = CURRENCIES.get(currency_code, CURRENCIES['INR'])
    symbol = currency['symbol']
    
    try:
        # Round to nearest integer
        val = int(round(float(amount)))
        
        if currency_code == 'INR':
            # Indian formatting for integers
            s = str(val)
            r = ",".join([s[x-2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
            return f"{symbol}{r}"
        else:
            # Standard formatting (no decimals)
            return f"{symbol}{val:,.0f}"
    except:
        return f"{symbol}{amount}"

def number_to_words(num, currency_code='INR'):
    """
    Converts a number to words based on currency format.
    INR -> Lakhs/Crores
    Others -> Millions/Billions
    """
    if num == 0:
        return "Zero"
    
    num = int(num)
    currency = CURRENCIES.get(currency_code, CURRENCIES['INR'])
    use_indian_system = currency['format'] == 'lakhs'
    
    under_20 = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
    tens = ['Zero', 'Ten', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
    
    def chunk_to_words(n):
        if n == 0: return []
        if n < 20: return [under_20[n]]
        if n < 100: return [tens[n // 10]] + chunk_to_words(n % 10)
        if n < 1000: return [under_20[n // 100], 'Hundred'] + chunk_to_words(n % 100)
        return []

    parts = []
    
    if use_indian_system:
        # Crores
        crores = num // 10000000
        num = num % 10000000
        if crores > 0:
            parts.extend(chunk_to_words(crores) + ['Crore'])
        
        # Lakhs
        lakhs = num // 100000
        num = num % 100000
        if lakhs > 0:
            parts.extend(chunk_to_words(lakhs) + ['Lakh'])
            
        # Thousands
        thousands = num // 1000
        num = num % 1000
        if thousands > 0:
            parts.extend(chunk_to_words(thousands) + ['Thousand'])
    else:
        # Billions
        billions = num // 1000000000
        num = num % 1000000000
        if billions > 0:
            parts.extend(chunk_to_words(billions) + ['Billion'])
            
        # Millions
        millions = num // 1000000
        num = num % 1000000
        if millions > 0:
            parts.extend(chunk_to_words(millions) + ['Million'])
            
        # Thousands
        thousands = num // 1000
        num = num % 1000
        if thousands > 0:
            parts.extend(chunk_to_words(thousands) + ['Thousand'])
            
    # Remaining hundreds/tens
    if num > 0:
        parts.extend(chunk_to_words(num))
        
    return " ".join(parts)

def decode_signature(encoded_str):
    """Decode the obfuscated signature"""
    import base64
    try:
        return base64.b64decode(encoded_str).decode('utf-8')
    except:
        return ""
