# roommates

#install condo for managing python packages

#create virtual env
`conda create -n dbms`

#activate
`conda activate dbms`

#install fastapi
`conda install -c conda-forge fastapi`

install pymysql
`conda install -c anaconda pymysql`

install uvicorn
`conda install -c conda-forge uvicorn-standard`

#run app
`uvicorn app:app --reload`
