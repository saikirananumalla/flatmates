conda remove -n dbms --all  
conda create -n dbms
conda activate dbms
conda install -c conda-forge fastapi=0.98.0 -y
conda install -c anaconda pymysql -y
conda install -c conda-forge uvicorn-standard -y
conda install -c conda-forge python-decouple -y
conda install -c conda-forge python-jose -y
conda install -c conda-forge python-multipart -y
uvicorn app:app --reload