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
  <p>Ollama is a local inference server that allows you to run large language models like Llama 3.2 directly on your machine. You can follow the official instructions here: 
  <a href="https://ollama.com/download" target="_blank">Download Ollama</a>.</p>

  <ol>
    <li><b>Download and install Ollama:</b>
      <p>Go to <a href="https://ollama.com/download" target="_blank">https://ollama.com/download</a> and download the installer for your operating system. Follow the setup instructions.</p>
    </li>
    <li><b>Start the Ollama server:</b>
      <pre>ollama serve</pre>
    </li>
    <li><b>Run the Llama 3.2 model (3b version):</b>
      <pre>ollama run llama3.2:3b</pre>
      <p>This command will automatically download the model (if not already present) and start it for usage.</p>
    </li>
  </ol>
</li>

<li><b>Install Langchain:</b>
  <p>Langchain is used to manage the structure of the conversation, prompt templates, and the interaction between the chatbot and the LLM (Llama 3.2).</p>

  <ol>
    <li><b>Install Langchain Core:</b>
      <p>This is required to use prompt templates, chains, and other core functionality like <code>PromptTemplate</code> from <code>langchain_core.prompts</code>.</p>
      <pre>pip install langchain-core</pre>
    </li>

    <li><b>Install Langchain Ollama:</b>
      <p>This module allows Langchain to connect directly with the Ollama server that runs the Llama 3.2 model.</p>
      <pre>pip install langchain-ollama</pre>
    </li>
  </ol>
</li>


<li><b>Install and launch Streamlit:</b>
  <p>Streamlit is used to create the web interface of the chatbot. It will open automatically in your browser when you run the app.</p>

  <ol>
    <li><b>Install Streamlit with pip:</b>
      <pre>pip install streamlit</pre>
    </li>
    <li><b>Launch the app:</b>
      <pre>streamlit run main.py</pre>
      <p>This command will start the chatbot interface locally on <code>http://localhost:8501</code>.</p>
    </li>
  </ol>
</li>


<li><b>(Optional) Configure OpenRouter key:</b>
  <p>If using OpenRouter, set your API key as an environment variable:</p>
  <pre>export OPENROUTER_API_KEY=your_key_here</pre>
  </li>




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


