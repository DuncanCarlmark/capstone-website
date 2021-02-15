# Capstone-Website
This is the web-application repository for the Parent-User music recommendation project

# How to run locally

### Step 1: Virtual Environment
In order to run the project locally we recommend that you create a virtual environment and install the packages listed in the **requirements.txt** file. You can just pip install the requirements locally, but using a virtual environment helps to ensure everything runs appropriately. 

### Step 2: Download Data
Our project uses publically available data from last.fm and billboard, and this data must be downloaded before running the project. To download the data just run the download_script.py file
```python3 download_script.py```
This will create a new data folder and place the raw data in a subfolder.

### Step 3: Launching Website
Once the environment is set up. In the root of the repository, run the command...
```python3 app.py```
This will locally start a development server on port **8080**. The website can then be accessed by a browser or through any other means of accessing port **8080** on your machine.

Once you have the actual site open, follow the rest of the instructions on the site to exectue the project.
