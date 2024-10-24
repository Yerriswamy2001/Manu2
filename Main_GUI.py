from tkinter import filedialog, Label
from PIL import Image, ImageTk
import numpy as np
# from tensorflow.keras.models import load_model
import cv2
import gridfs
from pymongo import MongoClient
import io
import warnings
warnings.filterwarnings("ignore")
import os
from pymongo import MongoClient
import tkinter as tk
from tkinter import ttk
from datetime import datetime,timedelta
import pymongo
from PIL import Image, ImageTk
from io import BytesIO
import threading
from pymongo import MongoClient
import warnings
warnings.filterwarnings("ignore")
import os
import time
from tkcalendar import Calendar
import cv2
from pymodbus.client.sync import ModbusTcpClient
import torch
from tkinter import messagebox
from gridfs import GridFSBucket
# from tensorflow import keras
# import tensorflow as tf
from src.COMMON.common import db_to_images_bulk_output,db_to_images_bulk_raw,load_env
# import tensorflow as tf
from src.MODEL.detectron import torchy_warmup
# print(tf.__version__)
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


ROOT_DIR = os.getcwd()
MEDIA_PATH = os.path.join(ROOT_DIR,'media')

env_vars = load_env(ROOT_DIR)
db_url = env_vars.get('DATABASE_URL')
db_name = env_vars.get('DATABASE_NAME')
plc_ip = env_vars.get('PLC_IP')
exp_time = env_vars.get('EXPOSURE_TIME')
weight_path1= env_vars.get('WEIGHT_FILE1')
# weight_path2 = env_vars.get('WEIGHT_FILE2')
serial_number = env_vars.get('CAMERA_ID')
deployment = env_vars.get('DEPLOYMENT')
machine_no = env_vars.get('MACHINE_NO')

if deployment == "True":
    from src.camfile.camconnection import *
    from src.main_cycle import main_process_save_plc
else:
    from src.main import main_process_save

# DB initalization
myclient = MongoClient(db_url)
mydb = myclient[db_name]

mycollec = mydb["MAIN"]
mycollec.create_index([("cur_date", pymongo.ASCENDING)])

#PLC
client = ModbusTcpClient(str(plc_ip))
modbus_client = client.connect()
print(modbus_client,'modbus_client')

if deployment == "True":
    #GPU
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model1 = torch.jit.load(os.path.join(MEDIA_PATH,f'WEIGHTS/{weight_path1}')).to(device)
    torch.backends.cudnn.benchmark = True
    torch.cuda.amp.autocast()
    torch.cuda.empty_cache()
else:
    #CPU
    device = torch.device("cpu")
    model1 = torch.jit.load(os.path.join(MEDIA_PATH,f'WEIGHTS/{weight_path1}'), map_location=device)

# if deployment == "True":
#     # Load the model to CPU
#     try:
#         model2 = keras.models.load_model(os.path.join(MEDIA_PATH, f'WEIGHTS/{weight_path2}'))
#     except Exception as e:
#         print(f"Error loading model: {e}")
# model2.compile(optimizer='adam', loss='mse',metrics=['accuracy'])


global flag
flag = False


class falg:
    def __init__(self):
        self.flag = False
        self.device = 0

asi = falg()

if deployment == "True":
    device = create_device_from_serial_number(serial_number)
    exposure_time = float(exp_time)  # change to desired value
    gain = 7  # change to desired value
    num_channels = setup(device, exposure_time, gain)
    if not modbus_client:
        print("PLC error ")
        sys.exit(0)
    device.start_stream()
    asi.device = device
else:
    pass

img = cv2.imread(os.path.join(MEDIA_PATH,'RAW IMAGES/1.jpg'))

torchy_warmup(img,model1)
torchy_warmup(img,model1)
torchy_warmup(img,model1)


#GUI SETUP
win = tk.Tk()
win.title("Manu Yantrayalay GUI")
win.configure(bg='#405D72')
win.iconbitmap(os.path.join(MEDIA_PATH,"GUI IMAGES/Manu_logo.ico"))


image1 = Image.open(
    "media/GUI IMAGES/RadomeTech Logo (570 × 161 px) No Background.png")
# Resize the image to a new width and height
new_width = 200
new_height = 50
resized_image1 = image1.resize((new_width, new_height))
test = ImageTk.PhotoImage(resized_image1)
label1 = tk.Label(image=test)
label1.image = test
label1.place(relx=0.84,rely=0)
label1.config(bg='#405D72')
image1 = Image.open(
    "media/GUI IMAGES/Manu_logo.png")
# Resize the image to a new width and height
new_width = 200
new_height = 50
resized_image1 = image1.resize((new_width, new_height))
test = ImageTk.PhotoImage(resized_image1)
label1 = tk.Label(image=test)
label1.image = test
label1.place(relx=0,rely=0)
label1.config(bg='#405D72')

