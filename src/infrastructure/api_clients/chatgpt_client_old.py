from common.content_helper import Helper
from common.exceptions import RateLimitExceededException
from openai import OpenAI, Model, OpenAIError
from time import sleep
from typing import List
import os
import json

from pydub import AudioSegment
from pydub.silence import split_on_silence


class ChatGPT:

    def __init__(self, cred_path:str):
        # Load Config

        with open(cred_path, "r") as file:
            creds = Helper.load_json(cred_path)

        # Assign API key from gpt_auth.json as an environment variable
        self.api_key = creds["api_key"]
        os.environ["OPENAI_API_KEY"] = self.api_key

        # Set the model to be used for text prompts
        self.text_model = "gpt-4-turbo-preview"

        # Create the OpenAI client
        self.client = OpenAI()
        # self.generate_image("A silent cosmic event, such as a planet collision or supernova, illustrating the eerie silence of space.", "data/output/test.png")

#region Testing Assistants API
        # response = self.generate_video_prompt("Whether it’s in our own backyard or millions of light-years away, the universe can get pretty weird.\\nThe Hubble Deep Field image showing multiple galaxies\\nThe Hubble Space Telescope has imaged the universe in greater depth than any telescope before it. Credit: NASA, ESA, G. Illingworth (UCO/Lick Observatory and the University of California, Santa Cruz), R. Bouwens (UCO/Lick Observatory and Leiden University) and the HUDF09 Team\\n\\nEAU DE SPACE\\nSpace smells like brimstone, at least according to former astronaut Chris Hadfield. His theory is that the vacuum causes trace chemicals to ‘leak’ out of the walls of a spacecraft, giving the impression that space has a smell, even though it likely doesn’t. We do know that Moon dust has a scent however, and it’s not very cheesy. According to astronauts, who were covered in lunar dust every time they came back from an excursion, it smells more like gunpowder.\\n\\nEarth\\nEarth is usually identified from space as being a pale blue dot, but considering that the number of trees on our planet outnumber the amount of stars in the Milky Way, perhaps we should become the pale blue-green dot. Credit: NASA Earth Observatory/Joshua Stevens; NOAA National\\n\\nTREES OUTNUMBER THE STARS\\nThough Earth is best known for being a water rich planet, we may need to rebrand to a green filled planet. It may surprise you, but there are more trees on Earth than there are stars in the Milky Way. According to a study published in Nature there are about 3 trillion trees on our planet. This far out paces the ‘measly’ 100-400 billion stars estimated to exist in the Milky Way.\\n\\nEERIE SILENCE\\nRidley Scott’s Alien franchise’s tagline ‘In space no one can hear you scream,’ is true.\\n\\nSound is basically just vibrating air — something the cosmos is lacking. The universe’s most extreme events, from colliding planets to supernovae, would occur silently for an observer. Space agencies like NASA have brought sound to some of space however. Instead of turning a microphone to the cosmos, researchers use a technique called data sonification that converts radio waves, plasma waves, and magnetic field into audio tracks so we can ‘hear’ space.\\n\\nThe cosmic microwave background showing different colors representing small temperature fluctuations.\\nThe cosmic microwave background (CMB) is a snapshot of the early universe; it is the oldest light we can see. This light has been Doppler shifted into the microwave portion of the spectrum, outside the realm of naked-eye observing. In this image, generated with data from the Planck satellite, different colors represent tiny temperature fluctuations in the universe. Credit: ESA and the Planck Collaboration\\n\\nWHY IS SPACE DARK?\\nIt’s estimated that there are at least 1 septilion stars in the universe — that’s the number 1 followed by 24 zeros. So with so many stars, why is it that the night sky appears, for the most part, black? This question is so common — and important — that it has a name: Olbers’ paradox. The key to this ‘problem’ is that the stars in the universe have only had 13.7 billion years to be born, evolve, and die, so the universe is not actually filled with stars at every location for us to see. Additionally, light has a finite speed, so we can only see light that has had enough time since the beginning of the universe to travel from its origin to Earth. Furthermore, as the universe expands, light traveling toward us from distant sources undergoes a process called Doppler shifting, which stretches the light to longer wavelengths. Given a large enough shift, the light is no longer visible to the human eye. In fact, the oldest radiation we can see in the universe, the cosmic microwave background, has been stretched so much that, though it is everywhere, it is invisible to the naked eye.")
        # print(response)
#endregion



