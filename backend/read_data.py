import pandas as pd
import time
import os

def sim_msg(info):
    print(info["text"])

# Simulation function
def simulate_dataframe(df, time_col, speed_factor, limit=None):
    previous_time = None
    for i, row in df.iterrows():
        if previous_time is None:
            sim_msg(row)
            previous_time = row[time_col]
        else:
            current_time = row[time_col]
            time_diff = (current_time - previous_time).total_seconds()
            time.sleep(time_diff * speed_factor)
            sim_msg(row)
            previous_time = current_time
        if limit is not None and i == limit-1:
            print(f"Limit of {limit} rows reached, stopping simulation")
            break

def read_data_realistic():
    data=pd.read_json('california_wildfires_final_data.json',lines=True)
    sorted_df = data.sort_values(by='created_at', ascending=True)
    simulate_dataframe(sorted_df, time_col='created_at', speed_factor=0.01, limit=3)

class DataQuery:
    def __init__(self, file_name, path="data/CrisisMMD_v2.0/json/"):
        self.file_name = file_name
        self.df = pd.read_json(f'{path}{file_name}',lines=True).sort_values(by='created_at', ascending=True)
        self.index = 0
    
    def get_next(self):
        if self.index < len(self.df):
            row = self.df.iloc[self.index]
            self.index += 1
            date_str = row["created_at"]
            date_obj = pd.to_datetime(date_str, format='%a %b %d %H:%M:%S %z %Y')
            formatted_date = date_obj.strftime('%d_%m_%Y')
            img_path = "data/CrisisMMD_v2.0/data_image/" + self.file_name[:self.file_name.rfind('_', 0, self.file_name.rfind('_'))] + "/" + formatted_date + "/"
            matching_files = [f for f in os.listdir(img_path) if str(row["id"]) in f and f[0]!="."]
            img_paths = [img_path + f for f in matching_files]
            if len(img_paths) > 0:
                return row["id"], row["text"], img_paths
            else:
                return row["id"], row["text"], None
        else:
            raise StopIteration("No more rows in DataFrame")
        
dq = DataQuery("california_wildfires_final_data.json")
print(dq.get_next())
print(dq.get_next())
print(dq.get_next())