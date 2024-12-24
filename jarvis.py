from importlib.metadata import version

import speech_recognition as sr
import pyttsx3
from pydantic.v1 import NoneStr
from urllib3.exceptions import RequestError
import os


import ctypes
import os
import random
import webbrowser
import googlesearch
from playsound import playsound

import openai
import requests
from PIL import Image
from io import BytesIO


import wikipedia

import json

from jspotify_api import JSpotifyAPI

import random


from threading import Thread

import ray

class Jarvis:
    def __init__(self):
        self.voice_note = None
        self.voice_text = None
        self.rate = None
        self.voices = None
        self.engine = None
        self.speech = sr.Recognizer()

        self.running = True
        self.Version = 0.02

        self.language_choice = 3 #By default, English.


        self.set_jarvis_engine()
        self.set_jarvis_language()

        self.greeting_dict = {'hello': 'hello', 'hi': 'hi'}
        self.open_launch_dict = {'open': 'open', 'launch': 'launch'}
        self.google_searches_dict = {'what': 'what', 'why': 'why', 'who': 'who', 'which': 'which'}
        self.social_media_dict = {'facebook': 'https://www.facebook.com', 'twitter': 'https://www.twitter.com'}
        self.social_post = {'post': 'post'}



        self.my_api_key = ''
        openai.api_key = self.my_api_key
        self.client = openai.OpenAI(api_key=self.my_api_key)

        self.gpt_messages = []

        self.wikipedia_arr = []


        #Custom APIs
        self.j_Spotify = JSpotifyAPI()

        self.my_number_dict = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8,
                               'nine': 9, 'ten': 10}

    def print_version(self):
        print(self.Version)

    def set_jarvis_engine(self):
        try:
            self.engine = pyttsx3.init()
        except ImportError:
            print("Requested driver is not found!")
        except RuntimeError:
            print("Driver failed to initialize!")

    @ray.remote
    def speak_to_cmd_ray(self,cmd):
        self.engine.say(cmd)
        self.engine.runAndWait()

    @ray.remote
    def read_voice_cmd_ray(self):
        self.voice_text = ''
        with sr.Microphone() as source:
            print("Please speak something...")
            while True:  # Loop indefinitely
                try:
                    self.speech.adjust_for_ambient_noise(source)
                    audio = self.speech.listen(source, phrase_time_limit=25)  # Set a phrase time limit
                    self.voice_text = self.speech.recognize_google(audio)
                    return self.voice_text  # Return the recognized text if successful
                except sr.UnknownValueError:
                    print("I couldn't understand you, please try again.")
                except sr.RequestError:
                    print("There was a network error.")
                except Exception as e:
                    print(f"An error occurred: {str(e)}")
        return self.voice_text

    def speak_to_cmd(self,cmd):
        self.engine.say(cmd)
        self.engine.runAndWait()

    def read_voice_cmd(self):
        self.voice_text = ''
        with sr.Microphone() as source:
            print("Please speak something...")
            while True:  # Loop indefinitely
                try:
                    self.speech.adjust_for_ambient_noise(source)
                    audio = self.speech.listen(source, phrase_time_limit=25)  # Set a phrase time limit
                    self.voice_text = self.speech.recognize_google(audio)
                    return self.voice_text  # Return the recognized text if successful
                except sr.UnknownValueError:
                    print("I couldn't understand you, please try again.")
                except sr.RequestError:
                    print("There was a network error.")
                except Exception as e:
                    print(f"An error occurred: {str(e)}")
        return self.voice_text

    def set_jarvis_language(self):
        self.voices = self.engine.getProperty('voices')

        #for voice in self.voices:
         #   print(voice.id)
        if self.language_choice == 1:
            self.engine.setProperty('voice', 'English (America)')

        elif self.language_choice == 2:
            self.engine.setProperty('voice', 'Turkish')

        elif self.language_choice == 3:
            self.engine.setProperty('voice', 'Spanish (Spain)')


        self.rate = 150
        self.engine.setProperty('rate', self.rate)



    def is_valid_note(self, greet_dict, voice_note):
        for key, value in greet_dict.items():
            # 'Hello Friday'
            try:
                if value == voice_note.split(' ')[0]:
                    return True

                elif key == voice_note.split(' ')[1]:
                    return True

            except IndexError:
                pass

        return




    def google_search_result(self,query):
        search_result = googlesearch.search(query)

        for result in search_result:
            print(result.replace('...', '').rsplit('.', 3)[0])
            if result != '':
                play_sound_from_polly(result.replace('...', '').rsplit('.', 3)[0], is_google=True)
                break


    def read_from_json_gpt(self):

        try:
            with open('jarvis_gpt.json', 'r') as file:
                self.gpt_messages = json.load(file)
        except FileNotFoundError:
            print('CHATGPT File not found')


    def read_from_json_wikipedia(self):

        try:
            with open('wikipedia.json', 'r') as file:
                self.wikipedia_arr = json.load(file)
        except FileNotFoundError:
            print('Wikipedia File not found')



    def write_to_json(self, filename):
        with open(f'{filename}.json', 'w') as file:
            json.dump(self.gpt_messages, file)


    def write_to_json2(self, filename, text):
        with open(f'{filename}.json', 'w') as file:
            json.dump(text, file)


    def convert_letter_to_numbers(self, voice_note):


        voice_note = voice_note.strip().lower()
        if voice_note in self.my_number_dict:
            return int(self.my_number_dict[voice_note])

    def generate_image(self, prompt):
        response = openai.images.generate(  # Use openai.Image directly
            prompt=prompt,
            n=1,
            size="512x512"  # You can adjust the size
        )
        image_url =response.data[0].url
        return image_url

    # Function to download and save the image
    def download_image(self,url, filename):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img.save(filename)
        print(f"Image saved as {filename}")

    def run(self):



        while self.running:


            self.read_from_json_gpt()
            self.read_from_json_wikipedia()





            print("Jarvis : Listening...")
            self.voice_note = self.read_voice_cmd().lower()





            print("Cmd : {}".format(self.voice_note))



            if 'generate' in self.voice_note:
                self.voice_note = self.voice_note.replace('generate', '')
                image_url = self.generate_image(self.voice_note)
                randomfile_prefix = random.randint(0,1000)
                randomfile_suffix = random.randint(0, 1000)
                self.download_image(image_url, f"./Images/{randomfile_prefix}_{randomfile_suffix}.png")
                print(image_url)
                img = Image.open(f"./Images/{randomfile_prefix}_{randomfile_suffix}.png")
                img.show()

                continue

            #Wikipedia
            if 'wikipedia' in self.voice_note:
                self.wikipedia_bool = True

                while self.wikipedia_bool:
                    try:
                        self.speak_to_cmd('Searching Wikipedia...')
                        query = self.voice_note.replace("in wikipedia", "")
                        print("Jarvis : " + "Searcing wikipedia for " + " * " + query + " * ")
                        results = wikipedia.summary(query, sentences=2)
                        self.speak_to_cmd("According to Wikipedia")
                        print("Jarvis : " + results)
                        self.speak_to_cmd(results)
                    except:
                        print('Could not find anything, sir.')

                    self.speak_to_cmd("Do you want me to take note, Sir?")
                    self.voice_note = self.read_voice_cmd().lower()

                    if 'yes' in self.voice_note:
                        self.speak_to_cmd("Taking a wikipedia note sir!")
                        self.write_to_json2('wikipedia', results)
                        self.wikipedia_bool = False
                    if 'no' in self.voice_note:
                        self.speak_to_cmd("Ok Sir!")
                        self.wikipedia_bool = False

                continue

            if 'play' in self.voice_note:
                self.voice_note.replace('play', '')
                self.j_Spotify.spotify_play_music(f"{self.voice_note}")
                continue

            if 'open spotify' in self.voice_note:
                spotify_bool = True

                while spotify_bool:
                    print("Jarvis : " + "Opening spotify...")
                    self.speak_to_cmd('Sir Is there a song that you wish for or an artist?')
                    self.voice_note = self.read_voice_cmd()
                    print("Cmd : {}".format(self.voice_note))

                    if 'song' in self.voice_note:
                        self.speak_to_cmd("Which song do you wanna listen Sir?")
                        self.voice_note = self.read_voice_cmd()
                        print("Cmd : {}".format(self.voice_note))
                        try:
                            self.speak_to_cmd(f"Opening {self.voice_note} on spotify!")
                            self.j_Spotify.spotify_play_music(f"{self.voice_note}")
                            spotify_bool = False
                        except:
                            print('Could not find a song named as you said, sir.')
                            spotify_bool = False
                        spotify_bool = False
                    if 'artist' in self.voice_note:
                        len_artist = False
                        correct_num = False
                        self.speak_to_cmd("Which artist do you wanna listen Sir?")

                        while not len_artist:
                            self.voice_note = self.read_voice_cmd()
                            print("Cmd : {}".format(self.voice_note))
                            if len(self.voice_note) > 2:
                                len_artist = True


                        self.speak_to_cmd(f"Searching the songs of {self.voice_note} on spotify!")

                        tracks = self.j_Spotify.get_artist_songs(f"{self.voice_note}")
                        self.speak_to_cmd("Sir Please choose a song from the artist...")
                        selected_number = 1
                        x = 1
                        for track in tracks:

                            self.speak_to_cmd(f"{x}" + track)
                            x += 1
                        self.speak_to_cmd("Choose the number of the song you want to listen, sir!")

                        while not correct_num:
                            self.voice_note = self.read_voice_cmd()
                            print("Cmd : {}".format(self.voice_note))
                            if str(self.voice_note) in self.my_number_dict:
                                correct_num = True

                        selected_number = int(self.convert_letter_to_numbers(self.voice_note))
                        self.speak_to_cmd(f"Opening {self.voice_note} on spotify!")
                        self.j_Spotify.spotify_play_music(str(tracks[selected_number-1]))

                        spotify_bool = False



                continue


            if self.is_valid_note(self.greeting_dict, self.voice_note):
                print('In greeting...')
                self.speak_to_cmd('Hello Sir I am your artificial Intelligence')
                continue

            if self.is_valid_note(self.open_launch_dict, self.voice_note):
                print('In open...')
                self.speak_to_cmd("Opening {}".format(self.voice_note.split(' ')[1]))

                if self.is_valid_note(self.social_media_dict, self.voice_note):

                    webbrowser.open(self.social_media_dict[self.voice_note.split(' ')[1]])
                else:
                    os.system('explorer C:\\"{}"'.format(self.voice_note.replace('open ', '').replace('launch ', '')))



            if 'pause song' in self.voice_note:
                self.j_Spotify.spotify_pause_music()

            if 'bye' in self.voice_note:
                self.speak_to_cmd('See you later Sir!')
                exit()

            if 'test' in self.voice_note:
                self.voice_note = ''
                if self.read_voice_cmd() == None:
                    self.speak_to_cmd('We are in testing mode , let us try this heheh motherrr miaaa') & self.read_voice_cmd()

            else:
                if (len(self.voice_note) > 20) and (('jarvis') in self.voice_note):
                    try:
                        print(len(self.voice_note))
                        self.gpt_messages.append({"role": "user", "content": self.voice_note})



                        chat_completion = self.client.chat.completions.create(
                            messages=self.gpt_messages,
                            model="gpt-3.5-turbo",
                        )

                        response = chat_completion.choices[0].message.content.strip()
                        print("Jarvis : " + response)
                        self.gpt_messages.append({"role": "assistant", "content": response})
                        self.write_to_json('jarvis_gpt')

                        self.speak_to_cmd(response)
                        
                        



                        
                    except:
                        continue



