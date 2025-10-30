from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import asyncio
import json
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection with fallback
try:
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
except KeyError as e:
    print(f"Warning: Missing environment variable {e}. Using default MongoDB settings.")
    mongo_url = "mongodb://localhost:27017"
    client = AsyncIOMotorClient(mongo_url)
    db = client["sentiment_analysis"]

# JWT Configuration
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'sentiment_analysis_super_secret_jwt_key_2025')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI(title="Sentiment Analysis API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Pydantic Models
class User(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class SentimentAnalysisRequest(BaseModel):
    text: str
    include_emotions: bool = True

class SentimentResult(BaseModel):
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    text: str
    sentiment_score: float  # -1 to 1
    sentiment_label: str    # positive, negative, neutral
    emotions: Dict[str, float]  # emotion scores
    keywords: List[str]     # keywords for image search
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SentimentAnalysisResponse(BaseModel):
    analysis: SentimentResult
    message: str

# Authentication utilities
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"email": email})
    if user is None:
        raise credentials_exception
    return User(**user)

# Simple sentiment analysis (without external AI service)
def analyze_sentiment_simple(text: str) -> Dict:
    """Simple rule-based sentiment analysis"""
    
    # Positive words
    positive_words = [
    'happy', 'joy', 'great', 'amazing', 'wonderful', 'fantastic', 'excellent',
    'good', 'love', 'awesome', 'brilliant', 'perfect', 'beautiful', 'nice',
    'excited', 'thrilled', 'pleased', 'delighted', 'satisfied', 'grateful',

    'cheerful', 'smile', 'hopeful', 'lucky', 'encouraging', 'gentle', 'kind',
    'energetic', 'free', 'generous', 'jovial', 'optimistic', 'peaceful',
    'radiant', 'relaxed', 'secure', 'strong', 'sunny', 'uplifting', 'vibrant',
    'warm', 'welcoming', 'wise', 'zesty', 'blessed', 'bubbly', 'caring',
    'carefree', 'charming', 'compassionate', 'confident', 'congenial',
    'content', 'cooperative', 'creative', 'daring', 'dynamic', 'eager', 'easygoing',
    'ecstatic', 'empathetic', 'enlightened', 'enthralled', 'euphoric', 'exuberant',
    'faithful', 'fascinating', 'fearless', 'friendly', 'funny', 'genuine', 'glad',
    'glowing', 'gracious', 'happy-go-lucky', 'harmonious', 'hearty', 'helpful',
    'honest', 'hope-filled', 'idealistic', 'incredible', 'independent', 'inspired',
    'intelligent', 'jolly', 'joyous', 'just', 'keen', 'kind-hearted', 'laughing',
    'light-hearted', 'lively', 'lovable', 'loving', 'luminous', 'mindful', 'miraculous',
    'motivated', 'noble', 'open-hearted', 'optimism', 'organized', 'outgoing',
    'passionate', 'patient', 'peace-loving', 'playful', 'polite', 'positive',
    'powerful', 'productive', 'promising', 'prosperous', 'proud', 'radiating',
    'reliable', 'resilient', 'resourceful', 'respectful', 'sanguine', 'secure',
    'sensational', 'serene', 'sincere', 'skilled', 'smart', 'sparkling', 'spirited',
    'spontaneous', 'strong-willed', 'supportive', 'sweet', 'thoughtful', 'thriving',
    'trustworthy', 'unbreakable', 'united', 'upbeat', 'vital', 'wealthy', 'wise',
    'witty', 'worthy', 'zealous', 'zesty', 'appreciated', 'approved', 'balanced',
    'best', 'better', 'blissful', 'bountiful', 'bright', 'buoyant', 'calm', 'capable',
    'celebrated', 'classic', 'clean', 'clear', 'comforted', 'committed', 'competent',
    'complimentary', 'contented', 'cool', 'courageous', 'creative', 'crisp', 'dazzling',
    'decisive', 'dedicated', 'delicious', 'dependable', 'devoted', 'distinguished',
    'dynamic', 'eager', 'easy', 'effective', 'efficient', 'elegant', 'empowered',
    'encouraged', 'endearing', 'engaged', 'enjoyable', 'enriched', 'enthusiastic',
    'equal', 'essential', 'ethical', 'excellent', 'exceptional', 'exhilarating',
    'expansive', 'fabulous', 'fair', 'faith-filled', 'famished', 'famous', 'fashionable',
    'fit', 'flawless', 'flexible', 'focused', 'fortunate', 'free-spirited', 'friendly',
    'fruitful', 'fun', 'gallant', 'generous', 'gifted', 'glorious', 'good-hearted',
    'graceful', 'grateful-hearted', 'handsome', 'harmonious', 'heartwarming', 'heavenly',
    'helpful-hearted', 'honorable', 'hope-filled', 'ideal', 'imaginative', 'impressive',
    'influential', 'ingenious', 'innovative', 'inspiring', 'intuitive', 'inventive',
    'invigorated', 'irresistible', 'jubilant', 'keen-eyed', 'kindred', 'knowledgeable',
    'laughable', 'learned', 'legendary', 'liberated', 'light', 'likeable', 'lionhearted',
    'lively-hearted', 'logical', 'lovely', 'lucid', 'luxurious', 'magical', 'magnificent',
    'mind-expanding', 'miraculous-hearted', 'motivating', 'natural', 'neat', 'nifty',
    'noble-hearted', 'nurturing', 'open-minded', 'original', 'outstanding', 'passionate-hearted',
    'peaceful-hearted', 'perceptive', 'perfected', 'pleasant', 'pleasing', 'poised', 'polished',
    'positive-thinking', 'powerful-hearted', 'precious', 'prepared', 'prestigious', 'profound',
    'prosperous-hearted', 'proud-hearted', 'radiant-hearted', 'refined', 'rejuvenated', 'relaxed-hearted',
    'reliable-hearted', 'remarkable', 'renowned', 'resilient-hearted', 'resourceful-hearted', 'respectable',
    'rewarded', 'rich', 'romantic', 'safe', 'satisfying', 'secure-hearted', 'sensuous', 'serene-hearted',
    'sharp', 'shining', 'sincere-hearted', 'skilled-hearted', 'smart-hearted', 'smooth', 'sparkling-hearted',
    'spirited-hearted', 'spiritual', 'splendid', 'stable', 'steady', 'stellar', 'strong-hearted', 'successful',
    'superb', 'supportive-hearted', 'sweet-hearted', 'thoughtful-hearted', 'thriving-hearted', 'trusting',
    'trustworthy-hearted', 'unshakeable', 'upbeat-hearted', 'valiant', 'vibrant-hearted', 'victorious',
    'vital-hearted', 'well', 'wise-hearted', 'witty-hearted', 'wonderstruck', 'worthy-hearted'
    ]

    
    # Negative words
    negative_words = [
    'sad', 'angry', 'terrible', 'awful', 'horrible', 'hate', 'bad',
    'disappointed', 'frustrated', 'annoyed', 'upset', 'depressed',
    'worried', 'anxious', 'scared', 'angry', 'furious', 'disgusted',

    'guilty', 'shameful', 'embarrassed', 'lonely', 'miserable', 'hopeless',
    'powerless', 'ashamed', 'fearful', 'regretful', 'uneasy', 'nervous',
    'resentful', 'bitter', 'grief', 'heartbroken', 'jealous', 'insecure',
    'defeated', 'melancholy', 'distressed', 'pessimistic', 'overwhelmed',
    'panicked', 'troubled', 'resenting', 'hurt', 'confused', 'disheartened',
    'tired', 'burnt-out', 'drained', 'neglected', 'worthless', 'sick',
    'discontented', 'distraught', 'intimidated', 'trapped', 'persecuted',
    'pressured', 'offended', 'rejected', 'stressed', 'ashamed-faced',
    'bewildered', 'chained', 'clumsy', 'critical', 'cynical', 'defensive',
    'demoralized', 'dismayed', 'displeased', 'embattled', 'empty', 'envious',
    'fear-stricken', 'frightened', 'frozen', 'hopelessness', 'humiliated',
    'impatient', 'indifferent', 'ineffective', 'infuriated', 'injured',
    'isolated', 'jealous-hearted', 'low', 'mad', 'melancholic', 'menacing',
    'mindless', 'mournful', 'numb', 'obnoxious', 'off-key', 'overworked',
    'paralyzed', 'perplexed', 'pained', 'resentful-hearted', 'restless',
    'saddened', 'shaky', 'sickened', 'sorrowful', 'spiteful', 'stiff',
    'sullen', 'suspicious', 'tense', 'tormented', 'troubled-hearted',
    'uncertain', 'unhappy', 'unloved', 'unmotivated', 'unwanted', 'vulnerable',
    'weak', 'weepy', 'withdrawn', 'worried-faced', 'worst', 'wretched',
    'agitated', 'alarmed', 'alienated', 'angst', 'apprehensive', 'ashamed-faced',
    'atrocious', 'awkward', 'baffled', 'broken', 'burdened', 'chaotic',
    'cheated', 'claustrophobic', 'coerced', 'combative', 'complicated', 'conflicted',
    'contradicted', 'cranky', 'crushed', 'damaged', 'dangerous', 'dark',
    'dazed', 'dejected', 'delayed', 'denied', 'deprived', 'derailed', 'desperate',
    'deteriorating', 'devastated', 'disappointed-hearted', 'disconnected',
    'dishonored', 'disillusioned', 'dismal', 'disrespected', 'disturbed',
    'doubtful', 'dragged', 'dreary', 'embarrassed-faced', 'empty-handed',
    'enraged', 'exhausted', 'fail', 'fearsome', 'feeble', 'forlorn',
    'forsaken', 'frozen-hearted', 'frightened-faced', 'frustrated-hearted',
    'grieving', 'groaning', 'grim', 'grimacing', 'grumpy', 'harassed',
    'heartache', 'heavy-hearted', 'helpless', 'hostile', 'horrified',
    'hurt-hearted', 'imperfect', 'imprisoned', 'inadequate', 'incompetent',
    'incomplete', 'indecisive', 'ineffective', 'infuriating', 'insensitive',
    'insignificant', 'insulted', 'intolerant', 'irritated', 'isolated-faced',
    'jaded', 'lackluster', 'lame', 'letdown', 'lifeless', 'lost', 'lousy',
    'manipulated', 'menacing-faced', 'mind-numbing', 'morose', 'mournful-hearted',
    'negative', 'numb-hearted', 'overbearing', 'overlooked', 'painful',
    'paralyzed-hearted', 'pathetic', 'perilous', 'pessimism-filled', 'powerless-faced',
    'prejudiced', 'regret', 'rejected-faced', 'repulsed', 'resentful-faced',
    'restless-hearted', 'sad-faced', 'sacrificed', 'scorned', 'selfish',
    'sensitive', 'separated', 'shaky-faced', 'shamed', 'shunned', 'sick-hearted',
    'silent', 'sinking', 'skeptical', 'sluggish', 'slow', 'smothered', 'spiteful-faced',
    'stagnant', 'stressed-faced', 'struggling', 'suffering', 'suffocated', 'sullen-faced',
    'tarnished', 'threatened', 'tormented-faced', 'trapped-faced', 'uncomfortable',
    'undervalued', 'unfair', 'unfocused', 'unfulfilled', 'unhappy-faced',
    'unimportant', 'unlucky', 'unresponsive', 'unsatisfied', 'unsure', 'uptight',
    'useless', 'vacant', 'vexed', 'violated', 'weak-hearted', 'wounded', 'worried-hearted'
    ]

    
    # Neutral words
    neutral_words = [
    'okay', 'fine', 'normal', 'regular', 'standard', 'average', 'typical',

    'usual', 'common', 'mediocre', 'moderate', 'fair', 'so-so', 'plain',
    'steady', 'routine', 'middle', 'middle-of-the-road', 'basic', 'satisfactory',
    'indifferent', 'neutral', 'middle-aged', 'balanced', 'mild', 'customary',
    'expected', 'average-looking', 'unremarkable', 'general', 'conventional',
    'ordinary', 'acceptable', 'manageable', 'moderate-paced', 'nothing-special',
    'humdrum', 'uneventful', 'nonchalant', 'undisturbed', 'unchanged',
    'plain-vanilla', 'modest', 'non-descript', 'functional', 'matter-of-fact',
    'passable', 'mid-level', 'straightforward', 'adequate', 'so-so', 'run-of-the-mill',
    'routine-looking', 'regular-paced', 'standard-issue', 'middle-range',
    'soft', 'unassuming', 'neutral-toned', 'typical-behavior', 'non-threatening',
    'unbiased', 'uninspired', 'nondescript', 'detached', 'reserved', 'quiet',
    'unexcited', 'placid', 'still', 'steady-handed', 'plain-speaking', 'plain-faced',
    'habitual', 'unchallenging', 'uncomplicated', 'subdued', 'lackluster',
    'non-reactive', 'passive', 'steady-going', 'lifeless', 'unexpressive',
    'undramatic', 'calm', 'matter-of-fact', 'unhurried', 'low-key', 'level-headed',
    'sleepy', 'subtle', 'soft-spoken', 'mellow', 'uneventful', 'unaffected',
    'even-tempered', 'temperate', 'mild-mannered', 'quiet-minded', 'still-faced',
    'collected', 'composed', 'conservative', 'measured', 'bland', 'placated',
    'relaxed', 'easy-going', 'undemanding', 'steadfast', 'timid', 'shy',
    'thoughtful', 'compliant', 'agreeable', 'apathetic', 'oblivious', 'nonchalant',
    'unconcerned', 'reserved', 'controlled', 'calculated', 'plain-patterned',
    'commonplace', 'unpretentious', 'bare', 'clean', 'inconspicuous', 'plainly',
    'haphazard', 'random', 'unchanged-faced', 'dull', 'colorless', 'unvaried',
    'level', 'even', 'regular-shaped', 'prosaic', 'steady-paced', 'repetitive',
    'unvarnished', 'undistinguished', 'low-profile', 'routine-task', 'non-dramatic',
    'subdued-tone', 'distant', 'reserved-tone', 'mindless', 'monotone', 'simple',
    'reliable', 'unwavering', 'plain-sounding', 'ordinary-faced', 'featureless',
    'modulated', 'even-handed', 'unremarked', 'unnoticed', 'silent', 'mundane',
    'unexcitable', 'unflustered', 'non-reactive-faced', 'neutral-expressed',
    'undramatic-faced', 'low-energy', 'without-flair', 'steady-expression',
    'plain-featured', 'stolid', 'calm-faced', 'unimpressed', 'self-contained',
    'unmoved', 'unpretentious-faced', 'mild-looking', 'soft-featured'
    ]

    
    text_lower = text.lower()
    words = text_lower.split()
    
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    neutral_count = sum(1 for word in words if word in neutral_words)
    
    # Calculate sentiment score
    total_sentiment_words = positive_count + negative_count
    if total_sentiment_words == 0:
        sentiment_score = 0.0
        sentiment_label = "neutral"
    else:
        sentiment_score = (positive_count - negative_count) / max(len(words), 1)
        sentiment_score = max(-1.0, min(1.0, sentiment_score * 2))  # Scale to -1 to 1
        
        if sentiment_score > 0.1:
            sentiment_label = "positive"
        elif sentiment_score < -0.1:
            sentiment_label = "negative" 
        else:
            sentiment_label = "neutral"
    
    # Generate emotions based on sentiment
    base_emotions = {
        "joy": 0.1,
        "sadness": 0.1,
        "anger": 0.1,
        "fear": 0.1,
        "surprise": 0.1,
        "disgust": 0.1,
        "trust": 0.3,
        "anticipation": 0.2
    }
    
    if sentiment_label == "positive":
        base_emotions["joy"] = 0.8 + random.uniform(-0.1, 0.1)
        base_emotions["trust"] = 0.6 + random.uniform(-0.1, 0.1)
        base_emotions["anticipation"] = 0.5 + random.uniform(-0.1, 0.1)
        keywords = ["happiness", "joy", "celebration", "success", "bright"]
    elif sentiment_label == "negative":
        base_emotions["sadness"] = 0.7 + random.uniform(-0.1, 0.1)
        base_emotions["anger"] = 0.4 + random.uniform(-0.1, 0.1)
        base_emotions["fear"] = 0.3 + random.uniform(-0.1, 0.1)
        keywords = ["sadness", "melancholy", "dark", "storm", "solitude"]
    else:
        base_emotions["trust"] = 0.5
        keywords = ["calm", "peaceful", "serene", "balance", "neutral"]
    
    # Normalize emotions to ensure they're between 0 and 1
    base_emotions = {k: max(0.0, min(1.0, v)) for k, v in base_emotions.items()}
    
    return {
        "sentiment_score": sentiment_score,
        "sentiment_label": sentiment_label,
        "emotions": base_emotions,
        "keywords": keywords[:5]  # Limit to 5 keywords
    }

