import streamlit as st # Import necessary libraries
import numpy as np
from PIL import Image
from datetime import datetime

st.set_page_config(page_title="BlessYou - Plant Identifier", page_icon="🌻", layout="wide", initial_sidebar_state="expanded") # configure the page with the title, icon and wide layout.

MODEL_PATH = "model.onnx" # Indicate where to find my model onnx
IMG_SIZE = (300, 300) # resize photos to fit with my model

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

COMMON_TO_SCI = {v.lower(): k for k, v in COMMON_NAMES.items()} # associate the scientific and english common name of my 93 plants.

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

INTENSITY_EMOJI = {"High":"🟠","Moderate":"🟡","Low":"🟢"} # Associates a colored emoji with each allergen intensity level.

@st.cache_resource(show_spinner=False)
def load_model():
    import onnxruntime as ort
    return ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"]) # loads the ONNX model once into memory.

def preprocess(img):
    img = img.convert("RGB").resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0) #  prepares the image for the model aka resize them and normalizes pixels between 0 and 1.

def show_allergen(sci_name): # Function that associate each plant with there potential allergene, this function happen when one plug allergen plant.
    info = ALLERGEN_INFO.get(sci_name)
    if info:
        emoji = INTENSITY_EMOJI.get(info["intensity"], "🟡")
        symptoms = ", ".join(info["symptoms"])
        msg = f"{emoji} **Pollen allergen - {info['intensity']}** - Season: {info['season']}\n\nSymptoms: {symptoms}"
        if info["intensity"] == "High":
            st.warning(msg)
        else:
            st.info(msg)
    else:
        st.success("No major pollen allergen recorded for this species.")

with st.sidebar: # The left panel with the BlessYou title and model information.
    st.title("🌻 BlessYou") 
    st.caption("Plant Identifier")
    st.divider()
    st.caption("MODEL: EfficientNetB3")
    st.caption("SPECIES: 93 Swiss plants")
    st.caption("ACCURACY: Top-1 ~82%")
    st.caption("ACCURACY: Top-1 ~95%")
    st.caption("SOURCE: PlantCLEF + iNaturalist")


col_title, col_meta = st.columns([3, 1])
with col_title: # The main title with today's date and number of species.
    st.title("🌻 BlessYou — Plant Identifier")
    st.caption(f"Identify Swiss plants & check allergen info · {datetime.now().strftime('%A, %d %B %Y')}")
with col_meta:
    st.metric(label="Species", value="93", delta="Swiss Flora")

st.divider()

tab_photo, tab_search, tab_species = st.tabs(["📷 Identify by Photo", "🔍 Search by Name", "🌿 All Species"])

with tab_photo: # part where one put photod
    st.subheader("Identify a Plant") #  creates the upload zone that accepts JPG, PNG and WEBP files.
    uploaded = st.file_uploader(
        "Upload one or more photos of the same plant to improve accuracy",
        type=["jpg","jpeg","png","webp"],
        accept_multiple_files=True # allow to put numerous photos
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
                    arr = preprocess(img) #reshape photo dimension
                    inp = session.get_inputs()[0].name
                    out = session.get_outputs()[0].name
                    logits = session.run([out], {inp: arr})[0][0] # sends the image through the ONNX model and gets back raw numbers.
                    e = np.exp(logits - logits.max())
                    probs = e / e.sum() # when there is numerous phots it makes an average to increase accuracy
                    all_probs = probs if all_probs is None else all_probs + probs
                all_probs /= len(uploaded)
                top5 = all_probs.argsort()[::-1][:5] #sort probability from higher to lower
                names = [CLASS_NAMES[i] for i in top5]
                best = names[0]
                common = COMMON_NAMES.get(best, "Common name unavailable")

                cols = st.columns(len(imgs))
                for i, img in enumerate(imgs):
                    with cols[i]:
                        st.image(img, use_container_width=True)

                st.divider() # associate plants find in the model with there scientific name, common name and possible allergen.
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric(label="Scientific Name", value=best)
                    st.metric(label="Common Name", value=common)
                with col2:
                    show_allergen(best)

                st.divider() # put the other three alternatives
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

with tab_search: # search by name
    st.subheader("Search by Common Name")
    query = st.text_input("Type a plant common name", placeholder="e.g. Silver Birch, Common Ash, Dog Rose...")
    if query:
        q = query.strip().lower()
        sci_match = COMMON_TO_SCI.get(q)
        matches = [(q, sci_match)] if sci_match else [(k, v) for k, v in COMMON_TO_SCI.items() if q in k]
        if not matches: # if nothing match tells you the plant was not found in data set
            st.warning(f'**"{query}"** was not found in our database of 93 Swiss plant species. Try another name or check the spelling.')
        else: # page that appear when you type a valid plant.
            for common_q, sci in matches[:5]:
                common_display = COMMON_NAMES.get(sci, common_q.title())
                st.subheader(f"🌿 {sci}")
                st.caption(common_display)
                show_allergen(sci)
                st.divider()


with tab_species: # display all plant in two category depending on allergenes
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

st.divider() # Footer Legal disclaimer at the bottom of the page.
st.caption("🌻 BlessYou · Plant identification powered by EfficientNetB3 · Not a substitute for professional botanical advice")
