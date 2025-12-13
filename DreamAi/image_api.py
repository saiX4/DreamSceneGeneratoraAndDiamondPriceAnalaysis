import requests
import base64

MODEL_ID = "@cf/black-forest-labs/flux-1-schnell"
ACCOUNT_ID = "c96c0833fcae9d3ec03167389ce13422"
API_TOKEN = "Fe32o7UlYzV9lC7GpHp_SiDlBglu_2fH3mPv3iEf" 

def api(prompt='create an image of cat'):
    inputs = {
    "prompt":prompt,
    "num_steps": 8,
    }
    response = requests.post(
        f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/{MODEL_ID}",
        headers={"Authorization": f"Bearer {API_TOKEN}"},
        json=inputs
    )

    if response.status_code == 200:
        result = response.json()
        if "result" in result and "image" in result["result"]:
        # Decode and Save
            img_data = base64.b64decode(result["result"]["image"])
            with open("./images/flux_output.png", "wb") as f:
                f.write(img_data)
            print("Success! Saved as 'flux_output.png'")
        else:
         print("Error parsing result:", result)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        