image1 = Image.open(
    "media/GUI IMAGES/SmartQC_logo.png")
# Resize the image to a new width and height
new_width = 100
new_height = 52
resized_image1 = image1.resize((new_width, new_height))
test = ImageTk.PhotoImage(resized_image1)
label1 = tk.Label(image=test)
label1.image = test
label1.place(relx=0.923,rely=0.92)
label1.config(bg='#405D72')

copy_right = "© 2024 Radome Technologies and Services. All rights reserved"
tk.Label(win, text=copy_right, font=("Helvetica", 10),bg="#405D72", fg="black").place(relx=0,rely=0.96)

# Main Tkinter window setup
def get_previous_image(fs_files):
    latest_and_previous_documents = list(fs_files.find(sort=[("uploadDate", pymongo.DESCENDING)], limit=2))
    if not latest_and_previous_documents: 
        return None
    elif len(latest_and_previous_documents) == 1:
        return None
    else:
        return latest_and_previous_documents[1]['_id']

def get_current_image(fs_files):
    latest_and_previous_documents = list(fs_files.find(sort=[("uploadDate", pymongo.DESCENDING)], limit=2))
    if not latest_and_previous_documents:
        return None
    elif len(latest_and_previous_documents) == 1:
        return latest_and_previous_documents[0]['_id']
    elif len(latest_and_previous_documents) == 2:
        return latest_and_previous_documents[0]['_id']


def display_image_pre(image):
    new_width = 432
    new_height = 270
    resized_image = image.resize((new_width, new_height))
    photo_image = ImageTk.PhotoImage(resized_image)
    label5.config(image=photo_image)
    label5.image = photo_image

def display_image_cur(image):
    new_width = 432
    new_height = 270
    resized_image = image.resize((new_width, new_height))
    photo_image = ImageTk.PhotoImage(resized_image)
    label4.config(image=photo_image)
    label4.image = photo_image

def update_image(fs_files,fs_chunks):
    try:
        latest = get_current_image(fs_files)
        if latest != None:
            chunks = fs_chunks.find({"files_id": latest})
            binary_data = b"".join(chunk["data"] for chunk in chunks)
            with BytesIO(binary_data) as f:
                image = Image.open(f)
                display_image_cur(image)
        else:
            noimage = Image.open(os.path.join(MEDIA_PATH, 'GUI IMAGES/no_image.jpg'))
            display_image_cur(noimage)
    except Exception as e:
        print(f"An error occurred in update_image: {e}")

    label4.after(500, update_image,fs_files,fs_chunks)

tk.Label(win, text="CURRENT IMAGE", font=('Helvetica', 16, 'bold'), bg='#405D72', fg='black').place(relx=0.1, rely=0.1)
label4 = tk.Label(win, bg='#405D72')
label4.place(relx=0.02, rely=0.14)
# update_image()

def update_image1(fs_files,fs_chunks): 
    try:
        previous = get_previous_image(fs_files)
        if previous != None:
            chunks = fs_chunks.find({"files_id": previous})
            binary_data = b"".join(chunk["data"] for chunk in chunks)
            with BytesIO(binary_data) as f:
                image = Image.open(f)
                display_image_pre(image)
        else:
            noimage = Image.open(os.path.join(MEDIA_PATH, 'GUI IMAGES/no_image.jpg'))
            display_image_pre(noimage)
    except Exception as e:
        print(f"An error occurred update_imag: {e}")

    label5.after(500, update_image1,fs_files,fs_chunks)

tk.Label(win, text="PREVIOUS IMAGE", font=(
    'Helvetica', 16, 'bold'),bg='#405D72', fg='black').place(relx=0.1,rely=0.525)
label5 = tk.Label(win,bg='#405D72')
label5.place(relx=0.02,rely=0.57)

def capture_image_save():
    lbl_mode.config(text="Save Mode is ON",borderwidth=1, relief="solid",fg="#fa0a0a")
    lbl_mode.update()
    lbl_mode.place(relx=0.6,rely=0.15)
    # log_event("Save Mode was clicked")
    
    
    print("Save Mode")
    if deployment == "True":
        t1 = threading.Thread(target=main_process_save_plc, args=(asi,client,MEDIA_PATH,mydb,model1,))
        t1.start()
    else:
        t1 = threading.Thread(target=main_process_save, args=(asi,MEDIA_PATH,mydb,model1,))
        t1.start()
    fs_files = mydb['INPUT IMAGES.files']
    fs_chunks = mydb['INPUT IMAGES.chunks']
    update_image(fs_files,fs_chunks)
    update_image1(fs_files,fs_chunks)

