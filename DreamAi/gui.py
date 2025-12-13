import customtkinter
from PIL import Image
import threading
import image_api 
import shutil    
import os  
from tkinter import filedialog 

app = customtkinter.CTk()

app.geometry("720x420")
app.resizable(False, False)
app.configure(fg_color="#000000")
app.title("DreamAi")

def run_api_in_background(prompt):
    """This function runs inside the thread (The Chef)"""
    try:
        print(f"Calling API with: {prompt}")
        image_api.api(prompt) # This blocks here, but it's okay because it's a thread
        print("API Call Complete.")
    except Exception as e:
        print(f"Error in API: {e}")

def monitor_thread(thread):
    if thread.is_alive():
        current_text = make_btn.cget("text")
        if current_text == "GENERATING...":
            make_btn.configure(text="GENERATING   ")
        else:
            make_btn.configure(text="GENERATING...")
        
        # 2. Check again in 100ms
        app.after(100, lambda: monitor_thread(thread))
    else:
        # --- THREAD IS DONE ---
        print("Updating UI...")        
        # 3. Reload the image from disk
        try:
            new_pil_image = Image.open("./images/flux_output.png")
            
            new_ctk_image = customtkinter.CTkImage(
                light_image=new_pil_image,
                dark_image=new_pil_image,
                size=(360,420)
            )
            
            # 4. Update the EXISTING label (Don't create a new one)
            result_image_label.configure(image=new_ctk_image)
            result_image_label.image = new_ctk_image # Keep reference
            
        except Exception as e:
            print(f"Error loading image: {e}")

        # 5. Reset Button
        make_btn.configure(text="GENERATE", state="normal")

def on_generate_click():
    """This triggers the process"""
    prompt_text = input_box.get("1.0", "end-1c")
    
    # 1. Disable button so user can't spam click
    make_btn.configure(text="GENERATING...", state="disabled")
    
    # 2. Start the Thread
    t = threading.Thread(target=run_api_in_background, args=(prompt_text,))
    t.start()
    
    # 3. Start the Monitor
    monitor_thread(t)

# --- NEW: DOWNLOAD FUNCTION ---
def on_download_click():
    """Opens a file dialog to save the generated image"""
    source_path = "./images/flux_output.png"
    
    # Check if the generated image actually exists
    if not os.path.exists(source_path):
        print("No image found to download!")
        return

    # Open Save As Dialog
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
        title="Save Generated Image"
    )

    # If user selected a path (didn't click cancel)
    if file_path:
        try:
            shutil.copy(source_path, file_path)
            print(f"Image saved successfully to: {file_path}")
        except Exception as e:
            print(f"Error saving file: {e}")

# --- 2. GUI SETUP ---

landing_frame = customtkinter.CTkFrame(app, fg_color="#050505")
landing_frame.pack(fill="both", expand=True)

headline_font = customtkinter.CTkFont(family="Orbitron", size=30, weight="bold")
subhead_font = customtkinter.CTkFont(family="Orbitron", size=10, weight="normal")

text_1 = customtkinter.CTkLabel(
    app, 
    text="Reality is boring \ngenerate a\nbetter one", 
    font=headline_font, 
    text_color="white",
    justify="left"
)
text_1.place(x=40, y=127)

text_2 = customtkinter.CTkLabel(
    app, 
    text="DreamAi", 
    font=subhead_font, 
    text_color="#CB37A0",
    justify="left"
)
text_2.place(x=40, y=90)

def generate_event():
    landing_frame.pack_forget()
    second_frame.pack(fill="both", expand=True)

button_font = customtkinter.CTkFont(family="Montserrat", size=15, weight="bold")

generate_btn = customtkinter.CTkButton(
    app,
    text="GENERATE  ➔",
    text_color='black',
    command=generate_event,
    width=200,                
    height=50,                
    font=button_font,
    fg_color="#CB37A0",    
    hover_color="#D01A9C" ,
    corner_radius=0           
)
generate_btn.place(x=40, y=270)

# Load landing image
try:
    my_image = customtkinter.CTkImage(light_image=Image.open("./images/e149e7673de6386c49b15b729713c0d7.jpg"),
                                      dark_image=Image.open("./images/e149e7673de6386c49b15b729713c0d7.jpg"),
                                      size=(360,420))
    image_label = customtkinter.CTkLabel(landing_frame, image=my_image) 
    image_label.pack(side='right')
except:
    print("Landing image not found")


second_frame = customtkinter.CTkFrame(app, fg_color="#101010")

input_box = customtkinter.CTkTextbox(second_frame, width=360, height=400, fg_color="#202020", text_color="white")
input_box.pack(side='left')

make_btn = customtkinter.CTkButton(
    second_frame, 
    text="GENERATE", 
    command=on_generate_click, 
    fg_color="#F5F2F4",    
    hover_color="#FFFFFF",
    width=360,
    height=50, 
    corner_radius=0,
    font=button_font,
    text_color='#CB37A0'
)
make_btn.place(x=0,y=375)

# Load initial result image (or placeholder)
try:
    my_image_1 = customtkinter.CTkImage(light_image=Image.open("./images/flux_output.png"),
                                        dark_image=Image.open("./images/flux_output.png"),
                                        size=(360,420))
except:
    # Handle case where image doesn't exist yet
    my_image_1 = None 

# Create the label once, we will update it later
result_image_label = customtkinter.CTkLabel(second_frame, image=my_image_1, text='') 
result_image_label.pack(side='right')

# UPDATED DOWNLOAD BUTTON
download_btn = customtkinter.CTkButton(
    second_frame, 
    text="DOWNLOAD", 
    command=on_download_click, # <--- CONNECTED THE FUNCTION HERE
    fg_color="#CB37A0",    
    hover_color="#D01A9C",
    width=360,
    height=50, 
    corner_radius=0,
    font=button_font,
    text_color='white'
)
download_btn.place(x=360,y=375)

app.mainloop()