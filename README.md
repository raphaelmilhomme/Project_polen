This is the description of the project of the Group number 12.09

Prerequisites:
-Python 3.11
-All required libraries are listed in requirements.txt
    -streamlit: the web app framework that turns python code into a visualised web app with buttons, sliders, charts
    -pandas: converts the data from the Open-Meteo API into a table to enable us to filter it by date, find peak pollen values and compute the best or worst day of the week
    -requests: calls data from external APIs: hourly pollen data and weather from Open-Meteo, find nearby pharmacies and doctors from OpenStreetMap API, detects the user's city by looking at their IP adress
    -numpy: handles missing pollen values by naming them NaN and removing those empty slots before doing calculations
    -folium + streamlit-folium: used to build the interactive Switzerland map with the "heated" dots around cities depending on the amounts of pollen, as well as the pharmacy and doctor pins. Streamlit-folium is used to show the map inside streamlit as this isn't a built in function
    -plotly: used to plot graphs, here it is the 5-day pollen forecast with one bar per selected pollen
    -onxruntime: loads and runs the plant identification machine learning model
    -pillow: opens plant photos, converts them into RGB file format with 300x 300 pixels before feeding them to the ML model
    -supabase: connecting the Community page to the database so we can save the comments, pollen sightings, tips...

-You can install them all at once with the command: pip install -r requirements.txt
-Run the app: streamlit run Home.py

Project description:
-BlessYou is a real time pollen forecast web app built for people who suffer of pollen allergies in Switzerland, especially in cities
-the website is built like this:
    Home Page:
        -You can enter your pollen allergies on the left with a choice of 5 different ones (Birch Grass, Mugwort, Hazel and Alder)
        -then you can enter your sensitivity level to each pollen
        -other informations can be added to your profile such as you location, your age group, whether you have asthma, whether you take medication for your pollen allergies, as well as how long you want to go outside today
        --> based on all this personnal information, the Open-Meteo Air Quality API and Weather API, as well as the OpenStreetMap API, the website shows you the current pollen levels of the ones you are allergic to and adapts the risk score based on your personal sensitivity and caracteristics. Then, the weather is shown, since this can have a significant impact on pollen levels. Your Personal Risk score based on all your personal information and daily pollen/ weather data is also shown. Based on this, the app can recommend you to take medications and when it would be better to go outside this week.
        -The "Switzerland Pollen Map" shows the pollen level in every major swiss city by clicking on the corresponding dots. You can also activate the Pharmacies and Doctors map, showing you their pins on the map in the city where you are located (marked with a small house).
        -The "5-Day Pollen Forecast" shows the levels of Pollen grains per m3 for the pollens you selected as being allergic to.
        -Finally, the "Nearby Pharmacies & Doctors" section enables you to show the list of pharmacies and doctors next to your selected location.
    
    Allergy Quiz:
        -It enables you to fill out your personal information, as well as potential symptoms you have felt in the past.
        -The goal is to try and detect potential pollen allergies that you might have, while not being aware of them.
    
    BlessYou Community:
        -Goal is for users to be able to communicate and share their experiences and tips.
        -First you can enter how you felt today regarding your allergies and compare it with other users.
        -Then you can look at various tips from other users for your selected location or in Switzerland as a whole.
        -You can also enter your own tips which will appear for all users.
        -The "Pollen Sightings" section enables you to report your personal experience as to what pollen you saw when going out.
        -Finally the Weekly discussion enables you to add other comments, tips or to discuss with random users. Each comment is posted with your allergies, as well as the risk rate for the day in which you posted the comment.

READ ME Plant Identifier:
1. Goals:
- Use a data base and deep learning to make a plant identifier where one can put some photos, to see if the plant has pollen
- Identifies 93 Swiss plant species using an EfficientNetB3 deep learning model
- When you give a photo the web site will give you: the english scientific and common name, and Allergen information: intensity level, pollen season, and symptoms.

2. Model Details

- Architecture: EfficientNetB3 (fine-tuned)
- Classes: 93 Swiss plant species
- Input: 300×300 RGB images
- Top-1 Accuracy: ~82%
- Top-5 Accuracy: ~95%
- Format: ONNX (CPU inference via onnxruntime)
- Training Dataset: PlantCLEF (Kaggle) + iNaturalist see training secction

3. Data source:
- iNaturalist Free API api.inaturalist.org/v1/observations (no key=; filter place_id=6753 - Research grade only
- PlanClef (1000 species of plant common in France) then I selected them according to thre criterias:

i. At least 100 photos
ii. Common in Switzerland
iii. And add the one with high allergen

4. Allergen Database
- The app includes allergen data for 28+ key Swiss species including:
ii. High: Silver Birch (Betula pendula), Common Ash (Fraxinus excelsior), Perennial Ryegrass (Lolium perenne)
iii. Moderate: Common Hornbeam (Carpinus betulus), Sessile Oak (Quercus petraea)
iV. Low: Norway Spruce (Picea abies), Small Leaved Lime (Tilia cordata)


5. How Plant Identification Works

- User uploads one or more photos of the same plant
- Each image is resized to 300*300 and normalized
- The ONNX model runs inference on each image
- Probabilities are averaged across all uploaded photos
- The top prediction is shown with allergen information
- 3 alternative species are listed as fallback options

6. Training
- Phase 1: Train head only (10 epochs, lr=0.001)
- Phase 2: Full fine-tuning (50 epochs, lr=0.0001)
- Data augmentation: rotation, zoom, brightness, flip
- Min 100 photos per species required
- See training/blessyou_final_training.py for full code

