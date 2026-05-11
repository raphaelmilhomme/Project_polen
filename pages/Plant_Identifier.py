"""
This is the Plant Identifier feature of the BlessYou Swiss Pollen app.
It runs as a Streamlit page and is the only file in this project that
directly uses the trained ML model (model.onnx).
 
Purpose:
    Allow users to identify Swiss plant species from photos and check
    whether the identified plant is a known pollen allergen in Switzerland.
 
Pipeline position:
    model.onnx (from blessyou_final_training.py) -> Plant_Identifier.py -> Streamlit UI
 
Features:
    Tab 1 - Identify by Photo : upload one or more photos, model runs inference,
            displays scientific name, common name and allergen info.
    Tab 2 - Search by Name    : search any of the 93 species by common name.
    Tab 3 - All Species       : browse all 93 species split by allergen status.
 
 Notes if you want to see how I train thiss model on Kaggle, check the training section 
 
 Requiremnet:  streamlit    : web interface
    onnxruntime  : runs the ONNX model on CPU (no TensorFlow needed at inference)
    numpy        : array operations for preprocessing and softmax
    PIL (Pillow) : image loading and resizing
    datetime     : display today's date in the header

Sources: I used Claude AI sonnet 4.6:
 - to make the plant list (common and scientific name) 
 - to generate/correct my code 
 - To find the allergenes and the symptome
 
The model was develop on kaggle
    """




import streamlit as st # Import necessary libraries
import numpy as np
from PIL import Image
from datetime import datetime

 # configure the page with the title, icon and wide layout.
st.set_page_config(page_title="BlessYou - Plant Identifier", page_icon="🌻", layout="wide", initial_sidebar_state="expanded")


# Indicate where to find my model onnx
MODEL_PATH = "model.onnx" 


# resize photos to fit with my model
# Must match IMG_SIZE used in blessyou_final_training.py
IMG_SIZE = (300, 300) 


# The 93 species the model was trained on, in the exact order from class_names.json

CLASS_NAMES = [
  "Acer campestre","Acer platanoides","Acer pseudoplatanus","Achillea millefolium",
  "Aesculus hippocastanum","Agrimonia eupatoria","Ajuga reptans","Alliaria petiolata",
  "Alnus glutinosa","Amelanchier ovalis","Anemone nemorosa","Angelica sylvestris",
  "Aquilegia vulgaris","Asplenium trichomanes","Bellis perennis","Betula pendula",
  "Buxus sempervirens","Carpinus betulus","Centaurea jacea","Chelidonium majus",
  "Cichorium intybus","Cirsium arvense","Cirsium palustre","Cirsium vulgare",
  "Clematis vitalba","Convolvulus arvensis","Cornus mas","Cornus sanguinea",
  "Coronilla varia","Corylus avellana","Crataegus laevigata","Crataegus monogyna",
  "Cytisus scoparius","Daucus carota","Digitalis purpurea","Dipsacus fullonum",
  "Echium vulgare","Epilobium angustifolium","Epilobium hirsutum","Eupatorium cannabinum",
  "Euphorbia amygdaloides","Fagus sylvatica","Fraxinus excelsior","Geranium molle",
  "Geranium robertianum","Glechoma hederacea","Hedera helix","Heracleum sphondylium",
  "Hypochaeris radicata","Juglans regia","Lamium album","Lamium maculatum",
  "Lamium purpureum","Larix decidua","Ligustrum vulgare","Lonicera xylosteum",
  "Lotus corniculatus","Lysimachia vulgaris","Origanum vulgare","Papaver rhoeas",
  "Picris hieracioides","Pinus sylvestris","Plantago lanceolata","Populus tremula",
  "Primula veris","Prunus avium","Prunus mahaleb","Prunus padus","Prunus spinosa",
  "Quercus petraea","Quercus pubescens","Quercus robur","Rosa canina","Rubus idaeus",
  "Salix alba","Salix caprea","Sambucus ebulus","Sambucus nigra","Silene latifolia",
  "Silene vulgaris","Sorbus aria","Sorbus aucuparia","Sorbus torminalis",
  "Symphytum officinale","Taraxacum officinale","Tilia cordata","Tilia platyphyllos",
  "Trifolium pratense","Verbascum thapsus","Veronica chamaedrys","Veronica persica",
  "Viburnum lantana","Viburnum opulus"
]

