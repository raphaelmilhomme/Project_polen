import streamlit as st
import numpy as np
from PIL import Image

st.set_page_config(page_title="BlessYou - Plant Identifier", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")

MODEL_PATH = "model.onnx"
IMG_SIZE = (224, 224)

CLASS_NAMES = ["Abies alba","Acer campestre","Acer platanoides","Acer pseudoplatanus","Achillea millefolium","Aesculus hippocastanum","Agrimonia eupatoria","Agrostis capillaris","Ajuga reptans","Alliaria petiolata","Allium ursinum","Alnus glutinosa","Alnus incana","Alopecurus pratensis","Amelanchier ovalis","Anagallis arvensis","Anemone nemorosa","Angelica sylvestris","Anthriscus sylvestris","Aquilegia vulgaris","Arabidopsis thaliana","Arctium lappa","Arctium minus","Arenaria serpyllifolia","Arnica montana","Arrhenatherum elatius","Artemisia vulgaris","Asplenium ruta-muraria","Asplenium trichomanes","Aster bellidiastrum","Astrantia major","Athyrium filix-femina","Barbarea vulgaris","Bellis perennis","Berberis vulgaris","Betula pendula","Betula pubescens","Brachypodium sylvaticum","Brassica napus","Bromus erectus","Bromus hordeaceus","Bromus sterilis","Bryonia dioica","Buphthalmum salicifolium","Buxus sempervirens","Caltha palustris","Calystegia sepium","Campanula patula","Campanula rotundifolia","Capsella bursa-pastoris","Cardamine amara","Cardamine pratensis","Carduus defloratus","Carduus nutans","Carex acutiformis","Carex flacca","Carex hirta","Carex pendula","Carex sylvatica","Carlina acaulis","Carpinus betulus","Carum carvi","Centaurea jacea","Centaurea scabiosa","Cerastium fontanum","Cerastium glomeratum","Chelidonium majus","Chenopodium album","Cichorium intybus","Cirsium arvense","Cirsium oleraceum","Cirsium palustre","Cirsium vulgare","Clematis vitalba","Clinopodium vulgare","Colchicum autumnale","Convallaria majalis","Convolvulus arvensis","Cornus mas","Cornus sanguinea","Coronilla varia","Corylus avellana","Crataegus laevigata","Crataegus monogyna","Crepis biennis","Cruciata laevipes","Cytisus scoparius","Dactylis glomerata","Daucus carota","Deschampsia cespitosa","Dianthus carthusianorum","Digitalis purpurea","Dipsacus fullonum","Dryopteris carthusiana","Dryopteris filix-mas","Echium vulgare","Epilobium angustifolium","Epilobium hirsutum","Equisetum arvense","Equisetum palustre","Equisetum sylvaticum","Eupatorium cannabinum","Euphorbia amygdaloides","Euphorbia cyparissias","Euphorbia helioscopia","Fagus sylvatica","Fallopia japonica","Festuca rubra","Filipendula ulmaria","Fragaria vesca","Frangula alnus","Fraxinus excelsior","Galium aparine","Galium mollugo","Galium odoratum","Galium verum","Geranium dissectum","Geranium molle","Geranium pratense","Geranium robertianum","Geum rivale","Geum urbanum","Glechoma hederacea","Glyceria fluitans","Gymnocarpium dryopteris","Hedera helix","Heracleum sphondylium","Hieracium lachenalii","Hieracium murorum","Hieracium pilosella","Hieracium sabaudum","Hippocrepis comosa","Holcus lanatus","Holcus mollis","Humulus lupulus","Hypericum maculatum","Hypericum perforatum","Hypochaeris radicata","Impatiens noli-tangere","Impatiens parviflora","Inula conyzae","Juglans regia","Juncus effusus","Juncus inflexus","Juniperus communis","Knautia arvensis","Lamium album","Lamium maculatum","Lamium purpureum","Larix decidua","Lathyrus pratensis","Leontodon hispidus","Leucanthemum vulgare","Ligustrum vulgare","Linaria vulgaris","Lolium multiflorum","Lolium perenne","Lonicera xylosteum","Lotus corniculatus","Luzula pilosa","Luzula sylvatica","Lychnis flos-cuculi","Lysimachia nummularia","Lysimachia vulgaris","Lythrum salicaria","Matricaria chamomilla","Medicago lupulina","Medicago sativa","Melampyrum pratense","Melica uniflora","Mentha aquatica","Molinia caerulea","Mycelis muralis","Myosotis arvensis","Myosotis scorpioides","Narcissus pseudonarcissus","Nardus stricta","Origanum vulgare","Oxalis acetosella","Papaver rhoeas","Paris quadrifolia","Phragmites australis","Picea abies","Picris hieracioides","Pimpinella major","Pimpinella saxifraga","Pinus sylvestris","Plantago lanceolata","Plantago major","Plantago media","Platanthera bifolia","Poa annua","Poa pratensis","Poa trivialis","Polygala vulgaris","Polygonatum multiflorum","Polygonum aviculare","Populus tremula","Potentilla anserina","Potentilla erecta","Potentilla reptans","Primula veris","Prunella vulgaris","Prunus avium","Prunus mahaleb","Prunus padus","Prunus spinosa","Pteridium aquilinum","Pulmonaria officinalis","Quercus petraea","Quercus pubescens","Quercus robur","Ranunculus acris","Ranunculus bulbosus","Ranunculus ficaria","Ranunculus repens","Rhinanthus alectorolophus","Rhinanthus minor","Rosa canina","Rubus fruticosus agg.","Rubus idaeus","Rumex acetosa","Rumex acetosella","Rumex obtusifolius","Salix alba","Salix caprea","Salix cinerea","Sambucus ebulus","Sambucus nigra","Sambucus racemosa","Sanguisorba minor","Sanguisorba officinalis","Saponaria officinalis","Scirpus sylvaticus","Senecio jacobaea","Senecio ovatus","Silene dioica","Silene latifolia","Silene vulgaris","Solidago canadensis","Solidago virgaurea","Sorbus aria","Sorbus aucuparia","Sorbus torminalis","Stachys officinalis","Stachys sylvatica","Stellaria media","Succisa pratensis","Symphytum officinale","Tanacetum vulgare","Taraxacum officinale","Thlaspi arvense","Tilia cordata","Tilia platyphyllos","Torilis japonica","Trifolium medium","Trifolium pratense","Trifolium repens","Urtica dioica","Vaccinium myrtillus","Verbascum thapsus","Veronica chamaedrys","Veronica officinalis","Veronica persica","Viburnum lantana","Viburnum opulus","Vicia cracca","Vicia sepium","Viola arvensis","Viola odorata","Viola tricolor"]

COMMON_NAMES = {"Abies alba":"Silver Fir","Acer campestre":"Field Maple","Acer platanoides":"Norway Maple","Acer pseudoplatanus":"Sycamore","Achillea millefolium":"Yarrow","Aesculus hippocastanum":"Horse Chestnut","Allium ursinum":"Wild Garlic","Alnus glutinosa":"Black Alder","Alnus incana":"Grey Alder","Alopecurus pratensis":"Meadow Foxtail","Amelanchier ovalis":"Snowy Mespilus","Anemone nemorosa":"Wood Anemone","Angelica sylvestris":"Wild Angelica","Anthriscus sylvestris":"Cow Parsley","Aquilegia vulgaris":"Common Columbine","Arctium lappa":"Greater Burdock","Arctium minus":"Lesser Burdock","Arnica montana":"Mountain Arnica","Arrhenatherum elatius":"False Oat Grass","Artemisia vulgaris":"Mugwort","Asplenium ruta-muraria":"Wall Rue","Asplenium trichomanes":"Maidenhair Spleenwort","Astrantia major":"Great Masterwort","Athyrium filix-femina":"Lady Fern","Bellis perennis":"Common Daisy","Berberis vulgaris":"Common Barberry","Betula pendula":"Silver Birch","Betula pubescens":"Downy Birch","Brassica napus":"Rapeseed","Caltha palustris":"Marsh Marigold","Campanula rotundifolia":"Harebell","Capsella bursa-pastoris":"Shepherd Purse","Cardamine pratensis":"Cuckoo Flower","Carlina acaulis":"Stemless Carline Thistle","Carpinus betulus":"Common Hornbeam","Carum carvi":"Caraway","Centaurea jacea":"Brown Knapweed","Chelidonium majus":"Greater Celandine","Cichorium intybus":"Common Chicory","Cirsium arvense":"Creeping Thistle","Cirsium vulgare":"Spear Thistle","Clematis vitalba":"Old Man Beard","Colchicum autumnale":"Autumn Crocus","Convallaria majalis":"Lily of the Valley","Convolvulus arvensis":"Field Bindweed","Cornus mas":"Cornelian Cherry","Cornus sanguinea":"Dogwood","Corylus avellana":"Common Hazel","Crataegus monogyna":"Hawthorn","Dactylis glomerata":"Cocksfoot","Daucus carota":"Wild Carrot","Digitalis purpurea":"Foxglove","Dryopteris filix-mas":"Male Fern","Epilobium angustifolium":"Rosebay Willowherb","Equisetum arvense":"Field Horsetail","Fagus sylvatica":"Common Beech","Fallopia japonica":"Japanese Knotweed","Festuca rubra":"Red Fescue","Filipendula ulmaria":"Meadowsweet","Fragaria vesca":"Wild Strawberry","Fraxinus excelsior":"Common Ash","Galium aparine":"Cleavers","Galium odoratum":"Sweet Woodruff","Galium verum":"Lady Bedstraw","Geranium pratense":"Meadow Cranesbill","Geranium robertianum":"Herb Robert","Geum urbanum":"Wood Avens","Glechoma hederacea":"Ground Ivy","Hedera helix":"Common Ivy","Heracleum sphondylium":"Common Hogweed","Holcus lanatus":"Yorkshire Fog","Humulus lupulus":"Common Hop","Hypericum perforatum":"St Johns Wort","Juglans regia":"Common Walnut","Juniperus communis":"Common Juniper","Knautia arvensis":"Field Scabious","Lamium album":"White Dead Nettle","Larix decidua":"European Larch","Leucanthemum vulgare":"Oxeye Daisy","Lolium multiflorum":"Italian Ryegrass","Lolium perenne":"Perennial Ryegrass","Lotus corniculatus":"Birds Foot Trefoil","Matricaria chamomilla":"Chamomile","Mentha aquatica":"Water Mint","Myosotis scorpioides":"Water Forget Me Not","Narcissus pseudonarcissus":"Wild Daffodil","Origanum vulgare":"Wild Marjoram","Oxalis acetosella":"Wood Sorrel","Papaver rhoeas":"Common Poppy","Phragmites australis":"Common Reed","Picea abies":"Norway Spruce","Pinus sylvestris":"Scots Pine","Plantago lanceolata":"Ribwort Plantain","Plantago major":"Greater Plantain","Poa annua":"Annual Meadow Grass","Poa pratensis":"Smooth Meadow Grass","Populus tremula":"Aspen","Primula veris":"Cowslip","Prunus avium":"Wild Cherry","Prunus spinosa":"Blackthorn","Pteridium aquilinum":"Bracken","Quercus petraea":"Sessile Oak","Quercus pubescens":"Downy Oak","Quercus robur":"Pedunculate Oak","Rosa canina":"Dog Rose","Rubus fruticosus agg.":"Bramble","Rubus idaeus":"Raspberry","Rumex acetosa":"Common Sorrel","Rumex acetosella":"Sheep Sorrel","Salix alba":"White Willow","Salix caprea":"Goat Willow","Sambucus nigra":"Elder","Sambucus racemosa":"Red Elder","Solidago canadensis":"Canadian Goldenrod","Solidago virgaurea":"Goldenrod","Sorbus aucuparia":"Rowan","Tanacetum vulgare":"Tansy","Taraxacum officinale":"Common Dandelion","Tilia cordata":"Small Leaved Lime","Tilia platyphyllos":"Large Leaved Lime","Trifolium pratense":"Red Clover","Trifolium repens":"White Clover","Urtica dioica":"Common Nettle","Vaccinium myrtillus":"Bilberry","Verbascum thapsus":"Great Mullein","Veronica chamaedrys":"Germander Speedwell","Viburnum opulus":"Guelder Rose","Viola odorata":"Sweet Violet","Viola tricolor":"Wild Pansy"}

COMMON_TO_SCI = {v.lower(): k for k, v in COMMON_NAMES.items()}

ALLERGEN_INFO = {"Betula pendula":{"season":"Mar-May","intensity":"High","symptoms":["Rhinitis","Conjunctivitis","Asthma"]},"Betula pubescens":{"season":"Mar-May","intensity":"High","symptoms":["Rhinitis","Conjunctivitis"]},"Corylus avellana":{"season":"Jan-Mar","intensity":"High","symptoms":["Rhinitis","Itching","Asthma"]},"Alnus glutinosa":{"season":"Feb-Apr","intensity":"Moderate","symptoms":["Rhinitis","Conjunctivitis"]},"Alnus incana":{"season":"Feb-Apr","intensity":"Moderate","symptoms":["Rhinitis"]},"Dactylis glomerata":{"season":"May-Jul","intensity":"Very High","symptoms":["Rhinitis","Asthma","Urticaria"]},"Lolium perenne":{"season":"May-Aug","intensity":"High","symptoms":["Rhinitis","Conjunctivitis","Asthma"]},"Lolium multiflorum":{"season":"May-Aug","intensity":"High","symptoms":["Rhinitis","Conjunctivitis"]},"Festuca rubra":{"season":"May-Jul","intensity":"Moderate","symptoms":["Rhinitis"]},"Poa pratensis":{"season":"May-Jul","intensity":"Moderate","symptoms":["Rhinitis","Conjunctivitis"]},"Arrhenatherum elatius":{"season":"May-Jul","intensity":"Moderate","symptoms":["Rhinitis","Conjunctivitis"]},"Artemisia vulgaris":{"season":"Jul-Sep","intensity":"Very High","symptoms":["Rhinitis","Asthma","Anaphylaxis"]},"Quercus robur":{"season":"Apr-May","intensity":"Moderate","symptoms":["Rhinitis","Conjunctivitis"]},"Quercus petraea":{"season":"Apr-May","intensity":"Moderate","symptoms":["Rhinitis"]},"Quercus pubescens":{"season":"Apr-May","intensity":"Low","symptoms":["Rhinitis"]},"Fraxinus excelsior":{"season":"Mar-May","intensity":"High","symptoms":["Rhinitis","Conjunctivitis","Asthma"]},"Plantago lanceolata":{"season":"May-Aug","intensity":"Moderate","symptoms":["Rhinitis","Conjunctivitis"]},"Plantago major":{"season":"May-Aug","intensity":"Low","symptoms":["Rhinitis"]},"Urtica dioica":{"season":"Jun-Sep","intensity":"Low","symptoms":["Rhinitis","Urticaria"]},"Carpinus betulus":{"season":"Mar-May","intensity":"Moderate","symptoms":["Rhinitis","Conjunctivitis"]},"Tilia cordata":{"season":"Jun-Jul","intensity":"Low","symptoms":["Rhinitis","Conjunctivitis"]},"Acer platanoides":{"season":"Apr-May","intensity":"Low","symptoms":["Mild Rhinitis"]},"Acer pseudoplatanus":{"season":"Apr-May","intensity":"Low","symptoms":["Mild Rhinitis"]},"Populus tremula":{"season":"Feb-Apr","intensity":"Low","symptoms":["Rhinitis"]},"Salix alba":{"season":"Mar-Apr","intensity":"Low","symptoms":["Rhinitis"]},"Salix caprea":{"season":"Feb-Apr","intensity":"Low","symptoms":["Rhinitis"]},"Fagus sylvatica":{"season":"Apr-May","intensity":"Low","symptoms":["Mild Rhinitis"]},"Sambucus nigra":{"season":"May-Jun","intensity":"Low","symptoms":["Rhinitis"]},"Solidago canadensis":{"season":"Aug-Oct","intensity":"Moderate","symptoms":["Rhinitis","Conjunctivitis"]},"Achillea millefolium":{"season":"Jun-Sep","intensity":"Low","symptoms":["Rhinitis","Dermatitis"]},"Matricaria chamomilla":{"season":"May-Aug","intensity":"Low","symptoms":["Rhinitis","Dermatitis"]},"Picea abies":{"season":"Apr-Jun","intensity":"Low","symptoms":["Mild Rhinitis"]},"Pinus sylvestris":{"season":"Apr-Jun","intensity":"Low","symptoms":["Mild Rhinitis"]}}

INTENSITY_COLOR = {"Very High":"#C4532A","High":"#B8935A","Moderate":"#3D5A3E","Low":"#6B8F6C"}

@st.cache_resource(show_spinner=False)
def load_model():
    import onnxruntime as ort
    return ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])

