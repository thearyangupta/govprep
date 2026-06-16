class ConversationMemory:
    """Holds the running conversation as a list of turns."""

    def __init__(self, max_turns=10):
        self.turns = []  # list of {"question":..., "answer":...}
        self.max_turns = max_turns

    def add(self, question, answer):
        self.turns.append({"question": question, "answer": answer})

        # Keep only the last max_turns to control prompt size/cost
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]

    def as_text(self):
        """Format history as text for prompts."""

        if not self.turns:
            return "(no previous conversation)"

        lines = []

        for t in self.turns:
            lines.append(f"User: {t['question']}")
            lines.append(f"Assistant: {t['answer']}")

        return "\n".join(lines)

    def recent_questions(self, n=3):
        """Just the last n user questions - used for query rewriting."""

        qs = [t["question"] for t in self.turns[-n:]]
        return qs

if __name__ == "__main__":
    mem = ConversationMemory()

    mem.add("Who is the President?", "The President is the head of state.")
    mem.add("What are their powers?", "Executive powers include...")

    print(mem.as_text())
    print("\nRecent questions:", mem.recent_questions()) 