import streamlit as st
import numpy as np
from PIL import Image
from datetime import datetime

st.set_page_config(page_title='BlessYou - Plant Identifier', page_icon='🌻', layout='wide', initial_sidebar_state='expanded')

MODEL_PATH = 'model.onnx'
IMG_SIZE = (224, 224)

CLASS_NAMES = ['Abies alba','Acer campestre','Acer platanoides','Acer pseudoplatanus','Achillea millefolium','Aesculus hippocastanum','Agrimonia eupatoria','Agrostis capillaris','Ajuga reptans','Alliaria petiolata','Allium ursinum','Alnus glutinosa','Alnus incana','Alopecurus pratensis','Amelanchier ovalis','Anagallis arvensis','Anemone nemorosa','Angelica sylvestris','Anthriscus sylvestris','Aquilegia vulgaris','Arabidopsis thaliana','Arctium lappa','Arctium minus','Arenaria serpyllifolia','Arnica montana','Arrhenatherum elatius','Artemisia vulgaris','Asplenium ruta-muraria','Asplenium trichomanes','Aster bellidiastrum','Astrantia major','Athyrium filix-femina','Barbarea vulgaris','Bellis perennis','Berberis vulgaris','Betula pendula','Betula pubescens','Brachypodium sylvaticum','Brassica napus','Bromus erectus','Bromus hordeaceus','Bromus sterilis','Bryonia dioica','Buphthalmum salicifolium','Buxus sempervirens','Caltha palustris','Calystegia sepium','Campanula patula','Campanula rotundifolia','Capsella bursa-pastoris','Cardamine amara','Cardamine pratensis','Carduus defloratus','Carduus nutans','Carex acutiformis','Carex flacca','Carex hirta','Carex pendula','Carex sylvatica','Carlina acaulis','Carpinus betulus','Carum carvi','Centaurea jacea','Centaurea scabiosa','Cerastium fontanum','Cerastium glomeratum','Chelidonium majus','Chenopodium album','Cichorium intybus','Cirsium arvense','Cirsium oleraceum','Cirsium palustre','Cirsium vulgare','Clematis vitalba','Clinopodium vulgare','Colchicum autumnale','Convallaria majalis','Convolvulus arvensis','Cornus mas','Cornus sanguinea','Coronilla varia','Corylus avellana','Crataegus laevigata','Crataegus monogyna','Crepis biennis','Cruciata laevipes','Cytisus scoparius','Dactylis glomerata','Daucus carota','Deschampsia cespitosa','Dianthus carthusianorum','Digitalis purpurea','Dipsacus fullonum','Dryopteris carthusiana','Dryopteris filix-mas','Echium vulgare','Epilobium angustifolium','Epilobium hirsutum','Equisetum arvense','Equisetum palustre','Equisetum sylvaticum','Eupatorium cannabinum','Euphorbia amygdaloides','Euphorbia cyparissias','Euphorbia helioscopia','Fagus sylvatica','Fallopia japonica','Festuca rubra','Filipendula ulmaria','Fragaria vesca','Frangula alnus','Fraxinus excelsior','Galium aparine','Galium mollugo','Galium odoratum','Galium verum','Geranium dissectum','Geranium molle','Geranium pratense','Geranium robertianum','Geum rivale','Geum urbanum','Glechoma hederacea','Glyceria fluitans','Gymnocarpium dryopteris','Hedera helix','Heracleum sphondylium','Hieracium lachenalii','Hieracium murorum','Hieracium pilosella','Hieracium sabaudum','Hippocrepis comosa','Holcus lanatus','Holcus mollis','Humulus lupulus','Hypericum maculatum','Hypericum perforatum','Hypochaeris radicata','Impatiens noli-tangere','Impatiens parviflora','Inula conyzae','Juglans regia','Juncus effusus','Juncus inflexus','Juniperus communis','Knautia arvensis','Lamium album','Lamium maculatum','Lamium purpureum','Larix decidua','Lathyrus pratensis','Leontodon hispidus','Leucanthemum vulgare','Ligustrum vulgare','Linaria vulgaris','Lolium multiflorum','Lolium perenne','Lonicera xylosteum','Lotus corniculatus','Luzula pilosa','Luzula sylvatica','Lychnis flos-cuculi','Lysimachia nummularia','Lysimachia vulgaris','Lythrum salicaria','Matricaria chamomilla','Medicago lupulina','Medicago sativa','Melampyrum pratense','Melica uniflora','Mentha aquatica','Molinia caerulea','Mycelis muralis','Myosotis arvensis','Myosotis scorpioides','Narcissus pseudonarcissus','Nardus stricta','Origanum vulgare','Oxalis acetosella','Papaver rhoeas','Paris quadrifolia','Phragmites australis','Picea abies','Picris hieracioides','Pimpinella major','Pimpinella saxifraga','Pinus sylvestris','Plantago lanceolata','Plantago major','Plantago media','Platanthera bifolia','Poa annua','Poa pratensis','Poa trivialis','Polygala vulgaris','Polygonatum multiflorum','Polygonum aviculare','Populus tremula','Potentilla anserina','Potentilla erecta','Potentilla reptans','Primula veris','Prunella vulgaris','Prunus avium','Prunus mahaleb','Prunus padus','Prunus spinosa','Pteridium aquilinum','Pulmonaria officinalis','Quercus petraea','Quercus pubescens','Quercus robur','Ranunculus acris','Ranunculus bulbosus','Ranunculus ficaria','Ranunculus repens','Rhinanthus alectorolophus','Rhinanthus minor','Rosa canina','Rubus fruticosus agg.','Rubus idaeus','Rumex acetosa','Rumex acetosella','Rumex obtusifolius','Salix alba','Salix caprea','Salix cinerea','Sambucus ebulus','Sambucus nigra','Sambucus racemosa','Sanguisorba minor','Sanguisorba officinalis','Saponaria officinalis','Scirpus sylvaticus','Senecio jacobaea','Senecio ovatus','Silene dioica','Silene latifolia','Silene vulgaris','Solidago canadensis','Solidago virgaurea','Sorbus aria','Sorbus aucuparia','Sorbus torminalis','Stachys officinalis','Stachys sylvatica','Stellaria media','Succisa pratensis','Symphytum officinale','Tanacetum vulgare','Taraxacum officinale','Thlaspi arvense','Tilia cordata','Tilia platyphyllos','Torilis japonica','Trifolium medium','Trifolium pratense','Trifolium repens','Urtica dioica','Vaccinium myrtillus','Verbascum thapsus','Veronica chamaedrys','Veronica officinalis','Veronica persica','Viburnum lantana','Viburnum opulus','Vicia cracca','Vicia sepium','Viola arvensis','Viola odorata','Viola tricolor']