#region Assistants API
    def assistant_exists(self, name) -> bool:
        print(f"\nChecking if {name} exists...")
        result = False
        existing_assistants = self.client.beta.assistants.list()
        for assistant in existing_assistants.data:
            if assistant.name == name:
                print(f"\t{name} already exists. Using...")
                result = True
        return result

    def create_new_assistant(self, name, root_instructions):
        print(f"\nCreating New Assistant: {name}...")

        assistant = self.client.beta.assistants.create(
            name=name,
            instructions=root_instructions,
            tools=[{"type": "code_interpreter"}],
            model=self.text_model,
            temperature=0.5
        )
        print(f"\t{name} Created.")
        return assistant

    def get_assistant(self, name: str):
        print(f"\nRetrieving Assistant: {name}")
        result = None
        existing_assistants = self.client.beta.assistants.list()
        for assistant in existing_assistants.data:
            if assistant.name == name:
                result = assistant
        print(f"\tAssistant: {name} retrieved.")
        return result

    def new_assistant_thread(self):
        print("\nCreating New Thread...")
        thread = self.client.beta.threads.create()
        print(f"\tThread: {thread} Created.")
        return thread

    def get_thread_by_id(self, thread_id):
        try:
            thread = self.client.beta.threads.retrieve(thread_id=thread_id)
            return thread
        except Exception as e:
            print(f"An error occurred while retrieving the thread: {e}")
            return None


    def run_assistant_thread(self, thread, assistant_name, additional_instructions):
        print(f"\nRunning Thread: {thread.id}...")

        # Get the assistant details directly, letting errors raise if it fails
        assistant = self.get_assistant(assistant_name)

        # Start the thread run and let any errors during creation or polling propagate
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
            additional_instructions=additional_instructions
        )

        # Poll until the run is completed, let it crash on failure
        while run.status != "completed":
            print(f"\tRun status: {run.status}")
            if run.status == "failed":
                errcode = run.last_error.code
                errmsg = run.last_error.message
                if errcode == "rate_limit_exceeded":
                    raise RateLimitExceededException("Request too Large")

                raise RuntimeError(f"ERROR: Run failed with error code {errcode}\n{errmsg}.")
            sleep(1)

        # Fetch the list of messages in the thread
        messages = self.client.beta.threads.messages.list(thread_id=thread.id)

        # Retrieve the last assistant response
        for message in reversed(messages.data):
            if message.role == "assistant":
                for content_block in message.content:
                    if content_block.type == 'text':
                        result = content_block.text.value
                        print(content_block.text.value)
                        return result

        raise RuntimeError("No assistant response found in the thread.")


    def generate_user_message(self, user_prompt, thread):
        print("\tGenerating User Message...")
        message = self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_prompt
        )

        print("\t\tUser Message Generated.")
        return message

#endregion


#region DALL-E API
    def generate_image(self, prompt: str, output_path: str, resolution="1024x1792", num_images=1):
        print("\nGenerating DALL-E Image...")
        if num_images > 10:
            num_images = 10

        print("\tSending Image Generation Request...")
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=resolution,
            quality="standard",
            n=num_images
        )

        image_url = response.data[0].url

        print(f"\tDownloading Image...")
        Helper.download_image(image_url, output_path)


    # def generate_images(self, prompts: List[str], resolution="1024x1792"):
    #     for prompt in prompts:
    #         self.generate_image()

#endregion


#region Text-to-Voice and Voice-to-Text
    def get_voice_from_text(self, msg: str, output_path: str, high_quality=False, voice="alloy", silent_time=500):
        print("\nConverting Message Into Audio...")
        model = "tts-1"
        if high_quality:
            model += "-hd"

        valid_voices = {"alloy", "echo", "fable", "onyx", "nova", "shimmer"}
        if voice not in valid_voices:
            raise ValueError(f"ERROR! Voice Model: {voice} is invalid.")

        response = self.client.audio.speech.create(
            model=model,
            voice=voice,
            input=msg
        )

        parent_dir = Helper.get_parent_directory(output_path)
        Helper.create_directory_structure(parent_dir)

        temp_output_path = output_path + "_temp"
        response.stream_to_file(temp_output_path)
        print(f"\tTemporary Audio File Downloaded to {temp_output_path}.")

        # Load the temporary audio file
        audio = AudioSegment.from_file(temp_output_path)

        # Create silence segment of 0.25 seconds
        silence = AudioSegment.silent(duration=silent_time)  # Duration is in milliseconds

        # Add silence to the end of the audio
        final_audio = audio + silence

        # Export the final audio to the original output path
        final_audio.export(output_path, format="mp3")
        print(f"\tAudio File with Silence Added Downloaded to {output_path}.")

        # Optionally delete the temporary file
        import os
        os.remove(temp_output_path)

    def get_text_from_voice(self):
        pass
#endregion


#region Completions API
    def send_chat_request(self, system_msg: str, user_msg: str) -> str:
        print("\nRetrieving Chat Response...")
        completion = self.client.chat.completions.create(
            model=self.text_model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg}
            ]
        )
        print("\tChat Response Retrieved.")
        return completion.choices[0].message
#endregion




#region Registering/Saving New Data
    def register_new_channel(self, channel_name: str):
        pass

    def register_new_video(self, video_title: str):
        pass
#endregion