# Maps scientific name -> English common name for all 93 species
COMMON_NAMES = {
  "Acer campestre":"Field Maple","Acer platanoides":"Norway Maple",
  "Acer pseudoplatanus":"Sycamore","Achillea millefolium":"Yarrow",
  "Aesculus hippocastanum":"Horse Chestnut","Agrimonia eupatoria":"Agrimony",
  "Ajuga reptans":"Bugle","Alliaria petiolata":"Garlic Mustard",
  "Alnus glutinosa":"Black Alder","Amelanchier ovalis":"Snowy Mespilus",
  "Anemone nemorosa":"Wood Anemone","Angelica sylvestris":"Wild Angelica",
  "Aquilegia vulgaris":"Common Columbine","Asplenium trichomanes":"Maidenhair Spleenwort",
  "Bellis perennis":"Common Daisy","Betula pendula":"Silver Birch",
  "Buxus sempervirens":"Common Box","Carpinus betulus":"Common Hornbeam",
  "Centaurea jacea":"Brown Knapweed","Chelidonium majus":"Greater Celandine",
  "Cichorium intybus":"Common Chicory","Cirsium arvense":"Creeping Thistle",
  "Cirsium palustre":"Marsh Thistle","Cirsium vulgare":"Spear Thistle",
  "Clematis vitalba":"Old Man Beard","Convolvulus arvensis":"Field Bindweed",
  "Cornus mas":"Cornelian Cherry","Cornus sanguinea":"Dogwood",
  "Coronilla varia":"Crown Vetch","Corylus avellana":"Common Hazel",
  "Crataegus laevigata":"Midland Hawthorn","Crataegus monogyna":"Common Hawthorn",
  "Cytisus scoparius":"Common Broom","Daucus carota":"Wild Carrot",
  "Digitalis purpurea":"Foxglove","Dipsacus fullonum":"Wild Teasel",
  "Echium vulgare":"Viper Bugloss","Epilobium angustifolium":"Rosebay Willowherb",
  "Epilobium hirsutum":"Great Willowherb","Eupatorium cannabinum":"Hemp Agrimony",
  "Euphorbia amygdaloides":"Wood Spurge","Fagus sylvatica":"Common Beech",
  "Fraxinus excelsior":"Common Ash","Geranium molle":"Dove Foot Cranesbill",
  "Geranium robertianum":"Herb Robert","Glechoma hederacea":"Ground Ivy",
  "Hedera helix":"Common Ivy","Heracleum sphondylium":"Common Hogweed",
  "Hypochaeris radicata":"Common Catsear","Juglans regia":"Common Walnut",
  "Lamium album":"White Dead Nettle","Lamium maculatum":"Spotted Dead Nettle",
  "Lamium purpureum":"Red Dead Nettle","Larix decidua":"European Larch",
  "Ligustrum vulgare":"Common Privet","Lonicera xylosteum":"Fly Honeysuckle",
  "Lotus corniculatus":"Birds Foot Trefoil","Lysimachia vulgaris":"Yellow Loosestrife",
  "Origanum vulgare":"Wild Marjoram","Papaver rhoeas":"Common Poppy",
  "Picris hieracioides":"Hawkweed Oxtongue","Pinus sylvestris":"Scots Pine",
  "Plantago lanceolata":"Ribwort Plantain","Populus tremula":"Aspen",
  "Primula veris":"Cowslip","Prunus avium":"Wild Cherry",
  "Prunus mahaleb":"St Lucie Cherry","Prunus padus":"Bird Cherry",
  "Prunus spinosa":"Blackthorn","Quercus petraea":"Sessile Oak",
  "Quercus pubescens":"Downy Oak","Quercus robur":"Pedunculate Oak",
  "Rosa canina":"Dog Rose","Rubus idaeus":"Raspberry",
  "Salix alba":"White Willow","Salix caprea":"Goat Willow",
  "Sambucus ebulus":"Dwarf Elder","Sambucus nigra":"Elder",
  "Silene latifolia":"White Campion","Silene vulgaris":"Bladder Campion",
  "Sorbus aria":"Common Whitebeam","Sorbus aucuparia":"Rowan",
  "Sorbus torminalis":"Wild Service Tree","Symphytum officinale":"Common Comfrey",
  "Taraxacum officinale":"Common Dandelion","Tilia cordata":"Small Leaved Lime",
  "Tilia platyphyllos":"Large Leaved Lime","Trifolium pratense":"Red Clover",
  "Verbascum thapsus":"Great Mullein","Veronica chamaedrys":"Germander Speedwell",
  "Veronica persica":"Common Field Speedwell","Viburnum lantana":"Wayfaring Tree",
  "Viburnum opulus":"Guelder Rose"
}

