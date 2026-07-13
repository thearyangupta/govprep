def recursive_chunk(text, chunk_size=500, overlap=50):
 """Split on paragraphs, then sentences, keeping chunks whole."""
 separators = ["\n\n", "\n", ". ", " "]

 def split(text, seps):
  if len(text) <= chunk_size or not seps:
   return [text]

  sep = seps[0]
  parts = text.split(sep)

  chunks, current = [], ""

  for part in parts:
   piece = part + sep

   if len(current) + len(piece) <= chunk_size:
    current += piece
   else:
    if current:
     chunks.append(current)

    # part itself too big? recurse with finer separator
    if len(piece) > chunk_size:
     chunks.extend(split(piece, seps[1:]))
     current = ""
    else:
     current = piece

  if current:
   chunks.append(current)

  return chunks

 return split(text, separators)