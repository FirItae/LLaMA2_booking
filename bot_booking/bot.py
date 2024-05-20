from transformers import  BitsAndBytesConfig, AutoTokenizer, AutoModelForCausalLM, pipeline

import torch
import telebot
import os

import json
from pathlib import Path


with open("./bot_booking/config.json") as f:
    cfg = json.load(f)
model_path  = Path(cfg["checkpoint"])/"booking"

SYSTEM_MSG = "Your name is Trip Assistant bot. You are a useful assistant as an AI chatbot to complete the tasks of the airline and hotel booking system. You can search, book, cancel and update flights and hotel rooms. The assistant is helpful, resourceful, smart and very friendly. If the user wants, he can talk about anything as soon as the assistant finishes filling in the following fields from the user: username, (when booking an air ticket: place of departure, destination), (when booking a hotel: location, number of stars), travel dates, trip budget. Any additional preferences or constraints the user may have. Get user detail step by step in proper conversion."

# Configuration for quantization
quantization_config = BitsAndBytesConfig(load_in_4bit=True,
                                         bnb_4bit_compute_dtype=torch.float16 )
# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(cfg["checkpoint"])
model = AutoModelForCausalLM.from_pretrained(model_path, quantization_config=quantization_config)
pipe = pipeline("text-generation", model, tokenizer=tokenizer, max_new_tokens=300, temperature=0.1, do_sample=False)

# Limit for chat history
history_limit = 500

# Initialize the Telegram Bot
bot = telebot.TeleBot(cfg["BOT_TOKEN"])

def load_chat_history(chat_id: int) -> list:
    """
    Load chat history from a JSON file for a given chat_id.
    
    Args:
        chat_id (int): The ID of the chat.
        
    Returns:
        list: List of chat history messages.
    """
    filename =  Path(cfg["logs_path"])/f"chat_{chat_id}_history.json"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        return []

def save_chat_history(chat_id: int, history: list) -> None:
    """
    Save chat history to a JSON file for a given chat_id.
    
    Args:
        chat_id (int): The ID of the chat.
        history (list): List of chat history messages.
    """
    filename =Path(cfg["logs_path"])/f"chat_{chat_id}_history.json"
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(history, file, ensure_ascii=False, indent=4)
        
def clear_chat_history(chat_id: int) -> None:
    """
    Clear chat history for a given chat_id.
    
    Args:
        chat_id (int): The ID of the chat.
    """
    filename = Path(cfg["logs_path"])/f"chat_{chat_id}_history.json"
    if os.path.exists(filename):
        os.remove(filename)

@bot.message_handler(commands=["start"])
def start(message: telebot.types.Message)-> None:
    """
    Handler for "/start" command. Sends a welcome message.
    
    Args:
        message (telebot.types.Message): The message object.
    """
    bot.send_message(message.chat.id, "Hello, I am a chatbot for booking hotels and plane tickets. Send me a message to get started.")
    bot.send_message(message.chat.id, "If you want to clear my memory of previous interactions, use /clear_history command.")


    
@bot.message_handler(commands=["clear_history"])
def clear_history(message: telebot.types.Message) -> None:
    """
    Handler for "/clear_history" command. Clears chat history.
    
    Args:
        message (telebot.types.Message): The message object.
    """
    chat_id = message.chat.id
    clear_chat_history(chat_id)
    bot.send_message(chat_id, "Chat history cleared successfully.")

    
@bot.message_handler(content_types="text")
def message_reply(message: telebot.types.Message ) -> None:
    """
    Handler for incoming text messages. Generates a response based on the chat history.
    
    Args:
        message (telebot.types.Message): The message object.
    """
    chat_id = message.chat.id
    chat_history = load_chat_history(chat_id)
    
    # Prepare messages list with system message
    messages = [{
                "role": "system",
                "content": SYSTEM_MSG,
            }]
    # Add previous user and assistant messages from history
    for msg in chat_history:
        messages.append({"role": "user", "content": msg["text"]})
        messages.append({"role": "assistant", "content": msg["assistant"]})
    # Add current user message
    messages.append({"role": "user", "content": message.text})
    
    # Generate response from the model
    response  = pipe(messages)[0]["generated_text"][-1]["content"].split("[INST]")[0]
    
    # Add current interaction to chat history
    chat_history.append({
        "text": message.text,
        "date": message.date,
        "from": {
            "id": message.from_user.id,
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name
        },
        "assistant": response
    })

    # Truncate history if it exceeds the limit
    if len(chat_history) > history_limit:
        chat_history = chat_history[-history_limit:] # keep only last 500 messages
        
    # Save chat history   
    save_chat_history(chat_id, chat_history)
    # Send response to the user
    bot.send_message(chat_id, response)

    

# Start polling for messages
bot.polling(none_stop=True, interval=0)