def preprocess(img):
    img = img.convert("RGB").resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)

def render_allergen(sci_name):
    info = ALLERGEN_INFO.get(sci_name)
    if info:
        color = INTENSITY_COLOR.get(info["intensity"], "#6B8F6C")
        tags = " ".join(f'<span style="background:#FFF0E0;color:#7A4F00;padding:0.15rem 0.5rem;border-radius:99px;font-size:0.75rem;font-family:DM Mono,monospace">{s}</span>' for s in info["symptoms"])
        return f'<div style="background:#FFF8F0;border-left:3px solid #B8935A;border-radius:0 8px 8px 0;padding:0.8rem 1rem;margin-top:1rem;font-size:0.88rem;color:#6B4A2D">Pollen allergen - <strong style="color:{color}">{info["intensity"]}</strong><br><span style="font-family:DM Mono,monospace;font-size:0.75rem">Season: {info["season"]}</span><div style="margin-top:0.5rem">{tags}</div></div>'
    return '<div style="background:#EAF3EA;border-left:3px solid #3D5A3E;border-radius:0 8px 8px 0;padding:0.8rem 1rem;margin-top:1rem;font-size:0.88rem;color:#1b5e20">No major pollen allergen recorded for this species in our database.</div>'

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap');
:root{--cream:#F7F3ED;--sage:#3D5A3E;--sage-light:#6B8F6C;--ink:#1A1A18;--gold:#B8935A;--surface:#EFEBE3;--surface2:#E8E2D8;--border:rgba(61,90,62,0.15);}
html,body,[class*="css"]{font-family:"DM Sans",sans-serif;background-color:var(--cream)!important;color:var(--ink);}
.stApp{background:var(--cream)!important;}
[data-testid="stSidebar"]{background:#1A1A18!important;}
[data-testid="stSidebar"] *{color:#C8DAC8!important;}
.app-logo{font-family:"Playfair Display",serif;font-size:3.5rem;font-weight:700;color:var(--ink);line-height:1;}
.app-logo em{color:var(--sage);font-style:italic;}
.app-eyebrow{font-family:"DM Mono",monospace;font-size:0.65rem;letter-spacing:0.2em;text-transform:uppercase;color:var(--sage-light);margin-bottom:0.5rem;}
.app-sub{font-size:0.75rem;color:var(--sage-light);letter-spacing:0.12em;text-transform:uppercase;margin-top:0.4rem;}
.section-title{font-family:"Playfair Display",serif;font-size:1.4rem;color:var(--ink);margin:2rem 0 1rem;padding-bottom:0.5rem;border-bottom:1px solid var(--border);font-style:italic;}
.plant-card{background:var(--surface);border-radius:16px;padding:1.5rem 2rem;border:1px solid var(--border);margin-top:1.5rem;}
.plant-name-sci{font-family:"Playfair Display",serif;font-size:1.8rem;font-weight:700;color:var(--ink);font-style:italic;}
.plant-name-common{font-family:"DM Mono",monospace;font-size:0.8rem;letter-spacing:0.12em;text-transform:uppercase;color:var(--sage-light);margin-top:0.2rem;margin-bottom:1rem;}
.alt-row{display:flex;align-items:center;gap:0.8rem;padding:0.6rem 0;border-bottom:1px solid var(--border);}
.alt-sci{font-family:"Playfair Display",serif;font-style:italic;color:var(--ink);flex:1;}
.alt-common{font-family:"DM Mono",monospace;font-size:0.72rem;color:var(--sage-light);}
.upload-zone{background:var(--surface);border:1.5px dashed rgba(61,90,62,0.3);border-radius:20px;padding:3rem;text-align:center;margin-top:1rem;}
.not-found-box{background:var(--surface2);border-left:3px solid #9e9e9e;border-radius:0 8px 8px 0;padding:0.8rem 1rem;margin-top:1rem;font-size:0.88rem;}
footer,#MainMenu,header{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div style="font-family:Playfair Display,serif;font-size:1.4rem;color:white;font-style:italic">Plant Identifier</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div style="font-size:0.7rem;color:#6B8F6C;line-height:2;font-family:DM Mono,monospace">MODEL: EfficientNetB0<br>SPECIES: 205 Swiss plants<br>ACCURACY: Top-5 63%<br>SOURCE: Kaggle Swiss Flora</div>', unsafe_allow_html=True)

st.markdown('<div style="padding:3rem 0 2rem;border-bottom:1px solid rgba(61,90,62,0.15);margin-bottom:2.5rem;display:flex;align-items:flex-end;justify-content:space-between"><div><div class="app-eyebrow">Swiss Flora - Identification and Allergens</div><div class="app-logo">Plant <em>Identifier</em></div><div class="app-sub">205 Swiss species - EfficientNetB0 - Pollen data</div></div><div style="text-align:right"><div style="display:inline-flex;align-items:center;gap:6px;background:#3D5A3E;color:#E8F0E8;padding:8px 16px;border-radius:40px;font-size:0.8rem;font-weight:500;"><div style="width:6px;height:6px;border-radius:50%;background:#C8DAC8;"></div>BlessYou</div></div></div>', unsafe_allow_html=True)

tab_photo, tab_search = st.tabs(["📷 Identify by photo", "🔍 Search by name"])

with tab_photo:
    st.markdown('<div class="section-title">Identify a plant</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Photos", type=["jpg","jpeg","png","webp"], label_visibility="collapsed", accept_multiple_files=True)
    if uploaded:
        uploaded = uploaded if isinstance(uploaded, list) else [uploaded]
        for uploaded_file in uploaded:
            img = Image.open(uploaded_file)
            st.markdown("---")
            col1, col2 = st.columns([1, 1.6], gap="large")
            with col1:
                st.image(img, use_container_width=True)
            with col2:
            with st.spinner("Analysing..."):
                try:
                    session = load_model()
                    arr = preprocess(img)
                    inp = session.get_inputs()[0].name
                    out = session.get_outputs()[0].name
                    logits = session.run([out], {inp: arr})[0][0]
                    e = np.exp(logits - logits.max())
                    probs = e / e.sum()
                    top5 = probs.argsort()[::-1][:5]
                    names = [CLASS_NAMES[i] for i in top5]
                    best = names[0]
                    common = COMMON_NAMES.get(best, "Common name unavailable")
                    st.markdown(f'<div class="plant-card"><div class="plant-name-sci">{best}</div><div class="plant-name-common">{common}</div>{render_allergen(best)}</div>', unsafe_allow_html=True)
                    st.markdown("<div style='margin-top:1.5rem'><strong>Other possibilities</strong></div>", unsafe_allow_html=True)
                    for n in names[1:4]:
                        c = COMMON_NAMES.get(n, "")
                        st.markdown(f'<div class="alt-row"><span class="alt-sci">{n}</span><span class="alt-common">{c}</span></div>', unsafe_allow_html=True)
                except Exception as ex:
                    st.error(f"Error: {ex}")
    else:
        st.markdown('<div class="upload-zone"><div style="font-size:3rem;margin-bottom:0.8rem">📷</div><div style="font-family:Playfair Display,serif;font-size:1.2rem;color:#3D5A3E;font-style:italic">Drop your photo here</div><div style="font-size:0.8rem;color:#6B8F6C;margin-top:0.5rem;font-family:DM Mono,monospace">JPG - PNG - WEBP - any resolution</div></div>', unsafe_allow_html=True)

with tab_search:
    st.markdown('<div class="section-title">Search by common name</div>', unsafe_allow_html=True)
    query = st.text_input("Common name", placeholder="e.g. Silver Birch, Common Nettle, Mugwort...", label_visibility="collapsed")
    if query:
        q = query.strip().lower()
        sci_match = COMMON_TO_SCI.get(q)
        matches = [(q, sci_match)] if sci_match else [(k, v) for k, v in COMMON_TO_SCI.items() if q in k]
        if not matches:
            st.markdown(f'<div class="not-found-box"><strong>"{query}"</strong> was not found in our database. Our database contains 205 Swiss plant species. Try another name or check the spelling.</div>', unsafe_allow_html=True)
        else:
            for common_q, sci in matches[:5]:
                common_display = COMMON_NAMES.get(sci, common_q.title())
                st.markdown(f'<div class="plant-card"><div class="plant-name-sci">{sci}</div><div class="plant-name-common">{common_display}</div>{render_allergen(sci)}</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div style="text-align:center;color:#6B8F6C;font-size:0.72rem;padding:0.5rem;font-family:DM Mono,monospace;letter-spacing:0.08em">BLESSYOU - Plant identification powered by EfficientNetB0 - Not a substitute for professional botanical advice</div>', unsafe_allow_html=True)