def exit_app():
    result = messagebox.askquestion("Exit", "Do you wish to proceed with exiting the application ?")
    if result == "yes":
        asi.flag = True
        win.destroy()
if deployment == "True":
    def sol_open(client):
        write_mem(client,13, 1)
        time.sleep(0.3)
        write_mem(client,13, 0)

    def emergency(client):
        write_mem(client,89, 1)
        time.sleep(0.3)
        write_mem(client,89, 0)
else:
    def sol_open():
        pass

    def emergency():
        pass


def open_second_window():
    def submit():
        start_date = start_calendar.get_date()
        end_date = end_calendar.get_date()
        start_time = start_time_entry.get()
        end_time = end_time_entry.get()
        start_datetime = datetime.strptime(start_date + " " + start_time, "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.strptime(end_date + " " + end_time, "%Y-%m-%d %H:%M:%S")
        start_datetime_str = start_datetime.strftime("%d-%m-%Y %H:%M:%S")
        end_datetime_str = end_datetime.strftime("%d-%m-%Y %H:%M:%S")
        batch_foldername = end_datetime.strftime("%d-%m-%Y_%H-%M-%S")
        output_dowmload_path = os.path.join(MEDIA_PATH,'PREDICTED IMAGES',batch_foldername)
        input_dowmload_path = os.path.join(MEDIA_PATH,'RAW IMAGES',batch_foldername)
        if select_box.get() == "Both":
            if not os.path.exists(output_dowmload_path):
                os.makedirs(output_dowmload_path)
                os.makedirs(input_dowmload_path)
            db_to_images_bulk_output(mydb,output_dowmload_path,start_datetime_str,end_datetime_str)
            db_to_images_bulk_raw(mydb,input_dowmload_path,start_datetime_str,end_datetime_str)
        elif select_box.get() == "Output Images":
            if not os.path.exists(output_dowmload_path):
                os.makedirs(output_dowmload_path)
            db_to_images_bulk_output(mydb,output_dowmload_path,start_datetime_str,end_datetime_str)
        elif select_box.get() == "Input Images":
            if not os.path.exists(input_dowmload_path):
                os.makedirs(input_dowmload_path)
            db_to_images_bulk_raw(mydb,input_dowmload_path,start_datetime_str,end_datetime_str)

        second_window.destroy()

    second_window = tk.Toplevel(win)
    second_window.iconbitmap(os.path.join(MEDIA_PATH,"GUI IMAGES/Manu_logo.ico"))
    second_window.title("Select the Date and Time Range")

    screen_width = second_window.winfo_screenwidth()
    screen_height = second_window.winfo_screenheight()
    window_width = 530
    window_height = 400
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    second_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Date Selection
    start_date_label = tk.Label(second_window, text="Start Date:")
    start_date_label.grid(row=0, column=0, padx=5, pady=5)
    start_calendar = Calendar(second_window, selectmode="day", date_pattern="yyyy-mm-dd")
    start_calendar.grid(row=1, column=0, padx=5, pady=5)
    
    end_date_label = tk.Label(second_window, text="End Date:")
    end_date_label.grid(row=0, column=1, padx=5, pady=5)
    end_calendar = Calendar(second_window, selectmode="day", date_pattern="yyyy-mm-dd")
    end_calendar.grid(row=1, column=1, padx=5, pady=5)

    # Time Selection
    start_time_label = tk.Label(second_window, text="Start Time:")
    start_time_label.grid(row=2, column=0, padx=5, pady=5)
    start_time_entry = tk.Entry(second_window)
    start_time_entry.insert(0, (datetime.now() - timedelta(hours=1)).strftime("%H:%M:%S"))  # Default to current time
    start_time_entry.grid(row=2, column=1, padx=5, pady=5)

    end_time_label = tk.Label(second_window, text="End Time:")
    end_time_label.grid(row=3, column=0, padx=5, pady=5)
    end_time_entry = tk.Entry(second_window)
    end_time_entry.insert(0, datetime.now().strftime("%H:%M:%S"))  # Default to current time
    end_time_entry.grid(row=3, column=1, padx=5, pady=5)

    options = ["Output Images","Input Images","Both"]
    selected_option = tk.StringVar()
    select_label = tk.Label(second_window, text="Select the options:")
    select_label.grid(row=4, column=0, padx=5, pady=5)
    select_box = ttk.Combobox(second_window, textvariable=selected_option, values=options)
    select_box.grid(row=4, column=1, padx=5, pady=5)

    # Submit button
    process_button = tk.Button(second_window, text="Submit", command=submit)
    process_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

############## Date and Time################
def update_datetime():
    current_datetime = datetime.now()
    current_date = current_datetime.strftime("%d/%m/%Y")
    current_time = current_datetime.strftime('%I:%M:%S %p')
    date_label.config(text=f"DATE: {current_date}")
    time_label.config(text=f"TIME: {current_time}")
   
    win.after(1000, update_datetime)  # Update every second (1000 milliseconds)


date_label = tk.Label(win, font=('Helvetica',15, 'bold'),bg='#405D72')
date_label.place(relx=0.2,rely=0.02)
# date_label.config(bg='#b5dbf2')

time_label = tk.Label(win, font=('Helvetica',15, 'bold'),bg='#405D72')

time_label.place(relx=0.68, rely=0.02)
# time_label.config(bg='#b5dbf2')
update_datetime()  # Start the initial update
##################################################


btn_SaveMode = tk.Button(win, text="Start Mode", font=('Helvetica 13 bold'),
                        width=15, height=1, relief=tk.RAISED,bg="#CDC2A5", borderwidth=3, command=capture_image_save)
btn_SaveMode.place(relx=0.42, rely=0.67)

btn_ok = tk.Button(win, text='Filter Images', font=('Helvetica 11 bold'),
                width=16, height=1, relief=tk.RAISED, borderwidth=3, command=open_second_window, bg="#CDC2A5")
btn_ok.place(relx=0.65,rely=0.67)
btn_destroy = tk.Button(win, text="Exit", font=('Helvetica 13 bold'),
                        width=12, height=1, relief=tk.RAISED, bg="red",borderwidth=3, command=exit_app)
btn_destroy.place(relx=0.87,rely=0.1)

status_label = tk.Label(win, text="Version 4.0 (BETA)",font= ('Helvetica 11 bold'),bg='#405D72')
status_label.place(relx=0.46,rely=0.96)

machine_label = tk.Label(win, text=f"Machine {machine_no}",font=('Helvetica', 18, 'bold'),fg="#fa0a0a",bg='#CDC2A5',borderwidth=2, relief="solid")
machine_label.place(relx=0.46, rely=0.02)
# machine_label.config(bg='#b5dbf2')

lbl_mode = tk.Label(win, text="", font=('Helvetica 10 bold'))
lbl_mode.place(relx=0.15, rely=0.23)

#####################count setter ####################################
def InspectionCount():
    today_date = datetime.now().strftime("%d-%m-%Y")
    # Count documents with decision: "Accept" for today
    total_count = mycollec.count_documents({"cur_date": today_date})
    if total_count == None:
        total_count = 0
 
    # print(df_filtered)
    inslbl.config(text=total_count)  # Update the label text
 
    # Schedule the next update after 1 second (1000 milliseconds)
    win.after(1000, InspectionCount)
 
inslbl = tk.Label(win, bg='#405D72',font=('Helvetica', 20, 'bold'),
               foreground='black')
inslbl.place(relx=0.54, rely=0.3)
InspectionCount()
tk.Label(win, text="INSPECTION COUNT :", bg='#405D72',font=(
    'Helvetica', 18,'bold')).place(relx=0.4, rely=0.3)
 
 
 
def DefectCount():
    # Get today's date in the required format
    today_date = datetime.now().strftime("%d-%m-%Y")
 
    # Count documents with decision: "Reject" for today
    reject_count = mycollec.count_documents({"cur_date": today_date, "Result":1})
    if reject_count == None:
        reject_count = 0
    defectlabel.config(text=reject_count)
    win.after(1000, DefectCount)  # Update every second (1000 milliseconds)
 
 
defectlabel = tk.Label(win,bg='#405D72', font=('Helvetica', 20, 'bold'),
                    foreground='red', text='')
defectlabel.place(x=1400, y=300)

tk.Label(win, text="DEFECT COUNT : ",bg='#405D72', font=(
    'Helvetica', 18,'bold')).place(relx=0.62, rely=0.3)
DefectCount()
 
# ############################# GOOD PART LABEL#################
def goodcount():
    # Get today's date in the required format
    today_date = datetime.now().strftime("%d-%m-%Y")
    # Count documents with decision: "Accept" for today
    accept_count = mycollec.count_documents({"cur_date": today_date, "Result":0})
    if accept_count == None:
        accept_count = 0
    goodlabl.config(text=accept_count)
    win.after(1000, goodcount)  # Update every second (1000 milliseconds)
 
goodlabl = tk.Label(win,bg='#405D72', font=('Helvetica', 20, 'bold'),
                 foreground='green', text='')
goodlabl.place(x=1730, y=300)
 
 
tk.Label(win,bg='#405D72', text="GOOD COUNT : ", font=(
    'Helvetica', 18,'bold')).place(relx=0.8, rely=0.3)
goodcount()
# win.overrideredirect(True)
win.mainloop()