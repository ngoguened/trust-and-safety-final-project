import re
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from string import punctuation

PHONE_REGEX = r'(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?:[-. ]*(?:ext|x|ext\.)\s*(\d+))?'
TELEGRAM_REGEX = r't\.me/[a-zA-Z0-9_]+'
EMOJI_REGEX = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]+'

def fix(text): return text.replace("i'm", "i am").replace("don't", "do not") 
STOP_WORDS = set(stopwords.words("english")) - {"not", "no"} 
LEMMATIZER = WordNetLemmatizer()

def preprocess_text_single(text: str) -> str:
    """Applies the full preprocessing chain to a single string for prediction."""
    
    if not isinstance(text, str):
        text = ""
        
    # 1. Lowercase and Contractions
    text = text.lower()
    text = fix(text) # Expand contractions

    # 2. Token Replacements (Order matters!)
    text = re.sub(r'http\S+|www\.\S+', '<URL>', text)
    text = re.sub(r't\.me/[a-zA-Z0-9_]+', '<TELEGRAM_HANDLE>', text, flags=re.IGNORECASE)
    text = re.sub(PHONE_REGEX, '<PHONE_NUMBER>', text)
    text = re.sub(r'@[\\w_]+', '<MENTION>', text)
    text = re.sub(r'\b\d+\b', '<NUM>', text)
    text = re.sub(EMOJI_REGEX, '<EMOJI>', text)
    
    # 3. Tokenize
    tokens = word_tokenize(text)
    
    # 4. Remove Punctuation and Empty strings
    tokens = [
        ''.join([c for c in word if c not in punctuation])
        for word in tokens if ''.join([c for c in word if c not in punctuation])
    ]
    
    # 5. Stopword Removal (except not/no)
    tokens = [w for w in tokens if w not in STOP_WORDS] 
    
    # 6. Lemmatization
    tokens = [LEMMATIZER.lemmatize(w) for w in tokens]
    
    # 7. Rejoin into cleaned text (ready for vectorizer)
    return " ".join(tokens)