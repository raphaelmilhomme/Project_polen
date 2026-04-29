
# BlessYou — iNaturalist Data Collector
# Downloads up to 200 photos per species from iNaturalist
# Filters by Switzerland (place_id=6753) + research grade
# Save as Kaggle Dataset after running!


import os
import time #  for adding delays between API calls
import requests # to call the iNaturalist API
from pathlib import Path # handle file paths cleanly
from concurrent.futures import ThreadPoolExecutor # download multiple images in parallel.

# Settings 
OUTPUT_DIR   = "/kaggle/working/inaturalist_swiss" # where to save the omage on kaggle
PHOTOS_MAX   = 200   # max photos per species
PLACE_ID     = 6753  # Switzerland
SLEEP        = 0.3   # seconds between API calls (be nice to the API)

# Species list
CLASS_NAMES = [
    'Abies alba','Acer campestre','Acer platanoides','Acer pseudoplatanus',
    'Achillea millefolium','Aesculus hippocastanum','Agrimonia eupatoria',
    'Agrostis capillaris','Ajuga reptans','Alliaria petiolata',
    'Allium ursinum','Alnus glutinosa','Alnus incana','Alopecurus pratensis',
    'Amelanchier ovalis','Anagallis arvensis','Anemone nemorosa',
    'Angelica sylvestris','Anthriscus sylvestris','Aquilegia vulgaris',
    'Arabidopsis thaliana','Arctium lappa','Arctium minus',
    'Arenaria serpyllifolia','Arnica montana','Arrhenatherum elatius',
    'Artemisia vulgaris','Asplenium ruta-muraria','Asplenium trichomanes',
    'Aster bellidiastrum','Astrantia major','Athyrium filix-femina',
    'Barbarea vulgaris','Bellis perennis','Berberis vulgaris',
    'Betula pendula','Betula pubescens','Brachypodium sylvaticum',
    'Brassica napus','Bromus erectus','Bromus hordeaceus','Bromus sterilis',
    'Bryonia dioica','Buphthalmum salicifolium','Buxus sempervirens',
    'Caltha palustris','Calystegia sepium','Campanula patula',
    'Campanula rotundifolia','Capsella bursa-pastoris','Cardamine amara',
    'Cardamine pratensis','Carduus defloratus','Carduus nutans',
    'Carex acutiformis','Carex flacca','Carex hirta','Carex pendula',
    'Carex sylvatica','Carlina acaulis','Carpinus betulus','Carum carvi',
    'Centaurea jacea','Centaurea scabiosa','Cerastium fontanum',
    'Cerastium glomeratum','Chelidonium majus','Chenopodium album',
    'Cichorium intybus','Cirsium arvense','Cirsium oleraceum',
    'Cirsium palustre','Cirsium vulgare','Clematis vitalba',
    'Clinopodium vulgare','Colchicum autumnale','Convallaria majalis',
    'Convolvulus arvensis','Cornus mas','Cornus sanguinea',
    'Coronilla varia','Corylus avellana','Crataegus laevigata',
    'Crataegus monogyna','Crepis biennis','Cruciata laevipes',
    'Cytisus scoparius','Dactylis glomerata','Daucus carota',
    'Deschampsia cespitosa','Dianthus carthusianorum','Digitalis purpurea',
    'Dipsacus fullonum','Dryopteris carthusiana','Dryopteris filix-mas',
    'Echium vulgare','Epilobium angustifolium','Epilobium hirsutum',
    'Equisetum arvense','Equisetum palustre','Equisetum sylvaticum',
    'Eupatorium cannabinum','Euphorbia amygdaloides','Euphorbia cyparissias',
    'Euphorbia helioscopia','Fagus sylvatica','Fallopia japonica',
    'Festuca rubra','Filipendula ulmaria','Fragaria vesca',
    'Frangula alnus','Fraxinus excelsior','Galium aparine',
    'Galium mollugo','Galium odoratum','Galium verum','Geranium dissectum',
    'Geranium molle','Geranium pratense','Geranium robertianum',
    'Geum rivale','Geum urbanum','Glechoma hederacea','Glyceria fluitans',
    'Gymnocarpium dryopteris','Hedera helix','Heracleum sphondylium',
    'Hieracium lachenalii','Hieracium murorum','Hieracium pilosella',
    'Hieracium sabaudum','Hippocrepis comosa','Holcus lanatus',
    'Holcus mollis','Humulus lupulus','Hypericum maculatum',
    'Hypericum perforatum','Hypochaeris radicata','Impatiens noli-tangere',
    'Impatiens parviflora','Inula conyzae','Juglans regia','Juncus effusus',
    'Juncus inflexus','Juniperus communis','Knautia arvensis',
    'Lamium album','Lamium maculatum','Lamium purpureum','Larix decidua',
    'Lathyrus pratensis','Leontodon hispidus','Leucanthemum vulgare',
    'Ligustrum vulgare','Linaria vulgaris','Lolium multiflorum',
    'Lolium perenne','Lonicera xylosteum','Lotus corniculatus',
    'Luzula pilosa','Luzula sylvatica','Lychnis flos-cuculi',
    'Lysimachia nummularia','Lysimachia vulgaris','Lythrum salicaria',
    'Matricaria chamomilla','Medicago lupulina','Medicago sativa',
    'Melampyrum pratense','Melica uniflora','Mentha aquatica',
    'Molinia caerulea','Mycelis muralis','Myosotis arvensis',
    'Myosotis scorpioides','Narcissus pseudonarcissus','Nardus stricta',
    'Origanum vulgare','Oxalis acetosella','Papaver rhoeas',
    'Paris quadrifolia','Phragmites australis','Picea abies',
    'Picris hieracioides','Pimpinella major','Pimpinella saxifraga',
    'Pinus sylvestris','Plantago lanceolata','Plantago major',
    'Plantago media','Platanthera bifolia','Poa annua','Poa pratensis',
    'Poa trivialis','Polygala vulgaris','Polygonatum multiflorum',
    'Polygonum aviculare','Populus tremula','Potentilla anserina',
    'Potentilla erecta','Potentilla reptans','Primula veris',
    'Prunella vulgaris','Prunus avium','Prunus mahaleb','Prunus padus',
    'Prunus spinosa','Pteridium aquilinum','Pulmonaria officinalis',
    'Quercus petraea','Quercus pubescens','Quercus robur','Ranunculus acris',
    'Ranunculus bulbosus','Ranunculus ficaria','Ranunculus repens',
    'Rhinanthus alectorolophus','Rhinanthus minor','Rosa canina',
    'Rubus fruticosus agg.','Rubus idaeus','Rumex acetosa',
    'Rumex acetosella','Rumex obtusifolius','Salix alba','Salix caprea',
    'Salix cinerea','Sambucus ebulus','Sambucus nigra','Sambucus racemosa',
    'Sanguisorba minor','Sanguisorba officinalis','Saponaria officinalis',
    'Scirpus sylvaticus','Senecio jacobaea','Senecio ovatus',
    'Silene dioica','Silene latifolia','Silene vulgaris','Solidago canadensis',
    'Solidago virgaurea','Sorbus aria','Sorbus aucuparia','Sorbus torminalis',
    'Stachys officinalis','Stachys sylvatica','Stellaria media',
    'Succisa pratensis','Symphytum officinale','Tanacetum vulgare',
    'Taraxacum officinale','Thlaspi arvense','Tilia cordata',
    'Tilia platyphyllos','Torilis japonica','Trifolium medium',
    'Trifolium pratense','Trifolium repens','Urtica dioica',
    'Vaccinium myrtillus','Verbascum thapsus','Veronica chamaedrys',
    'Veronica officinalis','Veronica persica','Viburnum lantana',
    'Viburnum opulus','Vicia cracca','Vicia sepium','Viola arvensis',
    'Viola odorata','Viola tricolor',
]

