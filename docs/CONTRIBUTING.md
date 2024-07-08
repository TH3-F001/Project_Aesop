# Hey there, neighbor!

Welcome to the Project_Aesop contribution guide! I'm real thrilled you're here to help make our project even better. Whether you're here to fix a bug or add some fancy new features, this guide will help you get started on the right foot and ensure we're all fishing with the same bait.

## 🗂 Directory Structure

Aesop adheres to a strict MVC (Model-View-Controller) architecture to keep things project tidy and navigable. Here's how we keep our files and folders:

- **Model (`/src/models`)**: Where all the magic happens with data handling and logic.
- **View (`/src/views`)**: All about user interfaces and presentation.
- **Controller (`/src/controllers`)**: The brains of the operation, directing traffic between views and models.

For a detailed dive into the MVC pattern, take a gander at [this helpful resource](https://www.freecodecamp.org/news/the-model-view-controller-pattern-mvc-architecture-and-frameworks-explained/).

## 🌾 Git Branching Strategy

Here’s how we manage our branches in the git world:
- **Main Branch**: The holy grail, always production-ready... well once we get there
- **Development Branch**: Named `development`, this is where all the action happens. Make sure it’s always in a good state.
- **Feature Branches**: Going off `development`, create your feature branch (e.g., `feature/add-new-widget`). Once you’re done, merge it back into `development`.
- **Release Branches**: When we’re ready to release, we branch off from `development` to `release`. This is where we do final tests and tweaks.
- **Hotfix Branches**: These come from `main` if we need to fix something after it’s gone live.

## 🔄 Pushing and Pull Requests

- **Commit Messages**: Keep 'em clear and descriptive.
- **Pushing**: Regularly push your changes to your feature branch and open a _pull request into `development`.
- **Pull Requests**: Provide a summary of changes and tag someone (probably me) for review. Keep your PRs small to simplify reviews and integration._

## 🔑 API Keys and Credentials

At the moment, if you’re looking to contribute to parts of the project that interact with external services, you’ll need to rustle up your own API accounts and credentials. Here’s the list of APIs we’re currently dancing with:
- **Reddit**
- **YouTube/Google**
- **ElevenLabs**
- **OpenAI**

Don't worry about setting up all of these keys unless you need 'em. Just pick the ones relevant to the bits you’re planning to work on. Heck, depending on what you’re doing, you might not need any keys at all!


## ⚙️ Project Setup
Once the setup script has been run relevent project variables and directories are stored in /srv/aesop/data/static/service_config.json for later reference
```
    git clone https://github.com/TH3-F001/Project_Aesop.git
    cd Project_Aesop/install
    chmod +x *.sh
    ./setup.sh
```




### setup.sh performs the following actions:
#### 1) install_dependencies.sh
Installs dependencies using dependencies.csv to get package manager commands and packages to install
#### 2) build_fs.sh
- Builds the tool's basic directory structure
- Copies template user level config files to the directories specified in service_config.json
- Creates a service user/group with access to those files/folders as defined in service_config.json.
#### 3) build_venv.sh
- Builds a python venv in the location defined by service_config.json
- Loads the variables from service_config.json and user_config.json into venv environment variables.

## Environment Variables
The setup process initializes several environment variables into the virtual environment. these variables are inherited from user_config.json and service_config.json
The names of these environment variables are as follows:
### User Directories:
These are meant for display purposes, and are just paths to logical links which point to corresponding service directories
  - USR_OUTPUT_DIR
  - USR_LOG_DIR
  - USR_DATA_DIR
### Service Directories:
These are where the magic actually happens and where the project should read and write data to/from
  - SRV_SECRETS_DIR
  - SRV_OUTPUT_DIR
  - SRV_LOG_DIR
  - SRV_DATA_DIR
  - SRV_TEMP_DIR
  - SRV_VENV_DIR
  - SRV_USRGRP



---

Thanks for contributing, and don't be a stranger—drop by with questions, updates, or even just to chat about the latest Packers game. Let’s keep it rolling smoothly, just like a cheese wheel down a hill. Happy coding!
