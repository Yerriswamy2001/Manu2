import os,time
import cv2
from datetime import datetime
from src.MODEL.Fourier_transform import process_image_for_anomaly
from src.MODEL.auto_encoder import process_image_for_anomaly1
from src.COMMON.common import nparray_to_bytes,recent_cycle,thread_func
from src.camfile.camconnection import *

# #local process code with out plc
# def main_process_save(asi,MEDIA_PATH,mydb,model):
#     num_cycles = 10
#     cycle_count = 0

#     while cycle_count < num_cycles:
#     # while (True):
#         st_time = time.time()
#         cycle_no = recent_cycle(mydb)
#         print('cycle_no',cycle_no)
#         current_time = datetime.now()
#         formatted_datetime = current_time.strftime("%Y-%m-%d_%H-%M-%S")
#         formatted_date = datetime.strptime(formatted_datetime, "%Y-%m-%d_%H-%M-%S")
#         format_date_imagename = formatted_date.strftime('%d%m%Y')
#         file_raw = str(cycle_no) + '_INPUT_'+format_date_imagename+'.jpg'
#         # file_output = str(cycle_no) + '_OUTPUT_'+format_date_imagename+'.jpg'

#         #Model
#         img = cv2.imread(os.path.join(MEDIA_PATH,'RAW IMAGES/2.jpg'))
#         format_date_db = formatted_date.strftime('%d-%m-%Y')
        
#         is_anomalous, error = process_image_for_anomaly(img, model, cycle_no,mydb,file_raw,MEDIA_PATH,format_date_db,threshold=0.004952204937580973, center_x=929, center_y=638, radius=430, inr=350)
#         error_str = str(error).replace(" ", "_").replace(":", "-") if error else "no_error"  # Simple sanitization
#         file_raw = f"{cycle_no}_INPUT_{is_anomalous}_{error_str}_{format_date_imagename}.jpg"
#         # file_output = f"{cycle_no}_OUTPUT_{is_anomalous}_{error_str}_{format_date_imagename}.jpg"

        
#         formatted_datetime_db = current_time.strftime("%d-%m-%Y %H:%M:%S")

#         thread_func(nparray_to_bytes, cycle_no, mydb, file_raw, "INPUT IMAGES", img, format_date_db, formatted_datetime_db)


#         insert_dict = {
#             'cycle_no':cycle_no,
#             'inspectionDatetime': formatted_datetime_db,
#             'cur_date':format_date_db,
#             'file_input':file_raw,
#             'is_anomalous': bool(is_anomalous),
#             "error": float(error), 
#         }
#         if is_anomalous:
#             mydb["ANOMALOUS_COLLECTION"].insert_one(insert_dict)
#         else:
#             mydb["NON_ANOMALOUS_COLLECTION"].insert_one(insert_dict)
#         mydb["MAIN"].insert_one(insert_dict)
#         en_time = time.time()
#         print(en_time-st_time,'cycle time')
#         cycle_count += 1

#local process code with out plc
def main_process_save(asi,MEDIA_PATH,mydb):
    num_cycles = 10
    cycle_count = 0

    while cycle_count < num_cycles:
    # while (True):
        st_time = time.time()
        cycle_no = recent_cycle(mydb)
        print('cycle_no',cycle_no)
        current_time = datetime.now()
        formatted_datetime = current_time.strftime("%Y-%m-%d_%H-%M-%S")
        formatted_date = datetime.strptime(formatted_datetime, "%Y-%m-%d_%H-%M-%S")
        format_date_imagename = formatted_date.strftime('%d%m%Y')
        file_raw = str(cycle_no) + '_INPUT_'+format_date_imagename+'.jpg'
        # file_output = str(cycle_no) + '_OUTPUT_'+format_date_imagename+'.jpg'

        #Model
        img = cv2.imread(os.path.join(MEDIA_PATH,'RAW IMAGES/2.jpg'))
        format_date_db = formatted_date.strftime('%d-%m-%Y')
        
        result, mse_loss = process_image_for_anomaly(img, cycle_no,mydb,file_raw,MEDIA_PATH,format_date_db , thresh_1=2.6000000000000e-05,thresh_2=2.8999999999999e-05)
        error_str = str(result).replace(" ", "_").replace(":", "-") if mse_loss else "no_error"  # Simple sanitization
        file_raw = f"{cycle_no}_INPUT_{result}_{error_str}_{format_date_imagename}.jpg"
        # file_output = f"{cycle_no}_OUTPUT_{is_anomalous}_{error_str}_{format_date_imagename}.jpg"

        
        formatted_datetime_db = current_time.strftime("%d-%m-%Y %H:%M:%S")
        thread_func(nparray_to_bytes, cycle_no, mydb, file_raw, "INPUT IMAGES", img, format_date_db, formatted_datetime_db)

        # if result == "anomaly":
        #     # Save in the "ANOMALY IMAGES" collection or folder
        #     thread_func(nparray_to_bytes, cycle_no, mydb, file_raw, "ANOMALY IMAGES", img, format_date_db, formatted_datetime_db)
        # else:
        #     # Save in the "GOOD IMAGES" collection or folder
        #     thread_func(nparray_to_bytes, cycle_no, mydb, file_raw, "GOOD IMAGES", img, format_date_db, formatted_datetime_db)

        if result == "Anomaly":
            decision = "Reject"
        else:
            decision = "Accept"

        print(decision, "decision")
        insert_dict = {
            'cycle_no':cycle_no,
            'inspectionDatetime': formatted_datetime_db,
            'cur_date':format_date_db,
            'file_input':file_raw,
            'is_anomalous':result,
            "error": float(mse_loss), 'decision':decision
        }
        # if is_anomalous:
        #     mydb["ANOMALOUS_COLLECTION"].insert_one(insert_dict)
        # else:
        #     mydb["NON_ANOMALOUS_COLLECTION"].insert_one(insert_dict)
        mydb["MAIN"].insert_one(insert_dict)
        en_time = time.time()
        print(en_time-st_time,'cycle time')
        cycle_count += 1