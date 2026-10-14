# LLM / RAG agent state — drives face overlay and debug UI.
# Published by companion_agent during listen → retrieve → think → act → speak.

string IDLE=idle
string LISTENING=listening
string RETRIEVING=retrieving
string THINKING=thinking
string SPEAKING=speaking
string ACTING=acting
string ERROR=error

std_msgs/Header header
string state           # one of the constants above
string provider        # none, ollama, openai
bool rag_used          # true when memories were retrieved this turn
uint32 memory_count    # number of RAG chunks injected this turn
string status_text     # short human-readable line for face subtitle / logs
