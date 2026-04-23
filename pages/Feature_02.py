import streamlit as st
import numpy as np
from PIL import Image

st.set_page_config(page_title="BlessYou · Plant Identifier", page_icon="🌿", layout="centered")

MODEL_PATH = "model.onnx"
IMG_SIZE = (224, 224)

CLASS_NAMES = ["Abies alba","Acer campestre","Acer platanoides","Acer pseudoplatanus","Achillea millefolium","Aesculus hippocastanum","Agrimonia eupatoria","Agrostis capillaris","Ajuga reptans","Alliaria petiolata","Allium ursinum","Alnus glutinosa","Alnus incana","Alopecurus pratensis","Amelanchier ovalis","Anagallis arvensis","Anemone nemorosa","Angelica sylvestris","Anthriscus sylvestris","Aquilegia vulgaris","Arabidopsis thaliana","Arctium lappa","Arctium minus","Arenaria serpyllifolia","Arnica montana","Arrhenatherum elatius","Artemisia vulgaris","Asplenium ruta-muraria","Asplenium trichomanes","Aster bellidiastrum","Astrantia major","Athyrium filix-femina","Barbarea vulgaris","Bellis perennis","Berberis vulgaris","Betula pendula","Betula pubescens","Brachypodium sylvaticum","Brassica napus","Bromus erectus","Bromus hordeaceus","Bromus sterilis","Bryonia dioica","Buphthalmum salicifolium","Buxus sempervirens","Caltha palustris","Calystegia sepium","Campanula patula","Campanula rotundifolia","Capsella bursa-pastoris","Cardamine amara","Cardamine pratensis","Carduus defloratus","Carduus nutans","Carex acutiformis","Carex flacca","Carex hirta","Carex pendula","Carex sylvatica","Carlina acaulis","Carpinus betulus","Carum carvi","Centaurea jacea","Centaurea scabiosa","Cerastium fontanum","Cerastium glomeratum","Chelidonium majus","Chenopodium album","Cichorium intybus","Cirsium arvense","Cirsium oleraceum","Cirsium palustre","Cirsium vulgare","Clematis vitalba","Clinopodium vulgare","Colchicum autumnale","Convallaria majalis","Convolvulus arvensis","Cornus mas","Cornus sanguinea","Coronilla varia","Corylus avellana","Crataegus laevigata","Crataegus monogyna","Crepis biennis","Cruciata laevipes","Cytisus scoparius","Dactylis glomerata","Daucus carota","Deschampsia cespitosa","Dianthus carthusianorum","Digitalis purpurea","Dipsacus fullonum","Dryopteris carthusiana","Dryopteris filix-mas","Echium vulgare","Epilobium angustifolium","Epilobium hirsutum","Equisetum arvense","Equisetum palustre","Equisetum sylvaticum","Eupatorium cannabinum","Euphorbia amygdaloides","Euphorbia cyparissias","Euphorbia helioscopia","Fagus sylvatica","Fallopia japonica","Festuca rubra","Filipendula ulmaria","Fragaria vesca","Frangula alnus","Fraxinus excelsior","Galium aparine","Galium mollugo","Galium odoratum","Galium verum","Geranium dissectum","Geranium molle","Geranium pratense","Geranium robertianum","Geum rivale","Geum urbanum","Glechoma hederacea","Glyceria fluitans","Gymnocarpium dryopteris","Hedera helix","Heracleum sphondylium","Hieracium lachenalii","Hieracium murorum","Hieracium pilosella","Hieracium sabaudum","Hippocrepis comosa","Holcus lanatus","Holcus mollis","Humulus lupulus","Hypericum maculatum","Hypericum perforatum","Hypochaeris radicata","Impatiens noli-tangere","Impatiens parviflora","Inula conyzae","Juglans regia","Juncus effusus","Juncus inflexus","Juniperus communis","Knautia arvensis","Lamium album","Lamium maculatum","Lamium purpureum","Larix decidua","Lathyrus pratensis","Leontodon hispidus","Leucanthemum vulgare","Ligustrum vulgare","Linaria vulgaris","Lolium multiflorum","Lolium perenne","Lonicera xylosteum","Lotus corniculatus","Luzula pilosa","Luzula sylvatica","Lychnis flos-cuculi","Lysimachia nummularia","Lysimachia vulgaris","Lythrum salicaria","Matricaria chamomilla","Medicago lupulina","Medicago sativa","Melampyrum pratense","Melica uniflora","Mentha aquatica","Molinia caerulea","Mycelis muralis","Myosotis arvensis","Myosotis scorpioides","Narcissus pseudonarcissus","Nardus stricta","Origanum vulgare","Oxalis acetosella","Papaver rhoeas","Paris quadrifolia","Phragmites australis","Picea abies","Picris hieracioides","Pimpinella major","Pimpinella saxifraga","Pinus sylvestris","Plantago lanceolata","Plantago major","Plantago media","Platanthera bifolia","Poa annua","Poa pratensis","Poa trivialis","Polygala vulgaris","Polygonatum multiflorum","Polygonum aviculare","Populus tremula","Potentilla anserina","Potentilla erecta","Potentilla reptans","Primula veris","Prunella vulgaris","Prunus avium","Prunus mahaleb","Prunus padus","Prunus spinosa","Pteridium aquilinum","Pulmonaria officinalis","Quercus petraea","Quercus pubescens","Quercus robur","Ranunculus acris","Ranunculus bulbosus","Ranunculus ficaria","Ranunculus repens","Rhinanthus alectorolophus","Rhinanthus minor","Rosa canina","Rubus fruticosus agg.","Rubus idaeus","Rumex acetosa","Rumex acetosella","Rumex obtusifolius","Salix alba","Salix caprea","Salix cinerea","Sambucus ebulus","Sambucus nigra","Sambucus racemosa","Sanguisorba minor","Sanguisorba officinalis","Saponaria officinalis","Scirpus sylvaticus","Senecio jacobaea","Senecio ovatus","Silene dioica","Silene latifolia","Silene vulgaris","Solidago canadensis","Solidago virgaurea","Sorbus aria","Sorbus aucuparia","Sorbus torminalis","Stachys officinalis","Stachys sylvatica","Stellaria media","Succisa pratensis","Symphytum officinale","Tanacetum vulgare","Taraxacum officinale","Thlaspi arvense","Tilia cordata","Tilia platyphyllos","Torilis japonica","Trifolium medium","Trifolium pratense","Trifolium repens","Urtica dioica","Vaccinium myrtillus","Verbascum thapsus","Veronica chamaedrys","Veronica officinalis","Veronica persica","Viburnum lantana","Viburnum opulus","Vicia cracca","Vicia sepium","Viola arvensis","Viola odorata","Viola tricolor"]

