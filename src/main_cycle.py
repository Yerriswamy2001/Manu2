import os,time
import cv2
from datetime import datetime
from src.MODEL.Fourier_transform import process_image_for_anomaly 
from src.COMMON.common import nparray_to_bytes,recent_cycle,thread_func
from src.camfile.camconnection import *

def main_process_save_plc(asi,modbus_client,MEDIA_PATH,mydb):
    asi.flag = False
 
    while (True):
    # while (True):
       
        cycle_no = recent_cycle(mydb)
        print('cycle_no',cycle_no)
        current_time = datetime.now()
        formatted_datetime = current_time.strftime("%Y-%m-%d_%H-%M-%S")
        formatted_date = datetime.strptime(formatted_datetime, "%Y-%m-%d_%H-%M-%S")
        format_date_imagename = formatted_date.strftime('%d%m%Y')
        file_raw = str(cycle_no) + '_INPUT_'+format_date_imagename+'.jpg'
        # file_output = str(cycle_no) + '_OUTPUT_'+format_date_imagename+'.jpg'
 
        #Model
        if asi.flag == True:
            print("cam exit")
            break
        try:
            while (read_mem(modbus_client,61) != True):
                if asi.flag == True:
                    break
                continue
        except:
            while (modbus_client != True):
                continue
            continue
        os.system('cls')
        start = time.time()
 
        if asi.flag == True:
            print("cam exit")
            break
        time.sleep(0.06)
        st_time = time.time()
 
        img = get_image(asi.device)
        img1 = cv2.merge([img, img, img])
        format_date_db = formatted_date.strftime('%d-%m-%Y')
       
      
        
        result, mse_loss = process_image_for_anomaly(img1, cycle_no,mydb,file_raw,MEDIA_PATH,format_date_db , thresh_1=2.6000000000000e-05,thresh_2=2.8999999999999e-05)
        error_str = str(result).replace(" ", "_").replace(":", "-") if mse_loss else "no_error"  # Simple sanitization
        file_raw = f"{cycle_no}_INPUT_{result}_{error_str}_{format_date_imagename}.jpg"
        # file_output = f"{cycle_no}_OUTPUT_{is_anomalous}_{error_str}_{format_date_imagename}.jpg"

        
        formatted_datetime_db = current_time.strftime("%d-%m-%Y %H:%M:%S")
        thread_func(nparray_to_bytes, cycle_no, mydb, file_raw, "INPUT IMAGES", img1, format_date_db, formatted_datetime_db)

        # file_output = f"{cycle_no}_OUTPUT_{is_anomalous}_{error_str}_{format_date_imagename}.jpg"
 
       #Decision
        if  result == "Anomaly":
            decision = "Reject"
            write_mem(modbus_client,64, 1)
            time.sleep(0.03)
            write_mem(modbus_client,63, 1)
        else:
           decision = "Accept"
        time.sleep(0.03)
        write_mem(modbus_client,64, 0)
        write_mem(modbus_client,63, 0)
        end = time.time()
        cycle_time = end-start
        print(decision,"result")
        insert_dict = {
            'cycle_no':cycle_no,
            'inspectionDatetime': formatted_datetime_db,
            'cur_date':format_date_db,
            'file_input':file_raw,
            'is_anomalous':result,
            "error": float(mse_loss),
            'decision':decision
        }
        mydb["MAIN"].insert_one(insert_dict)
        en_time = time.time()
        cycle_time = en_time-st_time
        print(f"Cycle time {round(cycle_time,2)} in Sec")
        if cycle_time < 0.9:
            time.sleep(0.9-cycle_time)