COMMON_NAMES = {'Abies alba':'Silver Fir','Acer campestre':'Field Maple','Acer platanoides':'Norway Maple','Acer pseudoplatanus':'Sycamore','Achillea millefolium':'Yarrow','Aesculus hippocastanum':'Horse Chestnut','Allium ursinum':'Wild Garlic','Alnus glutinosa':'Black Alder','Alnus incana':'Grey Alder','Artemisia vulgaris':'Mugwort','Bellis perennis':'Common Daisy','Betula pendula':'Silver Birch','Betula pubescens':'Downy Birch','Brassica napus':'Rapeseed','Carpinus betulus':'Common Hornbeam','Cirsium arvense':'Creeping Thistle','Cirsium vulgare':'Spear Thistle','Clematis vitalba':'Old Man Beard','Convallaria majalis':'Lily of the Valley','Corylus avellana':'Common Hazel','Dactylis glomerata':'Cocksfoot','Daucus carota':'Wild Carrot','Digitalis purpurea':'Foxglove','Dryopteris filix-mas':'Male Fern','Epilobium angustifolium':'Rosebay Willowherb','Fagus sylvatica':'Common Beech','Fallopia japonica':'Japanese Knotweed','Festuca rubra':'Red Fescue','Filipendula ulmaria':'Meadowsweet','Fragaria vesca':'Wild Strawberry','Fraxinus excelsior':'Common Ash','Galium aparine':'Cleavers','Galium verum':'Lady Bedstraw','Geranium pratense':'Meadow Cranesbill','Geranium robertianum':'Herb Robert','Geum urbanum':'Wood Avens','Hedera helix':'Common Ivy','Heracleum sphondylium':'Common Hogweed','Holcus lanatus':'Yorkshire Fog','Hypericum perforatum':'St Johns Wort','Juglans regia':'Common Walnut','Juniperus communis':'Common Juniper','Knautia arvensis':'Field Scabious','Lamium album':'White Dead Nettle','Larix decidua':'European Larch','Leucanthemum vulgare':'Oxeye Daisy','Lolium multiflorum':'Italian Ryegrass','Lolium perenne':'Perennial Ryegrass','Lotus corniculatus':'Birds Foot Trefoil','Matricaria chamomilla':'Chamomile','Origanum vulgare':'Wild Marjoram','Oxalis acetosella':'Wood Sorrel','Papaver rhoeas':'Common Poppy','Picea abies':'Norway Spruce','Pinus sylvestris':'Scots Pine','Plantago lanceolata':'Ribwort Plantain','Plantago major':'Greater Plantain','Poa annua':'Annual Meadow Grass','Poa pratensis':'Smooth Meadow Grass','Populus tremula':'Aspen','Primula veris':'Cowslip','Prunus avium':'Wild Cherry','Prunus spinosa':'Blackthorn','Pteridium aquilinum':'Bracken','Quercus petraea':'Sessile Oak','Quercus pubescens':'Downy Oak','Quercus robur':'Pedunculate Oak','Rosa canina':'Dog Rose','Rubus idaeus':'Raspberry','Rumex acetosa':'Common Sorrel','Salix alba':'White Willow','Salix caprea':'Goat Willow','Sambucus nigra':'Elder','Solidago canadensis':'Canadian Goldenrod','Sorbus aucuparia':'Rowan','Taraxacum officinale':'Common Dandelion','Tilia cordata':'Small Leaved Lime','Tilia platyphyllos':'Large Leaved Lime','Trifolium pratense':'Red Clover','Trifolium repens':'White Clover','Urtica dioica':'Common Nettle','Vaccinium myrtillus':'Bilberry','Viola odorata':'Sweet Violet','Viola tricolor':'Wild Pansy'}
COMMON_TO_SCI = {v.lower(): k for k, v in COMMON_NAMES.items()}

