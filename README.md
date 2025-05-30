<h1> 💬 Design and Development of an Automated and Controllable Chatbot for Assistance of Children and Adolescents at Risk</h1>

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
<ul>

  <li><b>Set up MongoDB using Docker:</b>
    <p>Before running these commands, make sure you have <b>Docker</b> and <b>mongosh</b> installed. You can follow the official MongoDB instructions here: 
    <a href="https://www.mongodb.com/docs/manual/tutorial/install-mongodb-community-with-docker/" target="_blank">
    Install MongoDB Community with Docker</a>.</p>
    <ol>
      <li><b>Pull the MongoDB Docker image:</b>
        <pre>docker pull mongodb/mongodb-community-server:latest</pre>
      </li>
      <li><b>Run MongoDB as a container:</b>
        <pre>docker run --name mongodb -p 27017:27017 -d mongodb/mongodb-community-server:latest</pre>
        <p>This maps port <code>27017</code> to your machine so MongoDB is accessible at <code>localhost:27017</code>.</p>
      </li>
      <li><b>Check if the container is running:</b>
        <pre>docker container ls</pre>
      </li>
    </ol>
  </li>

  <li><b>Install and configure Ollama and Llama 3.2:</b>
    <p>Ollama is a local inference server to run large language models like Llama 3.2 on your machine.</p>
    <ol>
      <li><b>Download and install Ollama:</b>
        <p>Go to <a href="https://ollama.com/download" target="_blank">https://ollama.com/download</a> and follow the setup instructions.</p>
      </li>
      <li><b>Start the Ollama server:</b>
        <pre>ollama serve</pre>
      </li>
      <li><b>Run the Llama 3.2 model (3b version):</b>
        <pre>ollama run llama3.2:3b</pre>
        <p>This will download and launch the model automatically on first use.</p>
      </li>
    </ol>
  </li>

  <li><b>Install Langchain:</b>
    <p>Langchain manages the conversation logic, prompt templates, and connection with the LLM.</p>
    <ol>
      <li><b>Install Langchain Core:</b>
        <p>Used for building prompts and chains via <code>langchain_core.prompts</code>.</p>
        <pre>pip install langchain-core</pre>
      </li>
      <li><b>Install Langchain Ollama:</b>
        <p>Required to connect Langchain with your Ollama LLM instance.</p>
        <pre>pip install langchain-ollama</pre>
      </li>
    </ol>
  </li>

  <li><b>Install and launch Streamlit:</b>
    <p>Streamlit powers the user interface of the chatbot and runs in the browser.</p>
    <ol>
      <li><b>Install Streamlit:</b>
        <pre>pip install streamlit</pre>
      </li>
      <li><b>Launch the app:</b>
        <pre>streamlit run main.py</pre>
        <p>It will open at <code>http://localhost:8501</code>.</p>
      </li>
    </ol>
  </li>

  <li><b>(Optional) Configure OpenRouter key:</b>
    <p>If you're using OpenRouter as a model backend, set your API key:</p>
    <pre>export OPENROUTER_API_KEY=your_key_here</pre>
  </li>

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


<h2>🧭 How It Works</h2>

<p>
When the user enters the platform, they are greeted with the main chatbot interface, which includes a clear title and a welcoming header.
</p>


<p>
The chatbot begins with an automatic welcome message. The user types a response into the input bar and presses "Enter" to continue.
</p>

<img src="interface_user.png" alt="Welcome message and input bar" width="600"/>

<p>
Next, the chatbot initiates the data collection phase, asking for: <b>age</b>, <b>name</b>, <b>location</b>, and <b>situation</b>. The user simply replies, while the system validates each response in the background.
</p>

<img src="urgente_visual.png" alt="Validation output in terminal (developer view)" width="600"/>

<p>
After successfully collecting all essential information, the chatbot asks one final, more detailed question about the user's situation. This answer is not validated, but it is included in the classification.
</p>


<p>
The conversation is then automatically classified based on urgency and appropriateness. A final farewell message is displayed based on this result.
</p>

<img src="urgente2.0.png" alt="Complete conversation with final message based on classification" width="600"/>

<p>
A report is generated and saved to MongoDB, containing the full conversation and classification details. The terminal shows real-time updates for these operations.
</p>

<img src="report.png" alt="Example of report saved in Visual Studio Code terminal " width="800"/>

<p>
Once the conversation ends, the input bar disappears, signaling to the user that the session is closed and preventing further interaction.
</p>