ALLERGEN_INFO = {"Betula pendula":{"season":"mars-mai","intensity":"Forte","symptoms":["rhinite","conjonctivite","asthme"]},"Corylus avellana":{"season":"jan-mars","intensity":"Forte","symptoms":["rhinite","prurit","asthme"]},"Alnus glutinosa":{"season":"fev-avril","intensity":"Moderee","symptoms":["rhinite","conjonctivite"]},"Dactylis glomerata":{"season":"mai-juil","intensity":"Tres forte","symptoms":["rhinite","asthme","urticaire"]},"Lolium perenne":{"season":"mai-aout","intensity":"Forte","symptoms":["rhinite","conjonctivite","asthme"]},"Artemisia vulgaris":{"season":"juil-sept","intensity":"Tres forte","symptoms":["rhinite","asthme"]},"Fraxinus excelsior":{"season":"mars-mai","intensity":"Forte","symptoms":["rhinite","conjonctivite","asthme"]},"Plantago lanceolata":{"season":"mai-aout","intensity":"Moderee","symptoms":["rhinite","conjonctivite"]},"Urtica dioica":{"season":"juin-sept","intensity":"Faible","symptoms":["rhinite","urticaire"]},"Carpinus betulus":{"season":"mars-mai","intensity":"Moderee","symptoms":["rhinite","conjonctivite"]},"Tilia cordata":{"season":"juin-juil","intensity":"Faible","symptoms":["rhinite","conjonctivite"]}}
INTENSITY_COLOR = {"Tres forte":"#8B4A4A","Forte":"#A0622A","Moderee":"#7A8A3A","Faible":"#4A6741"}

