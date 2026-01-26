# Hands-on With Reasoning Models

## Summary 
This repository contains a number of examples that illustrate the functionality of reasoning models and the new class of more complex problems they can solve.  

Rewatch the episode talking through the scenarios here:

[![Banner](../../../data/assets/livestream/S1E2-spotlight.png)](https://youtu.be/nTqr4pzxF-k?list=PLmsFUfdnGr3wzz6a4E-Szksg92JPng-AL)

The original code is available at https://github.com/jennifermarsman/o1Analysis.  

## Setup
This project requires access to an Azure OpenAI resource to run a reasoning model.  At the [model catalog](https://ai.azure.com/explore/models), you will need to deploy the **o1** or **o3-mini** model, for example.  (The code was originally written for the **o1-preview** model.)  Then update the .env file with the endpoint (and the deployment name if you change from the default).  You will also need to supply either an API key or use Microsoft Entra ID (formerly called Azure Active Directory) authentication.  We strongly recommend Microsoft Entra ID authentication for greater security.  To set it up, see https://learn.microsoft.com/azure/ai-services/openai/how-to/managed-identity.  Don't forget that you may need to run "az login" to refresh your credentials.  

Finally, use the following commands in a python environment (such as an Anaconda prompt window) to set up your environment.  This creates and activates an environment and installs the required packages.  For subsequent runs after the initial install, you will only need to activate the environment and then run the python script.  

### First run
```
conda create --name reasoning -y
conda activate reasoning

pip install -r requirements.txt
jupyter notebook o1Analysis.ipynb
```

### Subsequent runs
```
conda activate reasoning
jupyter notebook o1Analysis.ipynb
```