# Alternative: Use OpenAI API if available
async def analyze_sentiment_with_openai(text: str) -> Dict:
    """Analyze sentiment using OpenAI API (if available)"""
    try:
        import openai
        
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            raise ValueError("OpenAI API key not found")
        
        client = openai.OpenAI(api_key=openai_api_key)
        
        system_message = """You are a sentiment analysis expert. Analyze the given text and return your response in this EXACT JSON format:
{
    "sentiment_score": -0.5,
    "sentiment_label": "negative",
    "emotions": {
        "joy": 0.1,
        "sadness": 0.7,
        "anger": 0.2,
        "fear": 0.3,
        "surprise": 0.1,
        "disgust": 0.1,
        "trust": 0.2,
        "anticipation": 0.1
    },
    "keywords": ["melancholy", "solitude", "contemplation"]
}

Rules:
- sentiment_score: float between -1 (very negative) and 1 (very positive)
- sentiment_label: "positive", "negative", or "neutral"
- emotions: 8 emotions with scores 0-1
- keywords: 3-5 words for image search based on sentiment
- Return ONLY valid JSON, no additional text"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Analyze this text: {text}"}
            ],
            temperature=0.1
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        logging.error(f"OpenAI sentiment analysis failed: {str(e)}")
        # Fall back to simple analysis
        return analyze_sentiment_simple(text)

async def analyze_sentiment_with_ai(text: str) -> Dict:
    """Main sentiment analysis function with fallbacks"""
    try:
        # Try OpenAI first if available
        if os.environ.get('OPENAI_API_KEY'):
            return await analyze_sentiment_with_openai(text)
        else:
            # Fall back to simple analysis
            return analyze_sentiment_simple(text)
    except Exception as e:
        logging.error(f"Error in sentiment analysis: {str(e)}")
        # Final fallback
        return analyze_sentiment_simple(text)

# API Routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_create: UserCreate):
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_create.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and create user
        hashed_password = get_password_hash(user_create.password)
        user_dict = {
            "user_id": str(uuid.uuid4()),
            "email": user_create.email,
            "name": user_create.name,
            "hashed_password": hashed_password,
            "created_at": datetime.now(timezone.utc)
        }
        
        await db.users.insert_one(user_dict)
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_create.email}, expires_delta=access_token_expires
        )
        
        user = User(**user_dict)
        return Token(access_token=access_token, token_type="bearer", user=user)
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@api_router.post("/auth/login", response_model=Token)
async def login(user_login: UserLogin):
    try:
        user = await db.users.find_one({"email": user_login.email})
        if not user or not verify_password(user_login.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_login.email}, expires_delta=access_token_expires
        )
        
        user_obj = User(**user)
        return Token(access_token=access_token, token_type="bearer", user=user_obj)
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@api_router.post("/sentiment/analyze", response_model=SentimentAnalysisResponse)
async def analyze_sentiment(
    request: SentimentAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """Analyze sentiment of provided text"""
    try:
        if not request.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text cannot be empty"
            )
        
        # Perform sentiment analysis
        analysis_result = await analyze_sentiment_with_ai(request.text)
        
        # Create sentiment result
        sentiment_result = SentimentResult(
            user_id=current_user.user_id,
            text=request.text,
            sentiment_score=analysis_result["sentiment_score"],
            sentiment_label=analysis_result["sentiment_label"],
            emotions=analysis_result["emotions"],
            keywords=analysis_result["keywords"]
        )
        
        # Store in database
        await db.sentiment_analyses.insert_one(sentiment_result.dict())
        
        return SentimentAnalysisResponse(
            analysis=sentiment_result,
            message="Sentiment analysis completed successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Sentiment analysis error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sentiment analysis failed"
        )

@api_router.get("/sentiment/history", response_model=List[SentimentResult])
async def get_sentiment_history(
    current_user: User = Depends(get_current_user),
    limit: int = 10
):
    """Get user's sentiment analysis history"""
    try:
        analyses = await db.sentiment_analyses.find({
            "user_id": current_user.user_id
        }).sort("created_at", -1).limit(limit).to_list(length=None)
        
        return [SentimentResult(**analysis) for analysis in analyses]
    
    except Exception as e:
        logging.error(f"History retrieval error: {str(e)}")
        return []