@st.cache_resource(show_spinner=False)
def load_model():
    import onnxruntime as ort
    return ort.InferenceSession(MODEL_PATH, providers=["CPUExecutionProvider"])

def preprocess(img):
    img = img.convert("RGB").resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)

st.markdown("<h1 style='font-family:Playfair Display,serif;text-align:center;color:#2D3B2D;padding-top:2rem'>🌿 Plant Identifier</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#6B7F6B;margin-bottom:1.5rem'>205 especes suisses · EfficientNetB0</p>", unsafe_allow_html=True)

uploaded = st.file_uploader("Photo", type=["jpg","jpeg","png","webp"], label_visibility="collapsed")

if uploaded:
    img = Image.open(uploaded)
    col1, col2 = st.columns([1, 1.6], gap="large")
    with col1:
        st.image(img, use_container_width=True)
    with col2:
        with st.spinner("Analyse..."):
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
                scores = [float(probs[i]) for i in top5]
                st.markdown(f"<div style='font-family:Playfair Display,serif;font-size:1.6rem;font-weight:600;color:#2D3B2D'>{names[0]}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='background:#E8EFE8;border-radius:99px;height:6px;margin:4px 0 12px;overflow:hidden'><div style='background:linear-gradient(90deg,#6B9E6B,#4A7A4A);height:100%;width:{scores[0]*100:.0f}%;border-radius:99px'></div></div>", unsafe_allow_html=True)
                st.caption(f"Confiance : **{scores[0]*100:.1f}%**")
                info = ALLERGEN_INFO.get(names[0])
                if info:
                    color = INTENSITY_COLOR.get(info['intensity'], '#4A6741')
                    tags = " ".join(f"<span style='background:#F5E8E8;color:#8B4A4A;padding:0.2rem 0.5rem;border-radius:99px;font-size:0.75rem'>{s}</span>" for s in info['symptoms'])
                    st.markdown(f"<div style='background:#FFF8F0;border-left:3px solid #D4956A;border-radius:0 8px 8px 0;padding:0.8rem 1rem;margin-top:1rem;font-size:0.88rem;color:#6B4A2D'>Allergene · <strong style='color:{color}'>{info['intensity']}</strong><br>{info['season']}<br><div style='margin-top:0.4rem'>{tags}</div></div>", unsafe_allow_html=True)
                else:
                    st.success("Aucun allergene majeur repertorie.")
                st.markdown("**Top 5**")
                for i, (n, s) in enumerate(zip(names, scores), 1):
                    dot = "🟡" if n in ALLERGEN_INFO else "🟢"
                    st.markdown(f"<div style='display:flex;align-items:center;gap:0.8rem;padding:0.5rem 0;border-bottom:1px solid #E8EFE8'><span style='color:#A8C1A8;min-width:1.2rem'>{i}</span><span style='flex:1'>{dot} {n}</span><span style='color:#6B7F6B;font-size:0.8rem'>{s*100:.1f}%</span></div>", unsafe_allow_html=True)
            except Exception as ex:
                st.error(f"Erreur : {ex}")
else:
    st.markdown("<div style='background:#FDFAF4;border:1.5px dashed #A8C1A8;border-radius:16px;padding:2rem;text-align:center;margin:1.5rem 0'><div style='font-size:2.5rem'>📷</div><div style='color:#4A6741;font-size:1.1rem'>Glissez votre photo ici</div><div style='color:#8FAF8F;font-size:0.85rem'>JPG · PNG · WEBP</div></div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<div style='text-align:center;font-size:0.78rem;color:#A8C1A8'>BlessYou · 205 especes suisses · EfficientNetB0</div>", unsafe_allow_html=True)
