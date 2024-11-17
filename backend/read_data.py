import pandas as pd
import time
import os
import json
import random
import numpy as np
import io

pd.set_option('display.max_colwidth', None)

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



def read_json_file(json_path):
    """Helper function to read JSON file with extensive error handling"""
    # First try: Read line by line and fix common JSON issues
    try:
        data = []
        with open(json_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            
            # Check if content is wrapped in brackets
            if not content.startswith('['):
                content = '[' + content + ']'
            
            # Try to parse the entire content
            try:
                return pd.DataFrame(json.loads(content))
            except:
                # If that fails, try to parse line by line
                lines = content.strip('[]').split('\n')
                for line in lines:
                    line = line.strip().strip(',')  # Remove whitespace and trailing commas
                    if line:  # Skip empty lines
                        try:
                            # Try to parse the line as JSON
                            parsed_line = json.loads(line)
                            data.append(parsed_line)
                        except json.JSONDecodeError:
                            # If line parsing fails, try to fix common issues
                            try:
                                # Replace single quotes with double quotes
                                line = line.replace("'", '"')
                                # Ensure proper quote wrapping for keys
                                line = line.replace('"{', '{').replace('}"', '}')
                                parsed_line = json.loads(line)
                                data.append(parsed_line)
                            except:
                                continue
                
                if data:
                    return pd.DataFrame(data)
                
    except Exception as e:
        print(f"Error reading JSON file: {str(e)}")
    
    # If all attempts fail, try pandas read_json with different settings
    try:
        return pd.read_json(json_path, lines=True)
    except:
        try:
            return pd.read_json(json_path)
        except:
            pass
    
    raise ValueError(f"Could not read JSON file at {json_path}. The file might be corrupted or in an invalid format.")

def clean_for_json(value):
    """Convert non-serializable values to JSON-compatible format"""
    try:
        # Handle numpy arrays and pandas Series
        if isinstance(value, (np.ndarray, pd.Series)):
            return clean_for_json(value.tolist())
        # Handle lists and other iterables
        elif isinstance(value, (list, tuple)):
            return [clean_for_json(v) for v in value]
        # Handle individual values
        elif pd.api.types.is_float(value):
            return None if np.isnan(value) else float(value)
        elif isinstance(value, (np.int64, np.int32)):
            return int(value)
        elif isinstance(value, pd.Timestamp):
            return value.isoformat()
        elif pd.api.types.is_scalar(value) and pd.isna(value):
            return None
        return value
    except:
        return None

def jumble_data(tsv_path, json_path):
    # Read TSV with all values as strings initially to preserve data
    df_tsv = pd.read_csv(tsv_path, sep='\t', dtype=str)
    
    # Split the data into informative and not_informative
    df_informative = df_tsv[df_tsv['text_info'] == 'informative'].copy()
    print(df_informative.head(2))
    df_not_informative = df_tsv[df_tsv['text_info'] == 'not_informative'].copy()
    print(df_not_informative.head(2))
    
    # Load JSON data using the helper function
    try:
        df_json = read_json_file(json_path)
        print(f"Successfully read JSON file. Shape: {df_json.shape}, Columns: {df_json.columns.tolist()}")
    except Exception as e:
        print(f"Error details: {str(e)}")
        # Print first few lines of the JSON file for debugging
        with open(json_path, 'r', encoding='utf-8') as f:
            print("First few lines of JSON file:")
            print(f.read(500))
        raise
    
    # Validate required columns
    if 'id' not in df_json.columns or 'created_at' not in df_json.columns:
        raise ValueError("JSON data must contain 'id' and 'created_at' fields.")
    
    # Convert tweet_id to string in both dataframes to ensure matching
    df_informative['tweet_id'] = df_informative['tweet_id'].astype(str)
    df_json['id'] = df_json['id'].astype(str)
    
    # Merge with explicit handling of null values
    df_informative = df_informative.merge(
        df_json,
        left_on='tweet_id',
        right_on='id',
        how='left'
    )
    
    # Handle date sorting while preserving null values
    def safe_date_convert(date_val):
        if pd.isna(date_val) or date_val == '' or date_val is None:
            return pd.NaT
        return pd.to_datetime(date_val, errors='coerce')
    
    df_informative['date'] = df_informative['created_at'].apply(safe_date_convert)
    df_informative_sorted = df_informative.sort_values(
        by='date',
        na_position='first'
    )
    
    # Get the complete set of columns from both dataframes
    all_columns = list(set(df_informative_sorted.columns) | set(df_not_informative.columns))
    
    # Initialize missing columns in both dataframes
    for col in all_columns:
        if col not in df_informative_sorted.columns:
            df_informative_sorted[col] = None
        if col not in df_not_informative.columns:
            df_not_informative[col] = None
    
    # Ensure both dataframes have exactly the same columns in the same order
    df_informative_sorted = df_informative_sorted[all_columns]
    df_not_informative = df_not_informative[all_columns]
    
    # Concatenate the dataframes
    mixed_data = pd.concat(
        [df_not_informative, df_informative_sorted],
        ignore_index=True,
        copy=True
    )
    
    # Shuffle not_informative entries
    not_informative_indices = mixed_data[mixed_data['text_info'] == 'not_informative'].index.tolist()
    informative_indices = mixed_data[mixed_data['text_info'] == 'informative'].index.tolist()
    random.shuffle(not_informative_indices)
    
    # Create final dataset
    final_indices = not_informative_indices + informative_indices
    mixed_data = mixed_data.reindex(final_indices).reset_index(drop=True)
    
    # Convert DataFrame to list of dicts and clean the data
    json_result = [
        {k: clean_for_json(v) for k, v in record.items()}
        for record in mixed_data.replace({np.nan: None}).to_dict(orient='records')
    ]
    
    # Write back to JSON file
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_result, json_file, indent=4)
    
    return mixed_data

