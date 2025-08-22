import os
import tempfile
import pandas as pd
from datetime import datetime
from huggingface_hub import HfApi
from typing import Union, Optional

def upload_dataframe_to_hf(
    df: pd.DataFrame, 
    repo_id: str, 
    filename: str = "posts.csv",
    repo_type: str = "dataset"
) -> str:
    try:
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            return "❌ No HF_TOKEN environment variable set"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            df.to_csv(tmp.name, index=False)
            temp_path = tmp.name
        
        try:
            api = HfApi()
            api.upload_file(
                path_or_fileobj=temp_path,
                path_in_repo=filename,
                repo_id=repo_id,
                repo_type=repo_type,
                token=hf_token,
                commit_message=f"Update {filename} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            return f"✅ Successfully uploaded {filename} to {repo_id}"
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        return f"❌ Upload failed: {str(e)}"

def upload_csv_file(
    file_path: str, 
    repo_id: str, 
    filename: Optional[str] = None,
    repo_type: str = "dataset"
) -> str:
    try:
        if not os.path.exists(file_path):
            return f"❌ File not found: {file_path}"
        
        if filename is None:
            filename = os.path.basename(file_path)
        
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            return "❌ No HF_TOKEN environment variable set"
        
        api = HfApi()
        api.upload_file(
            path_or_fileobj=file_path,
            path_in_repo=filename,
            repo_id=repo_id,
            repo_type=repo_type,
            token=hf_token,
            commit_message=f"Upload {filename} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        return f"✅ Successfully uploaded {filename} to {repo_id}"
        
    except Exception as e:
        return f"❌ Upload failed: {str(e)}"

def create_hf_dataset(
    df: pd.DataFrame, 
    repo_id: str, 
    dataset_name: str = "posts_dataset"
) -> str:
    try:
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            return "❌ No HF_TOKEN environment variable set"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            df.to_csv(tmp.name, index=False)
            temp_path = tmp.name
        
        try:
            api = HfApi()
            api.upload_file(
                path_or_fileobj=temp_path,
                path_in_repo=f"{dataset_name}.csv",
                repo_id=repo_id,
                repo_type="dataset",
                token=hf_token,
                commit_message=f"Create dataset {dataset_name} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            return f"✅ Successfully created dataset {dataset_name} in {repo_id}"
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        return f"❌ Dataset creation failed: {str(e)}"

def validate_repo_id(repo_id: str) -> bool:
    if not repo_id:
        return False
    
    if '/' not in repo_id:
        return False
    
    import re
    pattern = r'^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, repo_id))
