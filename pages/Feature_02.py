<<<<<<< Updated upstream
import streamlit as st
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.metrics import TopKCategoricalAccuracy
import os

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BlessYou · Plant Identifier",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS (même design que app.py) ───────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap');

:root {
    --cream: #F7F3ED;
    --sage: #3D5A3E;
    --sage-light: #6B8F6C;
    --sage-pale: #C8DAC8;
    --ink: #1A1A18;
    --ink-soft: #3A3A36;
    --gold: #B8935A;
    --rust: #C4532A;
    --surface: #EFEBE3;
    --border: rgba(61,90,62,0.15);
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--cream) !important;
    color: var(--ink);
}
.stApp { background: var(--cream) !important; }

[data-testid="stSidebar"] {
    background: #1A1A18 !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] * { color: #C8DAC8 !important; }

.app-header {
    padding: 3rem 0 2rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2.5rem;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
}
.app-logo {
    font-family: 'Playfair Display', serif;
    font-size: 3.5rem;
    font-weight: 700;
    color: var(--ink);
    line-height: 1;
}
.app-logo em { color: var(--sage); font-style: italic; }
.app-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--sage-light);
    margin-bottom: 0.5rem;
}
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    color: var(--ink);
    margin: 2rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
    font-style: italic;
}
.result-card {
    background: var(--surface);
    border-radius: 20px;
    padding: 2rem;
    border: 1px solid var(--border);
    margin-bottom: 1rem;
}
.plant-name {
    font-family: 'Playfair Display', serif;
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--sage);
    font-style: italic;
}
.confidence {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: var(--sage-light);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 0.3rem;
}
.allergen-tag {
    display: inline-block;
    background: #FDF0EC;
    border: 1px solid var(--rust);
    color: #7A2000;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.75rem;
    font-family: 'DM Mono', monospace;
    margin: 3px;
    letter-spacing: 0.05em;
}
.no-allergen-tag {
    display: inline-block;
    background: #EAF3EA;
    border: 1px solid var(--sage);
    color: #1b5e20;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.75rem;
    font-family: 'DM Mono', monospace;
    margin: 3px;
}
.stButton > button {
    background: var(--sage) !important;
    color: white !important;
    border: none !important;
    border-radius: 40px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.5rem !important;
}
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Liste des plantes (même ordre que l'entraînement) ─────────────────────────
PLANTES = [
    "Papaver rhoeas", "Salvia officinalis", "Rumex crispus",
    "Sinapis arvensis", "Dactylorhiza incarnata", "Digitalis grandiflora",
    "Bellis perennis", "Taraxacum officinale", "Trifolium repens",
    "Trifolium pratense", "Ranunculus acris", "Plantago lanceolata",
    "Plantago major", "Urtica dioica", "Sambucus nigra",
    "Rosa canina", "Rubus idaeus", "Rubus fruticosus",
    "Fragaria vesca", "Viola tricolor", "Viola odorata",
    "Primula veris", "Primula vulgaris", "Convolvulus arvensis",
    "Capsella bursa-pastoris", "Stellaria media", "Chenopodium album",
    "Artemisia vulgaris", "Achillea millefolium", "Leucanthemum vulgare",
    "Centaurea jacea", "Centaurea cyanus", "Cirsium arvense",
    "Cirsium vulgare", "Tussilago farfara", "Solidago virgaurea",
    "Hypericum perforatum", "Geranium robertianum", "Geranium pratense",
    "Epilobium angustifolium", "Epilobium hirsutum", "Lythrum salicaria",
    "Lysimachia vulgaris", "Lysimachia nummularia", "Ajuga reptans",
    "Prunella vulgaris", "Lamium album", "Lamium purpureum",
    "Galeopsis tetrahit", "Stachys sylvatica", "Mentha aquatica",
    "Mentha arvensis", "Thymus serpyllum", "Origanum vulgare",
    "Verbascum thapsus", "Verbascum nigrum", "Digitalis purpurea",
    "Linaria vulgaris", "Veronica chamaedrys", "Veronica arvensis",
    "Rhinanthus minor", "Melampyrum pratense", "Euphrasia officinalis",
    "Galium verum", "Galium aparine", "Galium mollugo",
    "Valeriana officinalis", "Knautia arvensis", "Scabiosa columbaria",
    "Dipsacus fullonum", "Campanula rotundifolia", "Campanula patula",
    "Campanula rapunculus", "Jasione montana", "Phyteuma spicatum",
    "Succisa pratensis", "Lotus corniculatus", "Medicago lupulina",
    "Medicago sativa", "Vicia cracca", "Vicia sepium",
    "Lathyrus pratensis", "Lathyrus sylvestris", "Astragalus glycyphyllos",
    "Coronilla varia", "Hippocrepis comosa", "Anthyllis vulneraria",
    "Ononis spinosa", "Ononis repens", "Melilotus officinalis",
    "Melilotus albus", "Genista tinctoria", "Cytisus scoparius",
    "Calluna vulgaris", "Erica carnea", "Vaccinium myrtillus",
    "Vaccinium vitis-idaea", "Vaccinium oxycoccos", "Andromeda polifolia",
    "Oxalis acetosella", "Oxalis stricta", "Geranium molle",
    "Linum catharticum", "Linum usitatissimum", "Euphorbia cyparissias",
    "Euphorbia helioscopia", "Mercurialis perennis", "Mercurialis annua",
    "Polygonum aviculare", "Polygonum persicaria", "Rumex acetosa",
    "Rumex acetosella", "Rumex obtusifolius", "Atriplex patula",
    "Chenopodium bonus-henricus", "Beta vulgaris", "Silene vulgaris",
    "Silene dioica", "Silene latifolia", "Lychnis flos-cuculi",
    "Agrostemma githago", "Dianthus carthusianorum", "Dianthus deltoides",
    "Saponaria officinalis", "Cerastium fontanum", "Cerastium arvense",
    "Arenaria serpyllifolia", "Moehringia trinervia", "Scleranthus annuus",
    "Spergula arvensis", "Sagina procumbens", "Montia fontana",
    "Portulaca oleracea", "Sedum acre", "Sedum album",
    "Sedum telephium", "Sempervivum tectorum", "Saxifraga granulata",
    "Saxifraga aizoides", "Chrysosplenium alternifolium", "Parnassia palustris",
    "Ribes rubrum", "Ribes nigrum", "Ribes uva-crispa",
    "Alchemilla vulgaris", "Potentilla erecta", "Potentilla reptans",
    "Potentilla anserina", "Geum urbanum", "Geum rivale",
    "Filipendula ulmaria", "Filipendula vulgaris", "Spiraea salicifolia",
    "Prunus spinosa", "Prunus avium", "Prunus padus",
    "Sorbus aucuparia", "Sorbus aria", "Crataegus monogyna",
    "Crataegus laevigata", "Malus sylvestris", "Pyrus pyraster",
    "Amelanchier ovalis", "Acer campestre", "Acer pseudoplatanus",
    "Acer platanoides", "Fraxinus excelsior", "Ligustrum vulgare",
    "Syringa vulgaris", "Forsythia suspensa", "Viburnum lantana",
    "Viburnum opulus", "Lonicera periclymenum", "Lonicera xylosteum",
    "Cornus sanguinea", "Cornus mas", "Euonymus europaeus",
    "Rhamnus cathartica", "Frangula alnus", "Ilex aquifolium",
    "Hedera helix", "Clematis vitalba", "Aquilegia vulgaris",
    "Aconitum napellus", "Delphinium consolida", "Nigella arvensis",
    "Helleborus foetidus", "Helleborus niger", "Trollius europaeus",
    "Caltha palustris", "Ranunculus repens", "Ranunculus bulbosus",
    "Ranunculus ficaria", "Anemone nemorosa", "Anemone hepatica",
    "Pulsatilla vulgaris", "Thalictrum flavum", "Thalictrum aquilegiifolium",
    "Berberis vulgaris", "Chelidonium majus", "Fumaria officinalis",
    "Corydalis cava", "Corydalis solida", "Cardamine pratensis",
    "Cardamine hirsuta", "Arabis hirsuta", "Rorippa nasturtium-aquaticum",
    "Alliaria petiolata", "Sisymbrium officinale", "Brassica napus",
    "Raphanus raphanistrum", "Reseda lutea", "Reseda luteola",
    "Drosera rotundifolia", "Drosera anglica", "Nymphaea alba",
    "Nuphar lutea", "Calla palustris", "Arum maculatum",
    "Paris quadrifolia", "Convallaria majalis", "Polygonatum multiflorum",
    "Polygonatum odoratum", "Maianthemum bifolium", "Allium ursinum",
    "Allium oleraceum", "Allium vineale", "Muscari botryoides",
    "Scilla bifolia", "Gagea lutea", "Lilium martagon",
    "Fritillaria meleagris", "Colchicum autumnale", "Veratrum album",
    "Iris pseudacorus", "Iris germanica", "Crocus albiflorus",
    "Orchis mascula", "Orchis militaris", "Gymnadenia conopsea",
    "Platanthera bifolia", "Neottia nidus-avis", "Epipactis helleborine",
    "Cephalanthera damasonium", "Narcissus pseudonarcissus", "Galanthus nivalis",
    "Betula pendula", "Betula pubescens", "Fraxinus ornus",
    "Corylus avellana", "Alnus glutinosa", "Alnus incana",
    "Artemisia absinthium", "Ambrosia artemisiifolia", "Fagus sylvatica",
    "Carpinus betulus", "Quercus robur", "Quercus petraea",
    "Plantago media", "Rumex conglomeratus", "Rumex sanguineus"
]

# ── Base allergènes ────────────────────────────────────────────────────────────
ALLERGENES = {
    "Betula pendula": ["Rhinite allergique", "Asthme", "Conjonctivite"],
    "Betula pubescens": ["Rhinite allergique", "Asthme"],
    "Fraxinus excelsior": ["Rhinite allergique", "Asthme"],
    "Fraxinus ornus": ["Rhinite allergique"],
    "Corylus avellana": ["Rhinite allergique", "Allergie alimentaire croisée"],
    "Alnus glutinosa": ["Rhinite allergique", "Conjonctivite"],
    "Alnus incana": ["Rhinite allergique"],
    "Artemisia vulgaris": ["Rhinite allergique", "Asthme", "Dermatite"],
    "Artemisia absinthium": ["Rhinite allergique", "Dermatite"],
    "Ambrosia artemisiifolia": ["Rhinite allergique sévère", "Asthme", "Conjonctivite"],
    "Fagus sylvatica": ["Rhinite allergique"],
    "Carpinus betulus": ["Rhinite allergique"],
    "Quercus robur": ["Rhinite allergique"],
    "Quercus petraea": ["Rhinite allergique"],
    "Plantago lanceolata": ["Rhinite allergique", "Asthme"],
    "Plantago major": ["Rhinite allergique"],
    "Plantago media": ["Rhinite allergique"],
    "Rumex acetosa": ["Rhinite allergique"],
    "Rumex acetosella": ["Rhinite allergique"],
    "Rumex crispus": ["Rhinite allergique"],
    "Rumex obtusifolius": ["Rhinite allergique"],
    "Rumex conglomeratus": ["Rhinite allergique"],
    "Rumex sanguineus": ["Rhinite allergique"],
    "Urtica dioica": ["Urticaire", "Rhinite allergique"],
    "Taraxacum officinale": ["Rhinite allergique légère"],
    "Achillea millefolium": ["Dermatite de contact", "Rhinite allergique"],
    "Cirsium arvense": ["Rhinite allergique"],
    "Chenopodium album": ["Rhinite allergique"],
    "Mercurialis annua": ["Rhinite allergique"],
    "Mercurialis perennis": ["Rhinite allergique"],
    "Hedera helix": ["Dermatite de contact"],
    "Primula veris": ["Dermatite de contact"],
    "Primula vulgaris": ["Dermatite de contact"],
    "Aconitum napellus": ["Toxique — Ne pas manipuler"],
    "Colchicum autumnale": ["Toxique — Ne pas ingérer"],
    "Digitalis purpurea": ["Toxique — Cardiotoxique"],
    "Digitalis grandiflora": ["Toxique — Cardiotoxique"],
}

# ── Charger le modèle ──────────────────────────────────────────────────────────
@st.cache_resource
def load_plant_model():
    model_path = "meilleur_modele.h5"
    
    # Télécharger depuis Google Drive si pas présent
    if not os.path.exists(model_path):
        import gdown
        url = "https://drive.google.com/uc?id=1ma9N_JzwK75VtrlJhxNL4lVzktd1z4K_"
        with st.spinner("📥 Downloading model..."):
            gdown.download(url, model_path, quiet=False)
    
    model = load_model(model_path, custom_objects={
        "TopKCategoricalAccuracy": TopKCategoricalAccuracy
    })
    return model

# ── Prédiction ────────────────────────────────────────────────────────────────
def predict_plant(image, model):
    img = image.resize((224, 224))
    img_array = np.array(img) / 255.0
    if img_array.shape[-1] == 4:
        img_array = img_array[:, :, :3]
    img_array = np.expand_dims(img_array, axis=0)
    predictions = model.predict(img_array)
    top5_idx = np.argsort(predictions[0])[::-1][:5]
    results = []
    for idx in top5_idx:
        if idx < len(PLANTES):
            results.append({
                "plant": PLANTES[idx],
                "confidence": float(predictions[0][idx]) * 100,
                "allergens": ALLERGENES.get(PLANTES[idx], [])
            })
    return results

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="app-header">
  <div>
    <div class="app-eyebrow">Swiss Plant Identifier · AI-Powered</div>
    <div class="app-logo">Plant<em>ID</em></div>
    <div class="app-sub">Identify Swiss plants & check allergens</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:Playfair Display,serif;font-size:1.4rem;color:white;font-style:italic;">🌿 PlantID</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.7rem;color:#6B8F6C;line-height:2;font-family:DM Mono,monospace;'>
    MODEL · EfficientNetB0<br>
    TRAINED ON · 205 Swiss species<br>
    ACCURACY · ~41% top-1 · ~63% top-5<br>
    DATA · PlantCLEF Dataset
    </div>
    """, unsafe_allow_html=True)

# ── Main ───────────────────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>Upload a plant photo</div>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Choose a photo of a plant",
        type=["jpg", "jpeg", "png"],
        help="Take a clear photo of the plant's leaves, flowers or stem"
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded photo", use_container_width=True)

with col2:
    if uploaded_file:
        st.markdown("<div class='section-title'>Results</div>", unsafe_allow_html=True)

        with st.spinner("🌿 Analysing plant…"):
            try:
                model = load_plant_model()
                results = predict_plant(image, model)

                # Meilleur résultat
                best = results[0]
                allergens = best["allergens"]

                allergen_html = ""
                if allergens:
                    for a in allergens:
                        allergen_html += f'<span class="allergen-tag">⚠️ {a}</span>'
                else:
                    allergen_html = '<span class="no-allergen-tag">✅ No known allergens</span>'

                st.markdown(f"""
                <div class="result-card">
                    <div class="plant-name">{best['plant']}</div>
                    <div class="confidence">Confidence: {best['confidence']:.1f}%</div>
                    <div style="margin-top:1rem">{allergen_html}</div>
                </div>
                """, unsafe_allow_html=True)

                # Top 5
                st.markdown("**Other possibilities:**")
                for r in results[1:]:
                    allergens_str = ", ".join(r["allergens"]) if r["allergens"] else "No known allergens"
                    st.markdown(f"""
                    <div style="background:#F7F3ED;border-radius:12px;padding:0.75rem 1rem;
                                margin-bottom:0.4rem;border:1px solid rgba(61,90,62,0.1);">
                        <span style="font-family:'DM Sans';font-weight:500">{r['plant']}</span>
                        <span style="font-family:'DM Mono',monospace;font-size:0.7rem;
                                     color:#6B8F6C;margin-left:8px">{r['confidence']:.1f}%</span>
                        <div style="font-size:0.75rem;color:#6B8F6C;margin-top:2px">{allergens_str}</div>
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Error loading model: {str(e)}")
    else:
        st.markdown("""
        <div style="background:#EFEBE3;border-radius:20px;padding:3rem;text-align:center;
                    border:2px dashed rgba(61,90,62,0.2);margin-top:1rem;">
            <div style="font-size:3rem">🌿</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.2rem;
                        color:#3D5A3E;font-style:italic;margin-top:1rem;">
                Upload a photo to identify a plant
            </div>
            <div style="font-size:0.8rem;color:#6B8F6C;margin-top:0.5rem;font-family:'DM Mono',monospace;">
                205 Swiss species · Allergen detection
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#6B8F6C;font-size:0.72rem;padding:0.5rem;"
    "font-family:DM Mono,monospace;letter-spacing:0.08em;'>"
    "BLESSYOU · Plant identification powered by EfficientNetB0 · "
    "Not a substitute for professional botanical advice"
    "</div>", unsafe_allow_html=True,
=======
>>>>>>> Stashed changes
#placeholders