# Helper functions, Calls the iNaturalist API to get photo URLs for one species.
def get_photo_urls(taxon_name, max_photos=200, place_id=6753):
    urls = []
    page = 1
    per_page = 50 # 50 at a time until it has enough URLs. 
  

    while len(urls) < max_photos:
        try:
            r = requests.get(
                "https://api.inaturalist.org/v1/observations",
                params={
                    "taxon_name": taxon_name,
                    "place_id": place_id,
                    "quality_grade": "research",
                    "photos": True,
                    "per_page": per_page,
                    "page": page,
                    "order": "desc",
                    "order_by": "created_at",
                },
                timeout=15 # sends a request with the species name, the Switzerland place ID, and filters only research grade observations that have photos
            )
            data = r.json()
            results = data.get("results", [])
            if not results:
                break

            for obs in results:
                photos = obs.get("photos", [])
                for photo in photos:
                    url = photo.get("url", "")
                    if url:
                        # Get medium size instead of square thumbnail
                        url = url.replace("square", "medium") # Each photo URL is modified from square (thumbnail) to medium size for better quality.
                        urls.append(url)
                        if len(urls) >= max_photos:
                            break
                if len(urls) >= max_photos:
                    break

            # Check if there are more pages
            total = data.get("total_results", 0)
            if page * per_page >= total:
                break
            page += 1
            time.sleep(SLEEP)

        except Exception as e:
            print(f"  API error for {taxon_name}: {e}")
            break

    return urls


def download_image(args): # Downloads a single image from a URL and saves it as a .jpg
    """Download a single image."""
    url, filepath = args
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(r.content)
            return True
    except Exception:
        pass
    return False


def collect_species(taxon_name, output_dir, max_photos=200): #Manages the full collection for one species
    """Collect photos for one species."""
    # Create folder 
    folder_name = taxon_name.replace(" ", "_").replace(".", "")
    species_dir = Path(output_dir) / taxon_name
    species_dir.mkdir(parents=True, exist_ok=True)

    # Skip if already enough photos
    existing = list(species_dir.glob("*.jpg"))
    if len(existing) >= max_photos:
        print(f"  SKIP {taxon_name}: {len(existing)} photos already")
        return len(existing)

    needed = max_photos - len(existing)

    # Get URLs
    urls = get_photo_urls(taxon_name, max_photos=needed + 20)
    if not urls:
        print(f"  NO PHOTOS found for {taxon_name}")
        return 0

    # Prepare download tasks
    tasks = []
    for i, url in enumerate(urls[:needed]):
        filepath = species_dir / f"inat_{i:04d}.jpg"
        if not filepath.exists():
            tasks.append((url, str(filepath)))

    # Download in parallel
    downloaded = 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(download_image, tasks))
        downloaded = sum(results)

    total = len(existing) + downloaded
    print(f"  {taxon_name}: {downloaded} downloaded → {total} total")
    return total



os.makedirs(OUTPUT_DIR, exist_ok=True)

summary = {}
for i, taxon in enumerate(CLASS_NAMES):
    print(f"[{i+1}/{len(CLASS_NAMES)}] {taxon}")
    count = collect_species(taxon, OUTPUT_DIR, PHOTOS_MAX)
    summary[taxon] = count
    time.sleep(SLEEP)

