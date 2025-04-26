import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# Sample training data (replace with real disease names and solutions)
data = [
    # Fungal Diseases
    ("Powdery Mildew", 
     "Symptoms: White or gray powdery growth on leaves, stems, and buds. Leaves may curl and become distorted. "
     "Causes: Caused by fungal spores thriving in warm, dry conditions with poor air circulation. "
     "Prevention: Space plants properly, ensure good air circulation, and avoid overhead watering. "
     "Treatment: Use sulfur-based fungicides, neem oil, or potassium bicarbonate. Remove infected plant parts."),

    ("Leaf Spot", 
     "Symptoms: Brown, black, or tan spots on leaves, often with yellow halos. Severe infection leads to leaf drop. "
     "Causes: Caused by fungal pathogens (Alternaria, Cercospora) or bacteria (Xanthomonas) in humid environments. "
     "Prevention: Avoid overhead watering and remove infected leaves. Ensure good airflow. "
     "Treatment: Apply copper-based fungicides, organic fungicides, or a baking soda solution."),

    ("Root Rot", 
     "Symptoms: Yellowing leaves, stunted growth, and mushy, dark roots with a foul smell. "
     "Causes: Overwatering and poor soil drainage, leading to fungal infections (Phytophthora, Pythium). "
     "Prevention: Use well-draining soil and avoid overwatering. Ensure proper aeration. "
     "Treatment: Remove affected plants, treat with fungicides like metalaxyl, and improve drainage."),

    ("Blight", 
     "Symptoms: Rapid wilting, browning, and rotting of stems, leaves, and fruits. Can lead to plant death. "
     "Causes: Bacterial (Erwinia) or fungal (Phytophthora) pathogens thrive in warm, wet conditions. "
     "Prevention: Rotate crops, use resistant varieties, and avoid overhead watering. "
     "Treatment: Apply fungicides containing chlorothalonil or copper sulfate. Remove infected plants."),

    ("Rust", 
     "Symptoms: Small, orange, or brown pustules on the undersides of leaves, leading to defoliation. "
     "Causes: Fungal spores spread by wind and water. High humidity promotes infection. "
     "Prevention: Plant resistant varieties, prune excess foliage, and maintain proper plant spacing. "
     "Treatment: Apply sulfur or copper-based fungicides. Remove infected leaves to reduce spread."),

    # Bacterial Diseases
    ("Bacterial Wilt", 
     "Symptoms: Sudden wilting of leaves and stems. Affected stems may ooze a sticky, milky substance. "
     "Causes: Caused by soilborne bacteria (Ralstonia solanacearum) transmitted through infected soil or insects. "
     "Prevention: Practice crop rotation, use disease-resistant varieties, and control insect vectors. "
     "Treatment: Remove and destroy infected plants. Apply beneficial soil bacteria to suppress disease."),

    ("Fire Blight", 
     "Symptoms: Blackened, withered branches, flowers, and fruit resembling scorched tissue. "
     "Causes: Caused by the bacterium Erwinia amylovora, spread by insects, rain, and pruning tools. "
     "Prevention: Avoid excessive nitrogen fertilization, prune in dry weather, and sterilize tools. "
     "Treatment: Prune infected branches at least 12 inches below the affected area. Apply copper sprays."),

    ("Bacterial Leaf Streak", 
     "Symptoms: Water-soaked streaks on leaves that turn brown and necrotic, often with yellow halos. "
     "Causes: Caused by Xanthomonas bacteria spread by rain, irrigation, or contaminated tools. "
     "Prevention: Rotate crops, avoid working with wet plants, and use drip irrigation. "
     "Treatment: Apply copper-based bactericides and remove infected plant material."),

    # Viral Diseases
    ("Mosaic Virus", 
     "Symptoms: Mottled yellow, green, or white patterns on leaves, stunted growth, and distorted leaves. "
     "Causes: Spread by aphids, whiteflies, and contaminated tools. Common in tomatoes, cucumbers, and peppers. "
     "Prevention: Control insect vectors, use virus-resistant varieties, and disinfect gardening tools. "
     "Treatment: No cure. Remove infected plants to prevent spread."),

    ("Tomato Yellow Leaf Curl Virus", 
     "Symptoms: Yellowing and curling of leaves, stunted growth, and reduced fruit production. "
     "Causes: Transmitted by whiteflies (Bemisia tabaci). "
     "Prevention: Use reflective mulch to deter insects, control whiteflies with insecticidal soap. "
     "Treatment: No direct cure. Use virus-resistant plant varieties and remove infected plants."),

    # Soilborne & Environmental Diseases
    ("Damping-Off", 
     "Symptoms: Seedlings collapse and rot at the soil line. Often leads to failure in germination. "
     "Causes: Caused by soilborne fungi (Pythium, Fusarium) in overly wet, cool conditions. "
     "Prevention: Use sterilized soil, provide proper drainage, and avoid overwatering. "
     "Treatment: Apply biofungicides like Trichoderma or neem-based treatments."),

    ("Verticillium Wilt", 
     "Symptoms: Yellowing, wilting, and browning of lower leaves. Brown vascular tissue in stems. "
     "Causes: Soilborne fungus attacking plant roots, affecting tomatoes, peppers, and trees. "
     "Prevention: Rotate crops, use disease-resistant varieties, and improve soil drainage. "
     "Treatment: No cure. Remove infected plants and avoid replanting in the same soil."),

    ("Clubroot", 
     "Symptoms: Swollen, distorted roots and stunted plant growth. Affects cabbage, broccoli, and cauliflower. "
     "Causes: Soilborne pathogen (Plasmodiophora brassicae) thrives in acidic, wet soils. "
     "Prevention: Maintain soil pH above 7.2, improve drainage, and rotate crops. "
     "Treatment: Apply lime to increase soil pH. Remove and destroy infected plants."),

    ("Blossom-End Rot", 
     "Symptoms: Dark, sunken, leathery patches on the bottom of tomatoes, peppers, and squash. "
     "Causes: Calcium deficiency due to inconsistent watering or excessive nitrogen fertilization. "
     "Prevention: Maintain consistent watering, use mulch to retain moisture, and add calcium (lime, gypsum). "
     "Treatment: Foliar sprays with calcium chloride may help, but prevention is key."),

    # Insect & Parasitic Diseases
    ("Nematode Damage", 
     "Symptoms: Stunted growth, yellowing leaves, and swollen, knotty roots. "
     "Causes: Microscopic roundworms (Meloidogyne spp.) that feed on plant roots. "
     "Prevention: Use nematode-resistant plant varieties, rotate crops, and solarize soil. "
     "Treatment: Apply neem-based soil drenches or introduce beneficial nematodes."),

    ("Aphid Damage", 
     "Symptoms: Curling, yellowing leaves covered with sticky honeydew, which attracts sooty mold. "
     "Causes: Aphids sucking plant sap, weakening the plant and spreading diseases. "
     "Prevention: Attract natural predators (ladybugs, lacewings), plant companion crops like marigolds. "
     "Treatment: Spray with insecticidal soap, neem oil, or a water jet to dislodge aphids."),

    ("Whitefly Infestation", 
     "Symptoms: Yellowing leaves, reduced plant vigor, sticky residue, and sooty mold. "
     "Causes: Whiteflies sucking plant sap and transmitting viral diseases. "
     "Prevention: Use yellow sticky traps, plant reflective mulch, and maintain proper air circulation. "
     "Treatment: Apply neem oil, insecticidal soap, or introduce predatory insects like Encarsia wasps."),
]



# Prepare the dataset
X_train, y_train = zip(*data)
vectorizer = CountVectorizer()
X_train_vectors = vectorizer.fit_transform(X_train)

# Train a Naive Bayes model
model = MultinomialNB()
model.fit(X_train_vectors, y_train)

# Save the model and vectorizer
with open("model.pkl", "wb") as file:
    pickle.dump((vectorizer, model), file)

print("Model training complete. Saved as model.pkl.")
