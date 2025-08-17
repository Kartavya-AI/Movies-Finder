# AI-Powered Movies Finder 🤖🎬

(Rajani) An intelligent movie recommendation system powered by LangChain, OpenAI GPT, and Streamlit. This AI assistant helps users discover movies through natural language conversations and provides personalized recommendations based on preferences.

## Features ✨

- **AI-Powered Conversations**: Natural language interface powered by GPT-3.5-turbo
- **Movie Recommendations**: Get personalized movie suggestions using TMDB integration
- **Interactive Chat**: Real-time conversation interface built with Streamlit
- **LangSmith Integration**: Advanced tracing and monitoring capabilities
- **MCP Server Integration**: Uses TV recommender MCP server for enhanced functionality

## Tech Stack 🛠️

- **Python 3.12+** - Core programming language
- **LangChain** - AI framework for building applications
- **OpenAI GPT-3.5-turbo** - Large language model for conversations
- **Streamlit** - Web framework for interactive applications
- **LangSmith** - Monitoring and tracing platform
- **MCP (Model Context Protocol)** - Standardized AI tool integration
- **TMDB API** - Movie database integration

## Installation 📦

### Prerequisites

- Python 3.12 or higher
- OpenAI API key
- TMDB API key 

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/Kartavya-AI/Movies-Finder.git
cd movies-finder
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY = your_openai_api_key_here
LANGSMITH_API_KEY =cyour_langsmith_api_key_here
TMDB_API_KEY = your_tmdb_api_key_here
LANGUAGE = en-US
```
Note: Replace `your_openai_api_key_here`, `your_langsmith_api_key_here`, and `your_tmdb_api_key_here` with your actual API keys. 

## Usage 🚀

### Running the Application

Start the Streamlit application:
```bash
streamlit run main.py
```

The application will be available at `http://localhost:8501`

### Using the Interface

1. **Chat Interface**: Type your movie-related questions in the text input
2. **Examples**:
   - "I want to watch documentary on great personalities"
   - "What's a good comedy to watch with family?"
   - "Find movies similar to Inception"
   - "Show me top-rated sci-fi movies"

### API Integration

The system uses multiple APIs:
- **OpenAI API**: For AI-powered conversations
- **TMDB API**: For movie data and recommendations
- **LangSmith**: For conversation tracing and analytics

## Configuration ⚙️

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT integration | Yes |
| `LANGSMITH_API_KEY` | LangSmith API key for tracing | No |
| `TMDB_API_KEY` | TMDB API key for movie data | Yes |
| `LANGUAGE` | Interface language (default: en-US) | No |

### MCP Configuration

The `browser_mcp.json` file configures the MCP servers:

```json
{
  "mcpServers": {
    "TVRecommender": {
      "command": "npx",
      "args": ["tv-recommender-mcp-server"],
      "env": {
        "TMDB_API_KEY": "your_tmdb_key",
        "LANGUAGE": "en-US"
      }
    }
  }
}
```

## Development 🧪

### Running in Development Mode

```bash
# Install development dependencies
pip install -r requirements.txt

# Run in local development mode
streamlit run main.py 
```

### Debugging

Enable debug mode by setting:
```bash
export STREAMLIT_DEBUG=true
```

## Deployment 🚀

### Docker Deployment

```bash
# Build for production
docker build -t movies-finder:latest .

# Run in production
docker run -d \
  -p 8501:8501 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e LANGSMITH_API_KEY=$LANGSMITH_API_KEY \
  movies-finder:latest
```

### Cloud Deployment

#### Streamlit Cloud
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Set environment variables in dashboard

## API Reference 📚

### LangChain Integration

The application uses:
- **ChatOpenAI**: GPT-3.5-turbo for conversations
- **MCPAgent**: LangChain agent with MCP capabilities
- **LangSmith**: For tracing and monitoring

### Streamlit Components

- **st.title**: Application header
- **st.text_input**: User message input
- **st.button**: Clear history functionality
- **st.spinner**: Loading indicators
- **st.markdown**: Message display

## Contributing 🤝

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