ALLERGEN_INFO = {'Betula pendula':{'season':'Mar-May','intensity':'High','symptoms':['Rhinitis','Conjunctivitis','Asthma']},'Betula pubescens':{'season':'Mar-May','intensity':'High','symptoms':['Rhinitis','Conjunctivitis']},'Corylus avellana':{'season':'Jan-Mar','intensity':'High','symptoms':['Rhinitis','Itching','Asthma']},'Alnus glutinosa':{'season':'Feb-Apr','intensity':'Moderate','symptoms':['Rhinitis','Conjunctivitis']},'Alnus incana':{'season':'Feb-Apr','intensity':'Moderate','symptoms':['Rhinitis']},'Dactylis glomerata':{'season':'May-Jul','intensity':'Very High','symptoms':['Rhinitis','Asthma','Urticaria']},'Lolium perenne':{'season':'May-Aug','intensity':'High','symptoms':['Rhinitis','Conjunctivitis','Asthma']},'Lolium multiflorum':{'season':'May-Aug','intensity':'High','symptoms':['Rhinitis','Conjunctivitis']},'Festuca rubra':{'season':'May-Jul','intensity':'Moderate','symptoms':['Rhinitis']},'Poa pratensis':{'season':'May-Jul','intensity':'Moderate','symptoms':['Rhinitis','Conjunctivitis']},'Arrhenatherum elatius':{'season':'May-Jul','intensity':'Moderate','symptoms':['Rhinitis','Conjunctivitis']},'Artemisia vulgaris':{'season':'Jul-Sep','intensity':'Very High','symptoms':['Rhinitis','Asthma','Anaphylaxis']},'Quercus robur':{'season':'Apr-May','intensity':'Moderate','symptoms':['Rhinitis','Conjunctivitis']},'Fraxinus excelsior':{'season':'Mar-May','intensity':'High','symptoms':['Rhinitis','Conjunctivitis','Asthma']},'Plantago lanceolata':{'season':'May-Aug','intensity':'Moderate','symptoms':['Rhinitis','Conjunctivitis']},'Urtica dioica':{'season':'Jun-Sep','intensity':'Low','symptoms':['Rhinitis','Urticaria']},'Carpinus betulus':{'season':'Mar-May','intensity':'Moderate','symptoms':['Rhinitis','Conjunctivitis']},'Tilia cordata':{'season':'Jun-Jul','intensity':'Low','symptoms':['Rhinitis','Conjunctivitis']},'Fagus sylvatica':{'season':'Apr-May','intensity':'Low','symptoms':['Mild Rhinitis']},'Sambucus nigra':{'season':'May-Jun','intensity':'Low','symptoms':['Rhinitis']},'Solidago canadensis':{'season':'Aug-Oct','intensity':'Moderate','symptoms':['Rhinitis','Conjunctivitis']},'Matricaria chamomilla':{'season':'May-Aug','intensity':'Low','symptoms':['Rhinitis','Dermatitis']},'Picea abies':{'season':'Apr-Jun','intensity':'Low','symptoms':['Mild Rhinitis']},'Pinus sylvestris':{'season':'Apr-Jun','intensity':'Low','symptoms':['Mild Rhinitis']}}
INTENSITY_EMOJI = {'Very High':'🔴','High':'🟠','Moderate':'🟡','Low':'🟢'}

