import os
import json
import psycopg2
import re
from flask import Flask, request, send_from_directory
from twilio.twiml.messaging_response import MessagingResponse
import requests
from google.cloud import speech
from dotenv import load_dotenv
from pydub import AudioSegment
import google.generativeai as genai
import matplotlib
#backend 
matplotlib.use('Agg')
import matplotlib.pyplot as plt

load_dotenv()

#AUTHENTICATION 
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
DATABASE_URL = os.environ.get('DATABASE_URL')
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

user_last_meal = {}

app = Flask(__name__)

#CHART GENERATION
def generate_summary_chart(protein, carbs, fat):
    """Generates a pie chart of macronutrients and saves it as a file."""
    try:
        labels = 'Protein', 'Carbs', 'Fat'
        sizes = [protein, carbs, fat]
        sizes = [max(0, s) for s in sizes]
        
        if not any(sizes):
            print("No macro data to plot, skipping chart generation.")
            return None

        explode = [0, 0, 0]
        if max(sizes) > 0:
            explode[sizes.index(max(sizes))] = 0.1

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
                shadow=True, startangle=90, colors=['#ff9999','#66b3ff','#99ff99'])
        ax1.axis('equal')  
        
        chart_path = 'static/summary_chart.png'
        if not os.path.exists('static'):
            os.makedirs('static')
        plt.savefig(chart_path)
        plt.close(fig1) 
        
        base_url = request.url_root
        return f"{base_url}{chart_path}"
    except Exception as e:
        print(f"Error generating chart: {e}")
        return None

#ROUTE TO SERVE THE STATIC CHART IMAGE
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

#DATABASE AND AI 
def get_daily_summary(user_number):
    """Queries the database and returns a summary and a chart URL."""
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        query = "SELECT food_item, quantity, calories, protein_g, carbs_g, fat_g FROM food_logs WHERE user_number = %s AND created_at >= date_trunc('day', NOW())"
        cur.execute(query, (user_number,))
        records = cur.fetchall()
        cur.close()

        if not records:
            return "You haven't logged any food yet today.", None

        total_calories, total_protein, total_carbs, total_fat = 0, 0, 0, 0
        food_list = ""
        for record in records:
            food_list += f"\n- {record[1]} {record[0]} (~{record[2]} kcal)"
            total_calories += record[2] or 0
            total_protein += record[3] or 0
            total_carbs += record[4] or 0
            total_fat += record[5] or 0
            
        summary_message = f"📊 *Your Summary for Today:*\n"
        summary_message += food_list
        summary_message += f"\n\n*Totals:*\n🔥 Calories: *{total_calories:.0f} kcal*\n💪 Protein: *{total_protein:.1f} g*\n🍞 Carbs: *{total_carbs:.1f} g*\n🥑 Fat: *{total_fat:.1f} g*"
        
        chart_url = generate_summary_chart(total_protein, total_carbs, total_fat)
        
        return summary_message, chart_url
    except Exception as e:
        print(f"Database query or chart generation error: {e}")
        return "Sorry, I couldn't retrieve your summary due to an error.", None
    finally:
        if conn is not None:
            conn.close()

