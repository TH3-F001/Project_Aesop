from openai import OpenAI, Model, OpenAIError
import os
import yaml
from time import sleep


class ChatGPT:

    def __init__(self):
        # Load Config
        config_path = "appdata/restricted/gpt.yaml"
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)

        # Assign API key from gpt.yaml as an environment variable
        self.api_key = config["creds"]["api_key"]
        os.environ["OPENAI_API_KEY"] = self.api_key

        # We dump all output files here in a folder marked with the channel name/video title
        self.output_dir = config["output_folder"]

        # Set the model to be used for text prompts
        self.text_model = "gpt-4-turbo-preview"

        # Load Prompts into memory:


        # Create the OpenAI client
        self.client = OpenAI()
        self.generate_image("A silent cosmic event, such as a planet collision or supernova, illustrating the eerie silence of space.")

#region Testing Assistants API
        # response = self.generate_video_prompt("Whether it’s in our own backyard or millions of light-years away, the universe can get pretty weird.\\nThe Hubble Deep Field image showing multiple galaxies\\nThe Hubble Space Telescope has imaged the universe in greater depth than any telescope before it. Credit: NASA, ESA, G. Illingworth (UCO/Lick Observatory and the University of California, Santa Cruz), R. Bouwens (UCO/Lick Observatory and Leiden University) and the HUDF09 Team\\n\\nEAU DE SPACE\\nSpace smells like brimstone, at least according to former astronaut Chris Hadfield. His theory is that the vacuum causes trace chemicals to ‘leak’ out of the walls of a spacecraft, giving the impression that space has a smell, even though it likely doesn’t. We do know that Moon dust has a scent however, and it’s not very cheesy. According to astronauts, who were covered in lunar dust every time they came back from an excursion, it smells more like gunpowder.\\n\\nEarth\\nEarth is usually identified from space as being a pale blue dot, but considering that the number of trees on our planet outnumber the amount of stars in the Milky Way, perhaps we should become the pale blue-green dot. Credit: NASA Earth Observatory/Joshua Stevens; NOAA National\\n\\nTREES OUTNUMBER THE STARS\\nThough Earth is best known for being a water rich planet, we may need to rebrand to a green filled planet. It may surprise you, but there are more trees on Earth than there are stars in the Milky Way. According to a study published in Nature there are about 3 trillion trees on our planet. This far out paces the ‘measly’ 100-400 billion stars estimated to exist in the Milky Way.\\n\\nEERIE SILENCE\\nRidley Scott’s Alien franchise’s tagline ‘In space no one can hear you scream,’ is true.\\n\\nSound is basically just vibrating air — something the cosmos is lacking. The universe’s most extreme events, from colliding planets to supernovae, would occur silently for an observer. Space agencies like NASA have brought sound to some of space however. Instead of turning a microphone to the cosmos, researchers use a technique called data sonification that converts radio waves, plasma waves, and magnetic field into audio tracks so we can ‘hear’ space.\\n\\nThe cosmic microwave background showing different colors representing small temperature fluctuations.\\nThe cosmic microwave background (CMB) is a snapshot of the early universe; it is the oldest light we can see. This light has been Doppler shifted into the microwave portion of the spectrum, outside the realm of naked-eye observing. In this image, generated with data from the Planck satellite, different colors represent tiny temperature fluctuations in the universe. Credit: ESA and the Planck Collaboration\\n\\nWHY IS SPACE DARK?\\nIt’s estimated that there are at least 1 septilion stars in the universe — that’s the number 1 followed by 24 zeros. So with so many stars, why is it that the night sky appears, for the most part, black? This question is so common — and important — that it has a name: Olbers’ paradox. The key to this ‘problem’ is that the stars in the universe have only had 13.7 billion years to be born, evolve, and die, so the universe is not actually filled with stars at every location for us to see. Additionally, light has a finite speed, so we can only see light that has had enough time since the beginning of the universe to travel from its origin to Earth. Furthermore, as the universe expands, light traveling toward us from distant sources undergoes a process called Doppler shifting, which stretches the light to longer wavelengths. Given a large enough shift, the light is no longer visible to the human eye. In fact, the oldest radiation we can see in the universe, the cosmic microwave background, has been stretched so much that, though it is everywhere, it is invisible to the naked eye.")
        # print(response)
#endregion

#region Testing Dall-E API

#endregion


#region Run Externally
    def generate_video_prompt(self, user_prompt: str):
        # Get the Vidgen Assistant or Create it if needed
        if self.assistant_exists("VidGen Assistant"):
            self.vidgen_prompt_assistant = self.get_assistant("VidGen Assistant")
        else:
            root_vidgen_instructions = self.get_root_vidgen_instructions()
            self.vidgen_prompt_assistant = self.create_new_assistant("VidGen Assistant", root_vidgen_instructions)

        thread = self.new_thread()

        # Create the first user message
        message = self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_prompt
        )

        # Grab Channel data for thread instructions
        with open("appdata/prompts/gpt/thread_prompts/space_secrets.yaml", "r") as file:
            thread_instructions = file.read()

        # Run a query
        self.run_thread(thread, thread_instructions)

#endregion


#region Assistants API
    def assistant_exists(self, name) -> bool:
        result = False
        existing_assistants = self.client.beta.assistants.list()
        for assistant in existing_assistants.data:
            if assistant.name == name:
                print(f"\t{name} already exists. Using...")
                result = True
        return result

    def create_new_assistant(self, name, root_instructions):
        print(f"\tCreating New Assistant: {name}...")

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
        result = None
        existing_assistants = self.client.beta.assistants.list()
        for assistant in existing_assistants.data:
            if assistant.name == name:
                result = assistant
        return result

    def new_thread(self):
        return self.client.beta.threads.create()

    def run_thread(self, thread, additional_instructions):
        result = None
        try:
            # Start the run
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=self.vidgen_prompt_assistant.id,
                additional_instructions=additional_instructions
            )

            # Poll until the run is completed
            while run.status != "completed":
                print(f"Run status: {run.status}")
                if run.status == "failed":
                    raise RuntimeError("Run failed.")
                sleep(1)  # Adding a sleep to avoid busy-waiting

            # Fetch the list of messages in the thread
            messages = self.client.beta.threads.messages.list(thread_id=thread.id)

            # Retrieve the last assistant response
            for message in reversed(messages.data):
                if message.role == "assistant":
                    for content_block in message.content:
                        if content_block.type == 'text':
                            result = content_block.text.value
                            print(content_block.text.value)
                    break

        except OpenAIError as e:
            print(f"OpenAI error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        return result

#endregion


#region DALL-E API
    def generate_image(self, prompt, resolution="1024x1792", num_images=1):
        if num_images > 10:
            num_images = 10

        response = self.client.images.generate(
            model="dall-e-2",
            prompt=prompt,
            # size=resolution,
            quality="standard",
            n=num_images
        )

        image_url = response.data[0].url
        print(image_url)

#endregion


#region Completions API
    def request_video_prompt(self):
        completion = self.client.chat.completions.create(
            model=self.text_model,
            messages=[
                {"role": "system",
                 "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
                {"role": "user", "content": f"{self.video_generator_prompt}"}
            ]
        )
        print(completion.choices[0].message)
#endregion


#region Getters and Setters
    def get_root_vidgen_instructions(self) -> str:
        vidgen_prompt_path = "appdata/prompts/gpt/vidgen_assistant_prompt.txt"
        with open(vidgen_prompt_path, "r") as file:
            video_generator_prompt = file.read()

        return video_generator_prompt
#endregion
