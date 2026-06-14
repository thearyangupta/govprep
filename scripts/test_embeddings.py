from sentence_transformers import SentenceTransformer

# Load the model
print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')#this model always contain 384 numbers
print("Model loaded.\n")

# Test 1: Embed a single sentence
text = "The President of India is the head of state."
embedding = model.encode(text)
print(f"Text: '{text}'")
print(f"Embedding dimension: {len(embedding)}")
print(f"First 10 numbers: {embedding[:10]}")
print(f"Type: {type(embedding)}")
print("\n" + "="*60 + "\n")

# Test 2: Show similarity in action
sentences = [
 "Who is the prime minister of India?",
 "India's PM",
 "The PM of India",
 "I love eating mangoes",
 "Mango is my favorite fruit",
 "The capital of France is Paris",
]
embeddings = model.encode(sentences)

# Cosine similarity between embeddings - higher = more similar
from sentence_transformers.util import cos_sim #cosine similarity = How similar are two embeddings
similarity_matrix = cos_sim(embeddings, embeddings) #this compares
print("Similarity matrix (1.0 = identical meaning, 0.0 = unrelated):\n")
print(f"{'':<40}", end='')#Create a field that is 40 characters wide."Since the string is empty, all 40 positions become spaces.
for i in range(len(sentences)):
 print(f"S{i} ", end='')
print()

for i, sent in enumerate(sentences):
    print(f"S{i}: {sent[:36]:<40}", end='')
    for j in range(len(sentences)):
     print(f"{similarity_matrix[i][j]:.3f} ", end='')
    print()