"""
Reverse lookup: common name (lowercase) -> scientific name
Use in the Search part
"""
COMMON_TO_SCI = {v.lower(): k for k, v in COMMON_NAMES.items()} # associate the scientific and english common name of my 93 plants.

""" 
Allergen database for 21 key Swiss allergenic species
Each entry contains: pollen season, allergy intensity and main symptoms
"""

ALLERGEN_INFO = {
  "Betula pendula":{"season":"Mar-May","intensity":"High","symptoms":["Rhinitis","Conjunctivitis","Asthma"]},
  "Corylus avellana":{"season":"Jan-Mar","intensity":"High","symptoms":["Rhinitis","Itching","Asthma"]},
  "Alnus glutinosa":{"season":"Feb-Apr","intensity":"Moderate","symptoms":["Rhinitis","Conjunctivitis"]},
  "Fraxinus excelsior":{"season":"Mar-May","intensity":"High","symptoms":["Rhinitis","Conjunctivitis","Asthma"]},
  "Plantago lanceolata":{"season":"May-Aug","intensity":"Moderate","symptoms":["Rhinitis","Conjunctivitis"]},
  "Fagus sylvatica":{"season":"Apr-May","intensity":"Low","symptoms":["Mild Rhinitis"]},
  "Carpinus betulus":{"season":"Mar-May","intensity":"Moderate","symptoms":["Rhinitis","Conjunctivitis"]},
  "Quercus robur":{"season":"Apr-May","intensity":"Moderate","symptoms":["Rhinitis","Conjunctivitis"]},
  "Quercus petraea":{"season":"Apr-May","intensity":"Moderate","symptoms":["Rhinitis"]},
  "Quercus pubescens":{"season":"Apr-May","intensity":"Low","symptoms":["Rhinitis"]},
  "Pinus sylvestris":{"season":"Apr-Jun","intensity":"Low","symptoms":["Mild Rhinitis"]},
  "Tilia cordata":{"season":"Jun-Jul","intensity":"Low","symptoms":["Rhinitis","Conjunctivitis"]},
  "Tilia platyphyllos":{"season":"Jun-Jul","intensity":"Low","symptoms":["Rhinitis"]},
  "Populus tremula":{"season":"Feb-Apr","intensity":"Low","symptoms":["Rhinitis"]},
  "Salix alba":{"season":"Mar-Apr","intensity":"Low","symptoms":["Rhinitis"]},
  "Salix caprea":{"season":"Feb-Apr","intensity":"Low","symptoms":["Rhinitis"]},
  "Sambucus nigra":{"season":"May-Jun","intensity":"Low","symptoms":["Rhinitis"]},
  "Achillea millefolium":{"season":"Jun-Sep","intensity":"Low","symptoms":["Rhinitis","Dermatitis"]},
  "Cirsium arvense":{"season":"Jun-Sep","intensity":"Low","symptoms":["Rhinitis"]},
  "Acer platanoides":{"season":"Apr-May","intensity":"Low","symptoms":["Mild Rhinitis"]},
  "Acer pseudoplatanus":{"season":"Apr-May","intensity":"Low","symptoms":["Mild Rhinitis"]},
} # I selectect those plant because they are major allerge in Switzerland.