@st.cache_resource(show_spinner=False)
def load_model():
    import onnxruntime as ort
    return ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])

def preprocess(img):
    img = img.convert('RGB').resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)

def show_allergen(sci_name):
    info = ALLERGEN_INFO.get(sci_name)
    if info:
        emoji = INTENSITY_EMOJI.get(info['intensity'], '🟡')
        symptoms = ', '.join(info['symptoms'])
        msg = f"{emoji} **Pollen allergen - {info['intensity']}** - Season: {info['season']}\n\nSymptoms: {symptoms}"
        if info['intensity'] == 'Very High':
            st.error(msg)
        elif info['intensity'] == 'High':
            st.warning(msg)
        else:
            st.info(msg)
    else:
        st.success('No major pollen allergen recorded for this species.')

with st.sidebar:
    st.title('🌻 BlessYou')
    st.caption('Plant Identifier')
    st.divider()
    st.caption('MODEL: EfficientNetB0')
    st.caption('SPECIES: 205 Swiss plants')
    st.caption('ACCURACY: Top-5 63%')
    st.caption('SOURCE: Kaggle Swiss Flora')

col_title, col_meta = st.columns([3, 1])
with col_title:
    st.title('🌻 BlessYou - Plant Identifier')
    st.caption(f"Identify Swiss plants and check allergen info - {datetime.now().strftime('%A, %d %B %Y')}")
with col_meta:
    st.metric(label='Species', value='205', delta='Swiss Flora')

st.divider()

tab_photo, tab_search = st.tabs(['📷 Identify by Photo', '🔍 Search by Name'])

with tab_photo:
    st.subheader('Identify a Plant')
    uploaded = st.file_uploader('Upload one or more photos of the same plant to improve accuracy', type=['jpg','jpeg','png','webp'], accept_multiple_files=True)
    if uploaded:
        with st.spinner('Analysing...'):
            try:
                session = load_model()
                all_probs = None
                imgs = []
                for uploaded_file in uploaded:
                    img = Image.open(uploaded_file)
                    imgs.append(img)
                    arr = preprocess(img)
                    inp = session.get_inputs()[0].name
                    out = session.get_outputs()[0].name
                    logits = session.run([out], {inp: arr})[0][0]
                    e = np.exp(logits - logits.max())
                    probs = e / e.sum()
                    all_probs = probs if all_probs is None else all_probs + probs
                all_probs /= len(uploaded)
                top5 = all_probs.argsort()[::-1][:5]
                names = [CLASS_NAMES[i] for i in top5]
                best = names[0]
                common = COMMON_NAMES.get(best, 'Common name unavailable')
                cols = st.columns(len(imgs))
                for i, img in enumerate(imgs):
                    with cols[i]:
                        st.image(img, use_container_width=True)
                st.divider()
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric(label='Scientific Name', value=best)
                    st.metric(label='Common Name', value=common)
                with col2:
                    show_allergen(best)
                st.divider()
                st.subheader('Other Possibilities')
                for n in names[1:4]:
                    c = COMMON_NAMES.get(n, '')
                    info = ALLERGEN_INFO.get(n)
                    allergen_tag = f"- {INTENSITY_EMOJI.get(info['intensity'], '')} {info['intensity']} allergen" if info else '- No known allergen'
                    st.caption(f"🌿 **{n}** ({c}) {allergen_tag}")
            except Exception as ex:
                st.error(f'Error: {ex}')
    else:
        st.info('📷 Upload one or more photos of the same plant to identify it and get allergen information.')

with tab_search:
    st.subheader('Search by Common Name')
    query = st.text_input('Type a plant common name', placeholder='e.g. Silver Birch, Common Nettle, Mugwort...')
    if query:
        q = query.strip().lower()
        sci_match = COMMON_TO_SCI.get(q)
        matches = [(q, sci_match)] if sci_match else [(k, v) for k, v in COMMON_TO_SCI.items() if q in k]
        if not matches:
            st.warning(f'**{query}** was not found in our database of 205 Swiss plant species. Try another name or check the spelling.')
        else:
            for common_q, sci in matches[:5]:
                common_display = COMMON_NAMES.get(sci, common_q.title())
                st.subheader(f'🌿 {sci}')
                st.caption(common_display)
                show_allergen(sci)
                st.divider()

st.divider()
st.caption('🌻 BlessYou - Plant identification powered by EfficientNetB0 - Not a substitute for professional botanical advice')