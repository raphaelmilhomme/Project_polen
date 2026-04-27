This is the description of the project of the Group number 12.09
We installed these libraries...


READ ME Plant Identifier:
1. Goals:
- Use a data base and deep learning to make a plant identifier where one can put some photos, to see if the plant has pollen
- Identifies XXX Swiss plant species using an EfficientNetB0 deep learning model
- When you give a photo the web site will give you: the english scientific and common name, and Allergen information: intensity level, pollen season, and symptoms.

2. Model Details

- Architecture: EfficientNetB0 (fine-tuned)
- Classes: 147 Swiss plant species
- Input: 224×224 RGB images
- Top-1 Accuracy: XXX
- Top-5 Accuracy: XXX
- Format: ONNX (CPU inference via onnxruntime)
- Training Dataset: PlantCLEF (Kaggle)

3. Requirement:
- See above

4. Data source:
- PlanClef (1000 species of plant common in France) then I selected them according to thre criterias:
i. At least 60 photos
ii. Common in Switzerland
iii. And add the one with high allergen

5.Allergen Database
- The app includes allergen data for 28+ key Swiss species including:
i. Very High: Cocksfoot (Dactylis glomerata), Mugwort (Artemisia vulgaris)
ii. High: Silver Birch (Betula pendula), Common Ash (Fraxinus excelsior), Perennial Ryegrass (Lolium perenne)
iii. Moderate: Common Hornbeam (Carpinus betulus), Sessile Oak (Quercus petraea)
iV. Low: Norway Spruce (Picea abies), Small Leaved Lime (Tilia cordata)


6.How Plant Identification Works

- User uploads one or more photos of the same plant
- Each image is resized to 224×224 and normalized
- The ONNX model runs inference on each image
- Probabilities are averaged across all uploaded photos
- The top prediction is shown with allergen information
- 3 alternative species are listed as fallback options