# Associates a colored emoji with each allergen intensity level.
INTENSITY_EMOJI = {"High":"🟠","Moderate":"🟡","Low":"🟢"} 



@st.cache_resource(show_spinner=False)
def load_model():
   """
    Load the ONNX model into memory once and cache it for the session.
 
    Uses st.cache_resource so the model is only loaded on the first call  and reused for all subsequent inferences
 
    Returns:
        onnxruntime.InferenceSession: ready-to-use inference session
 
    Dependencies:
        onnxruntime : CPU inference engine (no TensorFlow needed at runtime)
    """
  
    import onnxruntime as ort
    return ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"]) 



def preprocess(img):
  """
  Prepares the image for the model
   Args:
        img (PIL.Image): raw image opened from user upload
 
    Returns:
        numpy.ndarray: shape (1, 300, 300, 3), dtype float32, values in [0,1]
  """

    img = img.convert("RGB").resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0) 




def show_allergen(sci_name): 
"""
Function that associate each plant with there potential allergene, this function happen when one plug allergen plant.
Args:
        sci_name (str): Scientific name of the species e.g. 'Betula pendula'
 
    Returns:
        None (renders directly into the Streamlit UI)
 
    Dependencies:
        ALLERGEN_INFO   : allergen database dict
        INTENSITY_EMOJI : emoji mapping for intensity levels
"""

    info = ALLERGEN_INFO.get(sci_name)
    if info:
        emoji = INTENSITY_EMOJI.get(info["intensity"], "🟡")
        symptoms = ", ".join(info["symptoms"])
        msg = f"{emoji} **Pollen allergen - {info['intensity']}** - Season: {info['season']}\n\nSymptoms: {symptoms}"
      
        # Use warning (orange) for High intensity, info (blue) for Moderate and Low
        if info["intensity"] == "High":
            st.warning(msg)
        else:
            st.info(msg)
    else:
        st.success("No major pollen allergen recorded for this species.")

# The left panel with the BlessYou title and model information.
with st.sidebar: 
    st.title("🌻 BlessYou") 
    st.caption("Plant Identifier")
    st.divider()
    st.caption("MODEL: EfficientNetB3")
    st.caption("SPECIES: 93 Swiss plants")
    st.caption("ACCURACY: Top-1 ~82%")
    st.caption("ACCURACY: Top-5 ~95%")
    st.caption("SOURCE: PlantCLEF + iNaturalist")


# Header -- main title and today's date
col_title, col_meta = st.columns([3, 1])
with col_title: # The main title with today's date and number of species.
    st.title("🌻 BlessYou — Plant Identifier")
    st.caption(f"Identify Swiss plants & check allergen info · {datetime.now().strftime('%A, %d %B %Y')}")
with col_meta:
    st.metric(label="Species", value="93", delta="Swiss Flora")

st.divider()

# Three tabs: photo identification, name search, full species list
tab_photo, tab_search, tab_species = st.tabs(["📷 Identify by Photo", "🔍 Search by Name", "🌿 All Species"])



