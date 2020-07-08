# smart_classroom

## Python requirements
Added a requirements.txt for used python libraries.


To use the requirements.txt first activate the virtual environment via "source venv/bin/activate".  
To install packages from the requirements.txt use "pip install -r requirements.txt".  
To save all/new packages for the project into the requirement use "pip freeze > requirements.txt".  
Use all of this only while the venv is activated, elese all your global packages will be saved into the requirements.txt!  

## Webpage
To use the webpage, first install node and npm https://www.npmjs.com/get-npm .  
Secondly go with your terminal to the folder presentation where the package.json lies. Execute "npm install" in your terminal.  
Lastly to compile the webpage execute "webpack" or if this is not found "./node_modules/webpack/bin/webpack.js".  
To finally run the webpage go to the dist folder and run "python -m http.server 8000". The webpage will open under localhost:8000.
