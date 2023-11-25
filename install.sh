conda remove -n dbms --all  
conda create -n dbms
conda activate dbms
conda install -c conda-forge fastapi=0.98.0
conda install -c anaconda pymysql
conda install -c conda-forge uvicorn-standard
conda install -c conda-forge python-decouple
conda install -c conda-forge python-jose
#conda install -c conda-forge python-multipart
uvicorn app:app --reload