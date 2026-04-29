# ============================================================
# BlessYou — Final Training Notebook
# Datasets: PlantCLEF + iNaturalist (already downloaded)
# Model: EfficientNetB3
# Min photos: 100 | Epochs: 75
# ============================================================

import os, json, shutil
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB3
from tensorflow.keras import layers, Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import TopKCategoricalAccuracy
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

print(f"TensorFlow: {tf.__version__}")
print(f"GPU: {len(tf.config.list_physical_devices('GPU')) > 0}")

# ── Paths ─────────────────────────────────────────────────────
PLANCLEF_PATH  = "/kaggle/input/datasets/datajameson/planclef/training"
INAT_PATH      = "/kaggle/input/notebookf1f2bfe39e/inaturalist_swiss"
COMBINED_PATH  = "/kaggle/working/combined_dataset"
OUTPUT_PATH    = "/kaggle/working"
IMG_SIZE       = 300
BATCH_SIZE     = 32
MIN_PHOTOS     = 100

# ── Species list ──────────────────────────────────────────────
plantes_suisse = [
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

plantes_allergenes = [
    'Betula pendula','Betula pubescens','Corylus avellana',
    'Alnus glutinosa','Alnus incana','Fraxinus excelsior',
    'Dactylis glomerata','Lolium perenne','Lolium multiflorum',
    'Poa pratensis','Poa annua','Festuca rubra',
    'Arrhenatherum elatius','Alopecurus pratensis','Holcus lanatus',
    'Agrostis capillaris','Bromus erectus','Bromus hordeaceus',
    'Deschampsia cespitosa','Anthoxanthum odoratum',
    'Artemisia vulgaris','Quercus robur','Quercus petraea',
    'Quercus pubescens','Fagus sylvatica','Carpinus betulus',
    'Plantago lanceolata','Plantago major','Rumex acetosa',
    'Rumex acetosella','Urtica dioica','Picea abies','Pinus sylvestris',
    'Tilia cordata','Tilia platyphyllos','Solidago canadensis',
    'Achillea millefolium','Matricaria chamomilla',
]

TOUTES_ESPECES = sorted(set(plantes_suisse + plantes_allergenes))

# ═══════════════════════════════════════════════════════════════
# STEP 1: Combine PlantCLEF + iNaturalist
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("STEP 1: Combining PlantCLEF + iNaturalist")
print("="*60)

os.makedirs(COMBINED_PATH, exist_ok=True)
plantes_finales = []

for espece in TOUTES_ESPECES:
    dest = os.path.join(COMBINED_PATH, espece)
    os.makedirs(dest, exist_ok=True)
    count = 0

    # Copy PlantCLEF
    planclef_dir = os.path.join(PLANCLEF_PATH, espece)
    if os.path.exists(planclef_dir):
        for f in os.listdir(planclef_dir):
            shutil.copy2(
                os.path.join(planclef_dir, f),
                os.path.join(dest, f"pc_{f}")
            )
            count += 1

    # Copy iNaturalist
    inat_dir = os.path.join(INAT_PATH, espece)
    if os.path.exists(inat_dir):
        for f in os.listdir(inat_dir):
            shutil.copy2(
                os.path.join(inat_dir, f),
                os.path.join(dest, f)
            )
            count += 1

    if count >= MIN_PHOTOS:
        plantes_finales.append(espece)
        print(f"  ✅ {espece}: {count} photos")
    else:
        print(f"  ❌ {espece}: {count} photos (below {MIN_PHOTOS})")

plantes_finales = sorted(plantes_finales)
print(f"\nFinal species: {len(plantes_finales)}")

with open(f"{OUTPUT_PATH}/class_names.json", "w") as f:
    json.dump(plantes_finales, f, indent=2)
print("class_names.json saved!")

# ═══════════════════════════════════════════════════════════════
# STEP 2: Train EfficientNetB3
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("STEP 2: Training EfficientNetB3")
print("="*60)

datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.15,
    zoom_range=0.25,
    horizontal_flip=True,
    brightness_range=[0.7, 1.3],
    channel_shift_range=20.0,
    fill_mode='nearest'
)

train_data = datagen.flow_from_directory(
    COMBINED_PATH,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    subset='training',
    classes=plantes_finales,
    class_mode='categorical'
)

val_data = datagen.flow_from_directory(
    COMBINED_PATH,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    subset='validation',
    classes=plantes_finales,
    class_mode='categorical'
)

NUM_CLASSES = train_data.num_classes
print(f"Training: {train_data.samples} images")
print(f"Validation: {val_data.samples} images")
print(f"Classes: {NUM_CLASSES}")

base_model = EfficientNetB3(
    weights='imagenet',
    include_top=False,
    input_shape=(IMG_SIZE, IMG_SIZE, 3)
)
base_model.trainable = False

x = base_model.output
x = layers.GlobalAveragePooling2D()(x)
x = layers.BatchNormalization()(x)
x = layers.Dense(512, activation='relu')(x)
x = layers.Dropout(0.4)(x)
x = layers.Dense(256, activation='relu')(x)
x = layers.Dropout(0.3)(x)
output = layers.Dense(NUM_CLASSES, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=output)
print(f"Parameters: {model.count_params():,}")

# Phase 1: Train head
print("\n=== Phase 1: Training head (10 epochs) ===")
model.compile(
    optimizer=Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy', TopKCategoricalAccuracy(k=5, name='top5_acc')]
)
model.fit(train_data, epochs=10, validation_data=val_data)

# Phase 2: Full fine-tuning
print("\n=== Phase 2: Full fine-tuning (75 epochs) ===")
base_model.trainable = True
model.compile(
    optimizer=Adam(learning_rate=0.0001),
    loss='categorical_crossentropy',
    metrics=['accuracy', TopKCategoricalAccuracy(k=5, name='top5_acc')]
)

callbacks = [
    ModelCheckpoint(
        f"{OUTPUT_PATH}/meilleur_modele_b3.h5",
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    ),
    EarlyStopping(
        monitor='val_accuracy',
        patience=15,
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=4,
        min_lr=1e-8,
        verbose=1
    )
]

history = model.fit(
    train_data,
    epochs=75,
    validation_data=val_data,
    callbacks=callbacks
)

print(f"\nBest val_accuracy : {max(history.history['val_accuracy']):.3f}")
print(f"Best val_top5_acc : {max(history.history['val_top5_acc']):.3f}")

# ═══════════════════════════════════════════════════════════════
# STEP 3: Export ONNX
# ═══════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("STEP 3: Exporting to ONNX")
print("="*60)

import subprocess
subprocess.run(["pip", "install", "tf2onnx", "-q"])
import tf2onnx

model_best = tf.keras.models.load_model(
    f"{OUTPUT_PATH}/meilleur_modele_b3.h5",
    custom_objects={"TopKCategoricalAccuracy": TopKCategoricalAccuracy}
)

input_signature = [tf.TensorSpec([1, IMG_SIZE, IMG_SIZE, 3], tf.float32)]
tf2onnx.convert.from_keras(
    model_best,
    input_signature=input_signature,
    output_path=f"{OUTPUT_PATH}/model.onnx"
)

size_mb = os.path.getsize(f"{OUTPUT_PATH}/model.onnx") / 1e6
print(f"\nONNX saved: {size_mb:.1f} MB")
print("\n" + "="*60)
print("DONE! Download from Output tab:")
print("  - model.onnx")
print("  - class_names.json")
print("="*60)