# TAB 1 -- Identify by Photo
with tab_photo: 
    st.subheader("Identify a Plant") 
  #  creates the upload zone that accepts JPG, PNG and WEBP files.
  # Multiple photos improve accuracy by averaging probabilities across images
   
    uploaded = st.file_uploader(
        "Upload one or more photos of the same plant to improve accuracy",
        type=["jpg","jpeg","png","webp"],
        accept_multiple_files=True 
    )
  
    if uploaded: 
        with st.spinner("Analysing..."):
            try:
                session = load_model()
                all_probs = None
                imgs = []
                for uploaded_file in uploaded:
                    img = Image.open(uploaded_file)
                    imgs.append(img)

                  # Preprocess and run inference on each photo
                    arr = preprocess(img) #reshape photo dimension
                    inp = session.get_inputs()[0].name
                    out = session.get_outputs()[0].name
                    logits = session.run([out], {inp: arr})[0][0]

                   # Softmax: convert raw model outputs (logits) to probabilities
                    e = np.exp(logits - logits.max())
                    probs = e / e.sum() # when there is numerous phots it makes an average to increase accuracy

                  # Accumulate probabilities across all uploaded photos
                    all_probs = probs if all_probs is None else all_probs + probs

                # Average probabilities across all photos
                all_probs /= len(uploaded)

                 # Get top 5 predictions sorted by probability (highest first)
                top5 = all_probs.argsort()[::-1][:5] #sort probability from higher to lower
                names = [CLASS_NAMES[i] for i in top5]
                best = names[0]
                common = COMMON_NAMES.get(best, "Common name unavailable")

                # Display uploaded photos side by side
                cols = st.columns(len(imgs))
                for i, img in enumerate(imgs):
                    with cols[i]:
                        st.image(img, use_container_width=True)

              

               
                st.divider() 

                 # associate plants find in the model with there scientific name, common name and possible allergen.
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric(label="Scientific Name", value=best)
                    st.metric(label="Common Name", value=common)
                with col2:
                    show_allergen(best)

                st.divider() 
              
                # Display 3 alternative predictions as fallback options
                st.subheader("Other Possibilities")
                for n in names[1:4]:
                    c = COMMON_NAMES.get(n, "")
                    info = ALLERGEN_INFO.get(n)
                    allergen_tag = f"- {INTENSITY_EMOJI.get(info['intensity'], '')} {info['intensity']} allergen" if info else "- No known allergen"
                    st.caption(f"🌿 **{n}** ({c}) {allergen_tag}")

            except Exception as ex:
                st.error(f"Error: {ex}")
    else:
        st.info("📷 Upload one or more photos of the same plant to identify it and get allergen information.")


# Table 2: Search by Name
with tab_search: 
    st.subheader("Search by Common Name")
    query = st.text_input("Type a plant common name", placeholder="e.g. Silver Birch, Common Ash, Dog Rose...")
    if query:
        q = query.strip().lower()

        # Try exact match first, then fall back to partial match
        sci_match = COMMON_TO_SCI.get(q)
        matches = [(q, sci_match)] if sci_match else [(k, v) for k, v in COMMON_TO_SCI.items() if q in k]
        if not matches: # if nothing match tells you the plant was not found in data set
            st.warning(f'**"{query}"** was not found in our database of 93 Swiss plant species. Try another name or check the spelling.')
        else: 
          # page that appear when you type a valid plant, Display up to 5 matching results with allergen info
            for common_q, sci in matches[:5]:
                common_display = COMMON_NAMES.get(sci, common_q.title())
                st.subheader(f"🌿 {sci}")
                st.caption(common_display)
                show_allergen(sci)
                st.divider()


# Tabe 3: display all plants in two categories depending on allergenes

with tab_species: 
    st.subheader("All 93 Species in our Database")
    st.caption("Plants compatible with the Photo Identifier")
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Allergenic Species**")
        for sci in CLASS_NAMES:
            if sci in ALLERGEN_INFO:
                info = ALLERGEN_INFO[sci]
                emoji = INTENSITY_EMOJI.get(info["intensity"], "🟢")
                common = COMMON_NAMES.get(sci, "")
                st.caption(f"{emoji} **{sci}** - {common} - {info['season']}")
    with col2:
        st.markdown("**Non-Allergenic Species**")
        for sci in CLASS_NAMES:
            if sci not in ALLERGEN_INFO:
                common = COMMON_NAMES.get(sci, "")
                st.caption(f"✅ **{sci}** - {common}")

# Footer Legal disclaimer at the bottom of the page.
st.divider() 
st.caption("🌻 BlessYou · Plant identification powered by EfficientNetB3 · Not a substitute for professional botanical advice")