def save_meal_to_db(user_number, meal_data):
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        for item in meal_data['items']:
            cur.execute(
                """INSERT INTO food_logs (user_number, food_item, quantity, calories, protein_g, carbs_g, fat_g) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (user_number, item.get('food'), item.get('quantity'), item.get('calories'), item.get('protein_g'), item.get('carbs_g'), item.get('fat_g'))
            )
        conn.commit()
        cur.close()
        return True
    except Exception as e:
        print(f"Database save error: {e}")
        return False
    finally:
        if conn is not None:
            conn.close()

def get_nutritional_info(text):
    """Sends text to Gemini and gets back structured nutritional data."""
    prompt = """
    Your task is to act as a nutrition analysis API.
    Analyze the meal described in the text and provide the output ONLY in a valid JSON format.
    Your entire response must be a single JSON object. Do not include any text, explanations, greetings, or markdown formatting like ```json before or after the JSON object.

    The JSON object must have a single key "items", which is a list.
    Each object in the "items" list must have the following keys: "food", "quantity", "calories", "protein_g", "carbs_g", and "fat_g".

    Analyze this text:
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        full_prompt = prompt + text
        response = model.generate_content(full_prompt, generation_config={'temperature': 0.0})
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            print("No valid JSON found in the Gemini response.")
            return None
    except Exception as e:
        print(f"Error calling Gemini or parsing JSON: {e}")
        return None

def transcribe_audio(audio_url):
    """Downloads, converts, and transcribes an audio file."""
    try:
        audio_content = requests.get(audio_url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)).content
        with open("temp_audio.ogg", "wb") as f: f.write(audio_content)
        audio = AudioSegment.from_ogg("temp_audio.ogg").set_sample_width(2)
        audio.export("converted_audio.wav", format="wav")
        with open("converted_audio.wav", "rb") as f: wav_content = f.read()
        client = speech.SpeechClient()
        audio_to_transcribe = speech.RecognitionAudio(content=wav_content)
        config = speech.RecognitionConfig(encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16, language_code="en-IN")
        response = client.recognize(config=config, audio=audio_to_transcribe)
        return response.results[0].alternatives[0].transcript if response.results else None
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

#MAIN WHATSAPP LOGIC
@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    """Main webhook that handles all incoming messages."""
    resp = MessagingResponse()
    incoming_msg = request.values.get('Body', '').lower().strip()
    user_number = request.values.get('From', '')

    transcribed_text = None
    if 'NumMedia' in request.values and int(request.values['NumMedia']) > 0:
        audio_url = request.values.get('MediaUrl0')
        transcribed_text = transcribe_audio(audio_url)
        if transcribed_text:
            incoming_msg = transcribed_text.lower().strip()
    elif incoming_msg:
        transcribed_text = incoming_msg

    summary_keywords = ['/summary', 'summary', 'today', 'how much today?', 'what did i eat']
    is_summary_request = any(keyword in incoming_msg for keyword in summary_keywords)

    if is_summary_request:
        summary_text, chart_url = get_daily_summary(user_number)
        msg = resp.message(summary_text)
        if chart_url:
            msg.media(chart_url)
        return str(resp)

    confirmation_keywords = ['yes', 'y', 'ok', 'save', 'yeah', 'yup']
    if user_number in user_last_meal and incoming_msg in confirmation_keywords:
        if save_meal_to_db(user_number, user_last_meal[user_number]):
            resp.message("✅ Great! I've logged that for you.")
        else:
            resp.message("❌ Sorry, there was an error saving your meal.")
        del user_last_meal[user_number]
        return str(resp)
    
    rejection_keywords = ['no', 'n', 'nope', 'cancel', 'discard']
    if user_number in user_last_meal and incoming_msg in rejection_keywords:
        resp.message("Okay, I've discarded that meal.")
        del user_last_meal[user_number]
        return str(resp) 
    
    if transcribed_text:
        nutritional_data = get_nutritional_info(transcribed_text)
        
        if nutritional_data and 'items' in nutritional_data:
            user_last_meal[user_number] = nutritional_data
            reply_message = "Here's what I found:\n"
            total_calories = 0
            for item in nutritional_data['items']:
                calories = item.get('calories', 0)
                food = item.get('food', 'Unknown')
                quantity = item.get('quantity', '')
                reply_message += f"\n- {quantity} {food} (~{calories} kcal)"
                total_calories += calories
            
            reply_message += f"\n\n*Total: ~{total_calories} kcal*\n\nShould I save this? (Reply Yes/No)"
            resp.message(reply_message)
        else:
            resp.message("Sorry, I couldn't figure out the nutritional info for that. Please try again.")
    else:
        resp.message("Please send a voice note or text message describing your meal.")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)



