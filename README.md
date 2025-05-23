<h1> 💬 Design and Development of an Automated and Controllable Chatbot for Assistance of Children and Adolescents in Risk</h1>

<h2>📄 Summary</h2>
<p>
This project was created to enhance the efficiency and social impact of the Fundación ANAR’s support service by developing an AI-powered chatbot. 
The goal is to optimize human resources, ensure high-quality initial support, and promote responsible use of the help channel for children and adolescents in distress.
</p>
<p>
<b>Main objectives:</b>
<ul>
  <li>Evaluate how current language models perform in classifying simulated conversations in youth support scenarios.</li>
  <li>Design a modular and scalable architecture that can be integrated with other digital psychosocial support platforms.</li>
  <li>Explore the technical feasibility and performance of open-source AI tools in critical environments.</li>
</ul>
</p>

<h2>⚙️ Installation</h2>

<h3>Technologies Used</h3>
<ul>
  <li><b>Python 3.9+</b> – Core programming language.</li>
  <li><b>Streamlit</b> – Web interface for the chatbot.</li>
  <li><b>Langchain</b> – Manages prompt logic and LLM interaction.</li>
  <li><b>Ollama</b> – Framework to run LLMs locally (required for Llama 3.2).</li>
  <li><b>Llama 3.2 </b> – AI model for natural conversation and classification.</li>
  <li><b>MongoDB</b> – Stores chat history and classification reports.</li>
</ul>


<h3>Setup Instructions</h3>
<pre>
git clone https://github.com/bemepe/Support-BChat.git
cd Support-BChat
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
docker run --name chatbot-mongo -p 27017:27017 -d mongo
ollama serve 
streamlit run main.py
</pre>

<li><b>Set up MongoDB using Docker:</b>
  <p>Before running these commands, make sure you have <b>Docker</b> and <b>mongosh</b> installed. You can follow the official MongoDB instructions here: 
  <a href="https://www.mongodb.com/docs/manual/tutorial/install-mongodb-community-with-docker/" target="_blank">
  Install MongoDB Community with Docker</a>.</p>

  <ol>
    <li><b>Pull the MongoDB Docker image:</b>
      <pre>docker pull mongodb/mongodb-community-server:latest</pre>
    </li
    <li><b>Run MongoDB as a container:</b>
      <pre>docker run --name mongodb -p 27017:27017 -d mongodb/mongodb-community-server:latest</pre>
      <p>This command maps port <code>27017</code> on the container to your local machine, so you can connect to MongoDB using <code>localhost:27017</code>.</p>
    </li>
    <li><b>Check if the container is running:</b>
      <pre>docker container ls</pre>
    </li>
  </ol>
</li>

<li><b>Install and configure Ollama and Llama 3.2:</b>
  <p>To run the language model locally, you need to install <b>Ollama</b>, a tool for serving large language models efficiently on your machine.</p>

  <ol>
    <li>
      <b>Download Ollama:</b>  
      Visit the official website and follow the instructions for your operating system:  
      <a href="https://ollama.com/download" target="_blank">https://ollama.com/download</a>
    </li>

    <li>
      <b>Start the Ollama server:</b>  
      <pre>ollama serve</pre>
    </li>

    <li>
      <b>Run the Llama 3.2 model (3b version):</b>  
      <pre>ollama run llama3.2:3b</pre>
      <p>This will automatically download and start the model the first time it is executed.</p>
    </li>
  </ol>
</li>




<li><b>(Optional) Configure OpenRouter key:</b>
  <p>If using OpenRouter, set your API key as an environment variable:</p>
  <pre>export OPENROUTER_API_KEY=your_key_here</pre>
  </li>

  <li><b>Run the chatbot:</b>
  <pre>streamlit run main.py</pre>
  </li>

<h2>🧭 How It Works</h2>
<p>
The system works through a state-driven conversational flow and validations
</p>
<ul>
  <li>When launched, it displays a warm welcome message via Streamlit in the browser.</li>
  <li>It then collects key information step by step: <b>age</b>, <b>name</b>, <b>location</b>, and <b>situation</b>.</li>
  <li>Each response is validated to ensure it's appropriate and clear.</li>
  <li>All data is stored in real time in a MongoDB database.</li>
  <li>Once the conversation ends, the system classifies it as <i>urgent</i>, <i>non-urgent</i>, or <i>unnecessary</i> using a large language model.</li>
  <li>A concise, empathetic final message is sent to the user, and a report is generated and saved automatically.</li>
</ul>


<h2>📁 Repository Structure</h2>
<pre>
.
├── main.py                   # Main Streamlit app and logic
├── prompts.py                # Dynamic prompts and farewell messages
├── classification.py         # Classification and validation logic
├── chats.py                  # Examples of simulated chats
├── chats_classification.py   # Classification of simulated chats
├── README.md                 # Project documentation
</pre>


