import os
from huggingface_hub import hf_hub_download

def download_weights():
    repo_id = "Tundragoon/Kokoro-German"
    print(f"Downloading weights for {repo_id}...")
    
    # Download the main model
    hf_hub_download(repo_id=repo_id, filename="kokoro-german-v1_1-de.pth")
    
    # Download the configuration
    hf_hub_download(repo_id=repo_id, filename="config.json")
    
    # Download the preferred default voice
    hf_hub_download(repo_id=repo_id, filename="voices/df_eva.pt")
    
    print("Download completed successfully!")

if __name__ == "__main__":
    download_weights()