class DataQuery:
    def __init__(self, file_name, path="data/CrisisMMD_v2.0/json/"):
        self.file_name = file_name
        self.df = pd.read_json(f'{path}{file_name}',lines=True)
        self.index = 0
    
    def get_next(self):
        if self.index < len(self.df):
            row = self.df.iloc[self.index]
            self.index += 1
            date_str = row["created_at"]
            date_obj = pd.to_datetime(date_str, format='%a %b %d %H:%M:%S %z %Y')
            formatted_date = date_obj.strftime('%d_%m_%Y')
            formatted_date = "_".join(str(int(part)) for part in formatted_date.split("_"))
            img_path = "data/CrisisMMD_v2.0/data_image/" + row["location"] + "/" + formatted_date + "/"
            matching_files = [f for f in os.listdir(img_path) if str(row["id"]) in f and f[0]!="."]
            img_paths = [img_path + f for f in matching_files]
            if len(img_paths) > 0:
                return row["id"], row["text"], row["location"], img_paths
            else:
                return row["id"], row["text"], row["location"], None
        else:
            raise StopIteration("No more rows in DataFrame")
        
def mix_data(tsv_path, json_path, output_path):
    tsv_df = pd.read_csv(tsv_path, sep='\t')
    with open(json_path, 'r') as file:  # Replace with your file path
        valid_lines = []
        for idx, line in enumerate(file, start=1):
            stripped = line.strip()
            # Check if the line starts with valid JSON structures
            if stripped and stripped[0] in '{[':
                try:
                    # Validate if the line is valid JSON
                    pd.json_normalize([pd.read_json(io.StringIO(stripped), typ='series')])
                    valid_lines.append(stripped)
                except ValueError as e:
                    print(f"Skipping malformed line {idx}: {stripped}\nError: {e}")

    # Combine valid lines into a single string
    valid_json = "\n".join(valid_lines)

    # Load the cleaned JSON lines into a pandas DataFrame
    json_df = pd.read_json(io.StringIO(valid_json), lines=True)
    json_df = json_df.replace([np.nan], [None])
    tsv_df.rename(columns={'tweet_id': 'id'}, inplace=True)
    merged_df = pd.merge(tsv_df, json_df, on='id', how='inner')
    df_informative = merged_df[merged_df['text_info'] == 'informative']
    df_not_informative = merged_df[merged_df['text_info'] == 'not_informative']
    df_informative['created_at'] = pd.to_datetime(df_informative['created_at'])

    # Sort by the 'created_at' column
    df_informative_sorted = df_informative.sort_values(by='created_at')
    
    df_not_informative_shuffled = df_not_informative.sample(frac=1, random_state=42).reset_index(drop=True)

    # Get the number of rows in each dataframe
    num_informative = len(df_informative_sorted)
    num_not_informative = len(df_not_informative_shuffled)

    # Create a weight distribution for intercalation (higher weight near the start)
    weights = np.linspace(1, 0.2, num_informative)  # Linear decrease in weight
    normalized_weights = weights / weights.sum()

    # Randomly intercalate rows from df_not_informative
    intercalation_indices = np.random.choice(
        range(num_informative),
        size=min(num_not_informative, num_informative),
        replace=False,
        p=normalized_weights
    )
    df_combined = df_informative_sorted.copy()
    for i, idx in enumerate(sorted(intercalation_indices)):
        # Insert rows from df_not_informative into df_combined
        row_to_insert = df_not_informative_shuffled.iloc[i]
        df_combined = pd.concat(
            [df_combined.iloc[:idx], pd.DataFrame([row_to_insert]), df_combined.iloc[idx:]]
        ).reset_index(drop=True)

    df_combined = df_combined.replace([np.nan], [None])
    df_combined["created_at"] = df_combined["created_at"].astype(str)
    df_combined["timestamp_ms"] = df_combined["timestamp_ms"].astype(str)

    df_combined.drop_duplicates(subset='id', inplace=True)

    # Save the combined dataframe to a new JSON file
    df_combined.to_json(output_path, orient="records", lines=True)

    # Write JSON without escaping forward slashes
    # with open(output_path, "w", encoding="utf-8") as f:
    #     json.dump(data, f, ensure_ascii=False)

