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






READ ME Home:
1. Goals:
- Offer a real time pollen forecast web app built for people who suffer of pollen allergies in Switzerland, principally in cities



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

3. Requirement:
- See above

4. Data source:
- iNaturalist Free API api.inaturalist.org/v1/observations (no key=; filter place_id=6753 - Research grade only
- PlanClef (1000 species of plant common in France) then I selected them according to thre criterias:

i. At least 100 photos
ii. Common in Switzerland
iii. And add the one with high allergen

5.Allergen Database
- The app includes allergen data for 28+ key Swiss species including:
ii. High: Silver Birch (Betula pendula), Common Ash (Fraxinus excelsior), Perennial Ryegrass (Lolium perenne)
iii. Moderate: Common Hornbeam (Carpinus betulus), Sessile Oak (Quercus petraea)
iV. Low: Norway Spruce (Picea abies), Small Leaved Lime (Tilia cordata)


6.How Plant Identification Works

- User uploads one or more photos of the same plant
- Each image is resized to 300*300 and normalized
- The ONNX model runs inference on each image
- Probabilities are averaged across all uploaded photos
- The top prediction is shown with allergen information
- 3 alternative species are listed as fallback options

7. Training
- Phase 1: Train head only (10 epochs, lr=0.001)
- Phase 2: Full fine-tuning (50 epochs, lr=0.0001)
- Data augmentation: rotation, zoom, brightness, flip
- Min 100 photos per species required
- See training/blessyou_final_training.py for full code