@api_router.get("/sentiment/stats", response_model=Dict)
async def get_sentiment_stats(current_user: User = Depends(get_current_user)):
    """Get user's sentiment analysis statistics"""
    try:
        pipeline = [
            {"$match": {"user_id": current_user.user_id}},
            {"$group": {
                "_id": "$sentiment_label",
                "count": {"$sum": 1},
                "avg_score": {"$avg": "$sentiment_score"}
            }}
        ]
        
        stats = await db.sentiment_analyses.aggregate(pipeline).to_list(length=None)
        
        # Format stats
        formatted_stats = {
            "total_analyses": sum(stat["count"] for stat in stats),
            "sentiment_distribution": {
                stat["_id"]: {
                    "count": stat["count"],
                    "average_score": round(stat["avg_score"], 2)
                } for stat in stats
            }
        }
        
        return formatted_stats
    
    except Exception as e:
        logging.error(f"Stats retrieval error: {str(e)}")
        return {
            "total_analyses": 0,
            "sentiment_distribution": {}
        }

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}

# Root endpoint for connection testing
@app.get("/")
async def root():
    return {
        "message": "Sentiment Analysis API",
        "status": "running",
        "version": "1.0.0"
    }

# Include the router in the main app
app.include_router(api_router)

# CORS configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_credentials=True,
#     allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_db_client():
    try:
        # Test database connection
        await client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
        
        # Create indexes for better performance
        await db.users.create_index("email", unique=True)
        await db.sentiment_analyses.create_index([("user_id", 1), ("created_at", -1)])
        logger.info("Database indexes created")
    except Exception as e:
        logger.warning(f"Database connection failed: {str(e)}. Some features may not work.")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)