def process_files(annotation_dir, json_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get lists of files in both directories
    annotation_files = os.listdir(annotation_dir)
    json_files = os.listdir(json_dir)
    # done = [file.split(".")[0] for file in os.listdir(output_dir) if file[0] != "."]
    for tsv_name in annotation_files:
        if tsv_name[0] != "." and "_".join(tsv_name.split('_')[:2]):
            name = "_".join(tsv_name.split('_')[:2])
            json_name = [file for file in json_files if name in file][0]
            print(f"Doing {tsv_name} and {json_name}")
            mix_data(f"{annotation_dir}/{tsv_name}", f"{json_dir}/{json_name}", f"{output_dir}/{name}.json")
            

# tsv_path = 'C:/Users/usuario/Desktop/se rompio el disco/uni/hackathons/Meta 2024/LlamaImpactHackathon/backend/data/CrisisMMD_v2.0/annotations/california_wildfires_final_data.tsv'
# json_path = 'C:/Users/jonai/Code/LlamaImpactHackathon/backend/data/CrisisMMD_v2.0/json/combined_shuffled_tweets.json'
# mix_data(tsv_path, json_path, "sorted_data.json")
# data_dir = os.getcwd() + "\\data\\CrisisMMD_v2.0"
# process_files(f"{data_dir}\\annotations", f"{data_dir}\\json", f"{data_dir}\\merged")
#dq = DataQuery("california_wildfires_final_data.json")
#print(dq.get_next())
#print(dq.get_next())
#print(dq.get_next())
#print(dq.get_next())
#print(dq.get_next())