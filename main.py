from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from transformers import pipeline
import google.generativeai as genai
import re

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("AVISO: GOOGLE_API_KEY não encontrada nas variáveis de ambiente")

genai.configure(api_key=GOOGLE_API_KEY)

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Iniciando modelo Gemini...")
except Exception as e:
    print(f"Erro ao inicializar modelo: {str(e)}")
    model = None

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def clean_text(text):
    text = re.sub(r'\[Música\]', '', text)
    text = re.sub(r'\[MUSIC\]', '', text)
    text = re.sub(r'\[MUSICA\]', '', text)
    
    text = re.sub(r'^[A-Z\s]+$', '', text, flags=re.MULTILINE)
    
    text = re.sub(r'^PR.*$', '', text, flags=re.MULTILINE)
    
    text = re.sub(r'^(\w+)\s+\1\s*$', '', text, flags=re.MULTILINE)
    
    text = re.sub(r'^\s*\S+\s+\S+\s*$', '', text, flags=re.MULTILINE)
    
    text = re.sub(r'^[\s.,!?]+$', '', text, flags=re.MULTILINE)
    
    text = re.sub(r'\s+', ' ', text)
    
    text = re.sub(r'\n\s*\n', '\n', text)
    
    return text.strip()

def analyze_with_gemini(text):
    if not GOOGLE_API_KEY:
        print("Erro: GOOGLE_API_KEY não configurada")
        return None
        
    if not model:
        print("Erro: Modelo Gemini não inicializado")
        return None
        
    try:
        print("Iniciando análise com Gemini...")
        prompt = f"""Analise esta transcrição de uma pregação e extraia os principais tópicos e versículos bíblicos mencionados.
        Ignore partes de música, avisos e saudações iniciais.
        Ignore partes, como a História da Primeira Igreja Batista de Itapevi. 
        Formate a resposta da seguinte maneira:

        TÓPICOS PRINCIPAIS:
        • [Liste os principais tópicos abordados]

        VERSÍCULOS BÍBLICOS:
        • [Liste os versículos mencionados]

        Aviso sobre as atividades da igreja:
        • [Liste as atividades mencionadas]

        Transcrição:
        {text}
        """
        
        print("Enviando prompt para o Gemini...")
        response = model.generate_content(prompt)
        print("Resposta recebida do Gemini")
        return response.text
    except Exception as e:
        print(f"Erro na chamada do Gemini: {str(e)}")
        print(f"Tipo do erro: {type(e)}")
        return None

def extract_video_id(url):
    try:
        video_id = None
        if 'youtube.com' in url:
            match = re.search(r'v=([^&]+)', url)
            if match:
                video_id = match.group(1)
        elif 'youtu.be' in url:
            video_id = url.split('/')[-1]
        
        if not video_id:
            print("URL do YouTube inválida")
            return None
        return video_id
    except Exception as e:
        print(f"Erro ao processar URL: {str(e)}")
        return None

def analyze_text(text):
    cleaned_text = clean_text(text)
    
    try:
        analysis = analyze_with_gemini(cleaned_text)
        return analysis
    except Exception as e:
        print(f"Erro na análise com Gemini: {str(e)}")
        return None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze")
async def analyze_video(url: str = Form(...)):
    try:
        video_id = extract_video_id(url)
        if not video_id:
            return {"error": "URL do YouTube inválida"}
        
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt'])
        except TranscriptsDisabled:
            print("Este vídeo não possui transcrições habilitadas")
            return {"error": "Este vídeo não possui transcrições habilitadas"}
        except NoTranscriptFound:
            print("Não foi encontrada transcrição para este vídeo")
            return {"error": "Não foi encontrada transcrição para este vídeo"}
        except Exception as e:
            print(f"Erro ao obter transcrição: {str(e)}")
            return {"error": f"Erro ao obter transcrição: {str(e)}"}
        
        transcription = " ".join([entry['text'] for entry in transcript])
        
        if not transcription:
            print("A transcrição está vazia")
            return {"error": "A transcrição está vazia"}
        
        try:
            analysis = analyze_text(transcription)
            if not analysis:
                return {"error": "Não foi possível analisar o conteúdo"}
            
            return {
                "title": "Análise da Pregação",
                "analysis": analysis
            }
        except Exception as e:
            print(f"Erro na análise do conteúdo: {str(e)}")
            return {"error": f"Erro na análise do conteúdo: {str(e)}"}
            
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        return {"error": f"Erro inesperado: {str(e)}"} 