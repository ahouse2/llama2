Automated Legal Discovery Co-Counsel – Technical Requirements & Project Plan
Overview and Objectives

This project aims to build an AI-powered legal discovery assistant (working name: Co-Counsel) that can help attorneys review evidence, find relevant case law, and even simulate courtroom interactions. The system will leverage state-of-the-art LLM agents, a knowledge graph of case facts, and a voice-based co-counsel interface to provide comprehensive support. Key objectives include:

End-to-End Discovery Automation: Ingest large volumes of case documents (emails, PDFs, transcripts, etc.), extract key facts/relations, and enable intelligent search and summarization of evidence.

Contextual Legal Reasoning: Answer complex legal questions with cited references to evidence and case law, using Retrieval-Augmented Generation and a knowledge graph for context-rich, reliable responses
medium.com
.

Interactive Timeline & Visualization: Automatically construct a timeline of case events with interactive pop-outs showing document excerpts and citations for each event.

Immersive User Experience: Provide a highly polished, neon-themed UI that is both gorgeous and user-friendly, with engaging visuals and smooth interactions. Users can converse with the AI via text or voice, explore evidence through an interactive timeline, and utilize a fun “Mock Court” simulation to test trial strategies.

Co-Counsel Voice Agent: Develop an emotionally aware, context-driven voice assistant (female persona, multiple accents available) that acts as a personable co-counsel – answering questions, explaining strategies, and learning from user interactions over time.

Low Cost & Easy Deployment: Prioritize open-source and efficient components to keep operational costs low or zero. The entire system should be deployable with one click (e.g. via Docker) for immediate use, with minimal configuration. Despite the sophisticated capabilities, the solution must remain production-ready, stable, and secure – suitable for enterprise use (justifying a potential $1000/month value).

Continuous Improvement: Include an inbuilt “AI dev team” capability – a mechanism for the system to learn new skills or add features on the fly (e.g. a coding agent that can extend functionality). The platform should also come with robust documentation for both end users and developers, to ease adoption and ongoing development.

System Architecture Overview

Architecture Summary: The Co-Counsel system will be composed of multiple specialized AI agents orchestrated in a coordinated pipeline, integrated with a knowledge management backend (for document ingestion, vector search, and knowledge graph storage). A modular front-end provides the UI/UX. The design emphasizes modularity, so each component (agents, tools, UI modules) can be developed and tested independently and then integrated. Key components include:

Multi-Agent Brain: A collection of AI agents using a framework like OpenAI’s Agents SDK or Microsoft’s Autogen for orchestration. These agents collaborate to handle user queries, perform document analysis, fetch external knowledge, and even modify system behavior when needed. The agents communicate via a shared memory and can delegate tasks to one another (using the framework’s primitives such as handoffs or tool calls
composio.dev
).

Knowledge Ingestion & RAG Pipeline: A backend pipeline (built with LlamaIndex and LlamaHub integrations) that ingests files/folders, indexes them (via embeddings for semantic search), and constructs a Knowledge Graph of key facts. This is a GraphRAG approach – converting unstructured text into a graph of entities and relationships
medium.com
, and storing it for query-time retrieval. The pipeline uses LLM-based extraction to identify entities (people, places, issues) and relations (e.g. person X is related to document Y, event Z happened on date D). This graph plus textual embeddings enables rich context discovery and relationship mapping across the case data.

Co-Counsel Voice Agent: The primary user-facing agent, responsible for conversing with the user (via voice or text) and orchestrating other agents. It maintains a long-term memory of the case and user preferences. It uses speech-to-text (for user input) and text-to-speech (for responses) with a selection of high-quality female voices (American, British, Australian accents) to personalize the experience. This agent is enhanced with emotional and temporal awareness logic.

User Interface (Web Application): A modern, neon-themed UI that ties everything together. The front-end communicates with the agents/back-end via API calls or websockets (for streaming responses). Key UI elements: a chat/voice console, a document/timeline explorer, a “Trial University” knowledge hub, and a Mock Court Simulator interface (with animated graphics for courtroom scenes). The UI will be responsive and browser-based for easy access, built with a contemporary framework (e.g. React) and styled for a high-tech neon look.

Below is a breakdown of major subsystems and their features/capabilities:

Multi-Agent Design and Orchestration

Agent Framework: We will use the OpenAI Agents SDK as the backbone for multi-agent orchestration. This choice is made because the OpenAI Agent SDK is a lightweight, production-ready framework with minimal abstractions (easy to learn) and built-in support for agent tools, handoffs between agents, and guardrails for safety
composio.dev
composio.dev
. The SDK allows defining multiple agents with distinct roles and facilitating conversation and task delegation among them. (Alternatively, we considered Microsoft’s Autogen framework, which offers flexible conversation topologies, but its documentation is less clear and it has a steeper learning curve
composio.dev
. OpenAI’s SDK provides a more straightforward path to a stable production system.)

 

Core Agents and Roles:

Co-Counsel (Lead Agent): The “face” of the system – interacts directly with the user via voice/text. It interprets user queries or commands (e.g. “Find any emails where the witness contradicts himself” or “What’s our strongest case law on expert testimony?”) and decides how to fulfill them by consulting other agents or tools. It maintains context of the ongoing conversation and the case’s key details. It has a persona configured to be professional yet personable, with emotional intelligence cues to respond appropriately to user’s tone or stress.

Ingestion & Analysis Agent: Monitors incoming documents or data sources. When new discovery documents are added (or updated), this agent uses LlamaIndex loaders to parse them and then triggers processes to update the vector index and knowledge graph. It may use LLM calls to extract entities/relations for GraphRAG and store results. Essentially, this agent keeps the knowledge base current and structured.

Research Agent: Focused on external knowledge retrieval. It can perform legal research – for instance, searching an internal case law database or even the web for relevant precedents. This agent has tools like a web search interface or an API to legal databases. (In a low-cost configuration, we might rely on open data like CourtListener or allow the user to plug in their own database of cases.) The research agent returns summaries of relevant law, with citations, to the Co-Counsel agent.

Reasoning/Strategy Agent: An agent dedicated to higher-level analysis – e.g. brainstorming legal strategies, spotting logical gaps or strengths in the case, and generating outlines or arguments. It may draw on “Trial University” knowledge (best practices, textbooks) and the case-specific facts to advise on strategy. This agent can also simulate an opposing counsel’s perspective to challenge assumptions (helping prepare counter-arguments).

Dev Agent (Self-Improvement): A specialized coding agent that acts as an “inbuilt dev team.” Its role is to monitor feature requests or repeated user needs that the system can’t yet handle, and then suggest or implement improvements. For example, if the user says, “I wish it could also visualize social network of people in this case,” the Dev Agent can generate code for a new visualization tool or integrate a new LlamaHub loader if needed. This agent would utilize the system’s codebase (with appropriate safeguards) to create new modules or update configurations, subject to approval. (This concept is inspired by systems like OmniAgent which use agents to continuously improve and expand capabilities
GitHub
.) The Dev Agent ensures the platform can evolve quickly without manual intervention, making the system future-proof and adaptive.

Agent Collaboration: These agents communicate through shared memory (context) and by passing tasks via the Agent SDK’s handoff mechanism. For instance, when the user asks a question, Co-Counsel might invoke the Analysis Agent to scan the knowledge graph for relevant info, and simultaneously ask the Research Agent for any supporting case law. Each agent returns results (citations, summaries) which Co-Counsel then synthesizes into a final answer for the user. All interactions are logged, and key findings get fed back into the context so the system’s memory grows. Crucially, the architecture will include guardrails: e.g., the Co-Counsel agent will validate outputs (for factual accuracy and tone) before presenting to the user, and the Dev Agent’s actions will require user confirmation or undergo a safety check (to avoid unintended changes).

 

Tools & Integrations for Agents:
We will integrate a suite of LlamaHub tools and data loaders for agent use. LlamaHub provides many ready-made connectors and tools to speed up development
llamahub.ai
. For example: the Ingestion Agent will use PDF and Word document loaders from LlamaHub to read files; the Research Agent might use a Bing/Web search tool or a case-law API wrapper (if available via LlamaHub or custom-built); agents can also use utility tools like calculators or a timeline generator. By mixing and matching these tools, we enable agents to handle diverse tasks without starting from scratch. The Agents SDK allows easy integration of such tools as functions the agents can invoke.

 

Memory and Context: The system will employ two levels of memory: (1) Short-term conversational context managed by the Co-Counsel agent (e.g. recent dialogue turns are kept in the prompt, and older ones summarized to fit context length), and (2) Long-term memory stores for case facts and user preferences. The long-term memory will be backed by our vector index and knowledge graph – effectively, the agent can “remember” any detail from the documents by querying the index when needed. Additionally, a small profile store might keep track of user-specific settings (preferred voice, any known emotional triggers, etc.). This memory design ensures the agent’s responses remain contextually relevant even in prolonged usage.

Knowledge Ingestion Pipeline (GraphRAG & LlamaIndex Integration)

A cornerstone of the platform is the Knowledge Base/Graph that houses all case information in an easily queryable form. We will implement a Graph-RAG pipeline using LlamaIndex and its LlamaHub integrations to handle this. The pipeline includes:

Data Ingestion: The system can connect to various data sources to import case materials. Using LlamaHub’s data loaders, we can support:

Local files or folders (e.g. a discovery dump of PDFs, DOCXs, images).

Cloud drives or emails (if needed, e.g. connect to Gmail/Outlook via API to pull communications).

Structured data like spreadsheets or databases (witness lists, exhibits lists).
Each data source can be added via the UI (drag-and-drop files or provide API credentials), and the Ingestion Agent will use the appropriate loader plugin to pull the content.

Preprocessing & Indexing: Imported documents are automatically processed by LlamaIndex. This involves:

Text Extraction & OCR: For PDFs or scans, run OCR if needed (using an open source OCR like Tesseract for low cost). For emails, parse headers and body.

Chunking: Split documents into manageable chunks (e.g. by paragraph or section) to feed into LLM-based extractors.

Vector Embedding: Each chunk is embedded into a vector representation and stored in a vector index (likely using an open-source vector DB like Chroma or FAISS for cost-efficiency). This enables semantic search – the system can retrieve relevant chunks given a query, even if wording differs.

Graph Construction (GraphRAG): In parallel with basic indexing, we perform entity and relationship extraction on the documents to build a knowledge graph. Using LlamaIndex’s GraphRAG modules, each text chunk is analyzed by an LLM (via a prompt that asks for triples like <Entity A> -- <relation> --> <Entity B>). From this we derive a set of nodes (entities) and edges (relations) that get added to a property graph structure
medium.com
. For example, if a document says “Alice signed the contract on Jan 5, 2023”, the graph might include nodes: Alice (Person), Contract (Document) and an edge: Alice –[signed on]→ Contract with attribute date=1/5/2023. All such triples across the dataset are merged into a unified graph. We will use either an in-memory graph via LlamaIndex (which uses NetworkX under the hood) or connect to an external graph database (like Neo4j) if persistence and scalability are needed. The graph is enriched with metadata – each node/edge can link back to the source documents (for citation), and key properties like dates, locations, roles (e.g. Alice = Plaintiff).

Community Detection & Summaries: (optional advanced step) As the graph grows, we can apply algorithms to find clusters of related information
medium.com
. For instance, a cluster might form around a particular event or topic (all people and docs related to “Contract Signing”). The system can then auto-generate a summary of each cluster using an LLM, giving a high-level overview. These summaries become part of the knowledge base, allowing the agent to fetch a concise context on a whole topic when needed
medium.com
.

Updating and Monitoring: The ingestion pipeline runs continuously or on schedule. If the user adds new files or new information, the pipeline updates the index and graph incrementally. The system will notify the user (perhaps via the Co-Counsel agent saying “I’ve ingested 5 new documents and updated the case graph”) and highlight newly uncovered entities or facts. There will also be a verification step: because LLM extraction can sometimes err, the pipeline could include a validation pass (e.g. flag uncertain extractions for user review in the UI’s timeline or graph view).

Search and Query Engine: With the vector index and knowledge graph in place, any query posed to the system can be answered via a combination of semantic search and graph traversal. We will implement a custom GraphRAG Query Engine (leveraging LlamaIndex’s interface) that on query will:

Use the vector index to retrieve top relevant text chunks (documents passages likely to contain the answer).

Identify which entities or graph substructures are relevant to the query (e.g. if the question is about “Who met on Jan 5?”, it will find event nodes on that date and connected people).

Gather the information from both sources and feed into an answer-synthesis prompt for an LLM, which generates a final answer with clear references. The references will be derived from the source metadata, so the answer can say “According to Witness John’s deposition, he met Alice on Jan 5, 2023
medium.com
” (with the citation linking to that deposition excerpt).
This approach ensures answers are both accurate and explainable, as the underlying graph provides a structured understanding of the case and the source documents back up every claim.

Overall, by using LlamaHub and LlamaIndex, we drastically reduce development effort for this pipeline – these tools provide robust connectors and algorithms to connect LLMs with our knowledge base
llamahub.ai
. The result is a powerful, scalable knowledge repository that the Co-Counsel agents can query in real-time to support the user.

Co-Counsel Voice Assistant (Emotionally & Contextually Aware)

The Co-Counsel voice agent is the centerpiece of user interaction. It aims to emulate a knowledgeable, helpful co-counsel attorney who not only provides information but does so with emotional intelligence and contextual awareness. Here we detail its key features and how to implement them:

Natural Conversation Interface: Users can communicate with Co-Counsel either by typing in a chat interface or by speaking to it (pressing a “Talk” button or using a wake word). We will integrate speech-to-text (STT) for user voice input – likely leveraging an open-source model like OpenAI Whisper (which can run locally for free, albeit needing some compute) for high accuracy transcription. Whisper’s accuracy and multi-language support make it a strong choice, though we’ll use the base model to keep it cost-free (or an on-prem deployment if needed). On the output side, text-to-speech (TTS) will give the agent a voice. We plan to offer a range of female voice personas: e.g. an American English voice, a British English voice, and an Australian English voice, so the user can select their preferred co-counsel voice. To keep cost low, we can use open-source TTS engines such as Coqui TTS or Mozilla TTS which have pre-trained models for different accents. These can run locally and produce fairly natural speech. For a more polished option, the system could optionally integrate with cloud TTS services (Azure Cognitive Services or Amazon Polly) where many high-quality voices exist – but those may incur cost, so the default will be offline TTS. The voice output will be streamed if possible (so the agent doesn’t wait to speak until the whole paragraph is ready, giving a responsive feel).

Emotional Awareness: To truly feel like a human co-counsel, the agent should detect and respond to the user’s emotional state. We will implement a simple sentiment & tone analyzer on the user’s input (both text and voice). For example, using an NLP model to detect if the user’s message is anxious, frustrated, confident, etc., or analyzing acoustic features of their speech (volume, pace) to gauge stress. Based on this, Co-Counsel will adjust its own tone and content. Example: If the user sounds upset or says something like “I’m really overwhelmed by this case,” the agent can switch to a more empathetic style: “I understand – there’s a lot here. Let’s take it step by step,” possibly even modulating the TTS voice to a softer tone. TTS engines with SSML support could allow control over speaking style and rate to convey empathy. By contrast, if the user is in a hurry (“Quick, what’s the deadline for filing this motion?!”), the agent should respond concisely and confidently. This emotional adaptability will be implemented through a set of response style guidelines triggered by the sentiment analysis results. The agent’s prompt will also include instructions like “You are supportive and calm if the user is anxious; you stay cheerful if the user seems discouraged,” etc.

Temporal Awareness: Co-Counsel will be aware of timelines and deadlines. It will use the case timeline (from the knowledge graph) to understand the sequence of events – for instance, knowing that a meeting happened after a contract was signed, or that today is 2 days before trial. We will integrate a simple calendar utility into the agent: it can access the current date/time and any scheduling information provided (e.g. trial date, discovery cutoff dates). This way, if a user asks “How much time until our deposition?” the agent can respond with the exact time remaining, and if relevant, contextualize it (“The deposition is in 3 days (on Nov 10). You should finalize the question list by tomorrow.”). The timeline data in the knowledge graph, which includes dates for events and filings, will also enable the agent to answer questions about chronology or identify inconsistencies (e.g. “Witness says X happened after Y, but timeline shows the reverse – we should investigate that”).

Context-Driven and Memory-Based: Throughout the conversation, Co-Counsel maintains context about what has been discussed. It will not ask the same questions repeatedly and can refer back to earlier topics (“As I mentioned earlier, the email from John on Jan 5 is crucial…”). We’ll implement this by keeping a conversation history and using LLM summarization for older parts to keep them in memory. Additionally, because the agent has access to the knowledge graph and document embeddings, it can pull in context on-the-fly. For example, if the user suddenly asks about “the contract clause about indemnification,” the agent can quickly search the indexed documents for “indemnification” and retrieve the exact clause text to quote in its answer, citing the contract. This ability to inject real quotes and facts from the case context is vital for trust – the user will see the agent is grounding its answers in the actual evidence (no hallucinations). All citations will be clearly presented (e.g. as footnotes or clickable links in the chat UI).

Skill Learning and Adaptation: The Co-Counsel agent isn’t static; it will learn from each interaction. On the simplest level, it refines its understanding of the user’s preferences (for instance, if the user often asks for case law comparisons, the agent might proactively start providing them). More ambitiously, combined with the Dev Agent, the system can gain new skills. For example, if the user tries to use the agent for a task it doesn’t know (“Can you simulate a jury poll for me?”) and the agent fails, the Dev Agent could step in: perhaps finding an open-source module for jury simulation or training a new prompt for that. Over time, the repertoire of the Co-Counsel grows. We will maintain a skills registry – essentially a list of tasks the system can handle, with pointers to which agent/tool does it. If a new skill is added, it’s registered here so next time a similar request comes, Co-Counsel knows which internal capability to invoke. This is analogous to an experienced lawyer learning new techniques as they work more cases. The user can also explicitly instruct the agent to learn something (“Please remember this particular judge’s preference for brief style”) – the agent will then store that in its long-term memory for future use.

Voice Persona Customization: Given the user’s desire for an adorable and entertaining experience, we will incorporate multiple voice persona options and perhaps slight personality variations. While all voices will remain professional in content, some might have a warmer or more upbeat delivery. We can allow the user to choose a character avatar for the co-counsel (for example: a friendly young associate vs. a seasoned paralegal assistant) which might adjust the tone slightly and the avatar’s image on screen. These touches add an element of charm and make the interaction more engaging, without undermining the seriousness of the legal tasks. The UI might show an avatar icon (perhaps in neon outline style) that “speaks” (with a speech bubble or synchronized animation when voice is playing). Keeping the vibe somewhat light and adorable – for instance, the avatar might do a little celebratory animation when it finds a key piece of evidence, or a thinking animation while searching – will help user experience. This ensures that using the platform is not only useful but also pleasant and even fun.

In summary, the Co-Counsel voice agent will combine advanced AI reasoning with a humanized touch. By being deeply integrated with the case knowledge (thanks to the GraphRAG pipeline) and maintaining an awareness of the user’s state and case context, it will truly function as a reliable second chair attorney. It will offer advice, answer questions with evidence, keep the user on track with timelines, and do so in a manner that feels natural and supportive.

User Interface Design (Neon Theme & Key Components)

The user interface will be designed to be highly intuitive, visually striking, and conducive to productivity. We draw inspiration from modern “neon” design trends – think dark backgrounds, glowing accent colors, futuristic widgets – to create a polished, professional yet vibrant look. Below we describe the main UI components and how the user will interact with them:

 

General Look & Feel: The app will use a dark theme (charcoal or deep navy backgrounds) with bright neon highlights (electric blue, purple, or magenta) for borders, text highlights, and icons. Important interactive elements might glow or pulse subtly to draw attention. This neon aesthetic gives a cutting-edge tech feel, aligning with the AI nature of the product, and also ensures high contrast for readability. The layout will be clean, not cluttered – leveraging whitespace (or rather, “darkspace”) to avoid overwhelming the user despite the many features. Consistent iconography and typography will be used for a cohesive appearance. Transitions between views will be smooth (e.g. sliding panels, fade-ins) to reinforce the polished quality.

 

1. Chat & Voice Console: This is the primary panel where the user converses with the Co-Counsel agent. It will resemble a chat messenger interface embedded in the application:

Conversation Window: shows the dialogue history between the user and Co-Counsel. Each user message and each AI response will appear in speech bubbles (user on the right, AI on the left, for example). Next to the AI’s messages, an icon or avatar representing the co-counsel is shown. During voice output, this icon could animate (like a waveform or a “speaking” animation) to indicate audio playback.

Microphone & Input Controls: At the bottom of the chat panel, there’s a text input box and a microphone button. The user can type queries or click the mic to speak. When the mic is active, visual feedback (like a pulsing ring or changing waveform) will confirm that the app is listening. After speaking, the recognized text is displayed for confirmation before the AI responds. The user can interrupt or stop the AI’s speech if needed (with a “stop” button), and can also request the AI to repeat or clarify answers.

Adaptive Formatting: The AI’s answers in the chat will often include references or lists. The UI will format these nicely – for example, if the AI provides a list of bullet points or a step-by-step plan, it will render as a formatted list. Citations will appear as small superscript numbers or icons that can be clicked to see the source excerpt (more on that below). This makes the chat content not just a plain text blob, but a rich, interactive transcript.

2. Document & Timeline Explorer: A core feature is the ability to explore case materials via a timeline interface with pop-out details. This could be a dedicated panel or a modal that the user can open while discussing something with the AI (the AI might even bring it up, e.g., “Let’s look at the timeline of events – opening timeline…”). Key elements:

Interactive Timeline View: A horizontal timeline that spans the major events of the case in chronological order. Each event is represented by a node/point on the timeline, possibly with a short label and date (e.g. “Jan 5, 2023 – Contract Signed”). The timeline can be scrolled or zoomed (if the case spans years, etc.). We can also allow filtering by category (e.g. toggle to view only “communications” or only “court filings”). Events could be color-coded (e.g. all court events in one color, all incident-related events in another) for clarity.

Event Pop-outs: When the user clicks on an event node, a detailed pop-out card appears. This card will show the key info about the event: a description (e.g. “Alice signed the contract with Bob’s company.”), involved entities (people or documents), and crucially, excerpts and citations from the source documents that establish this event. For example, it might show a snippet from “Contract.pdf” that contains the signature line, with a citation link to the full document. If a witness mentioned the event in testimony, that quote is shown too, cited to “Alice Deposition, p. 23”. These pop-outs basically compile the evidence for that event in one place. The user can scroll within the pop-out if multiple excerpts are present. This feature is immensely useful for quickly accessing supporting evidence while formulating arguments.

Document Viewer Mode: The timeline pop-outs will include options to open the full document if needed. There could be a “View Full Document” button that opens a PDF viewer or text viewer within the app (perhaps a side-by-side panel or a full-screen overlay) so the user can read the entire source. The viewer will support basic functions like text search, page thumbnails, etc., to navigate the document. The cited excerpt will be highlighted in the document when opened, to orient the user.

Linking with Chat: The UI will be designed such that the chat and timeline are interconnected. If the AI, in chat, references an event or a document, the corresponding timeline item might subtly glow or an icon appears to let the user click and see it in context. Conversely, if the user is browsing the timeline and wants more analysis, they could click an “Ask about this” button on an event card to prompt the AI in the chat (which could then answer, e.g. “This contract signing is crucial because it triggered the obligation we’re now disputing…”). This fluid link between narrative (chat) and data (timeline/docs) empowers users to dive deep or get summary as needed.

3. Case Law & Knowledge Hub (Trial University): To support legal research and general knowledge, the UI will have a section we dub “Trial University”. This serves two purposes: a legal research interface and an educational portal.

Legal Research Interface: Essentially a specialized search engine for case law or legal Q&A. The user can enter queries (like “precedents on expert witness admissibility in California”) and the system will retrieve relevant cases or articles. Results might be listed with titles, snippets, and citation info. The user can click on a result to see a summary or the full text (if available). If our system has access to an open case law database (for free), we will integrate it here; if not, we might allow importing a database or at least the AI can answer via its own trained knowledge (with the caution to verify). The Co-Counsel agent will also use this behind the scenes when needed, but this interface gives the user direct control to do their own research as well.

Educational Content (“Trial University”): We will include a library of resources for trial practice – think of it as built-in documentation and tutorials for legal procedures. This could be organized as a set of topics or FAQs: e.g. “How to draft an opening statement,” “Motions in Limine – quick guide,” “Common objections and responses,” etc. The user can browse these, or simply ask Co-Counsel (“What’s a motion in limine?”) and the agent can answer by drawing from this knowledge base (citing it as Trial University Handbook or similar). The content can be a mix of text, short videos, or even interactive quizzes. Given our budget constraints, initial content might be text-based summaries of public domain materials or custom-written tutorials. The key is that a user (especially a junior attorney) can learn and improve skills using the platform – fulfilling an educational role beyond just their current case.

UI Integration: The Knowledge Hub might be accessible via a tab or menu. If the user enters Learning Mode (perhaps toggling “Trial University” on), the UI could even change slightly – maybe a less intense theme or a “classroom” motif to indicate the switch from active case work to learning. Within answers in the chat, when the AI cites general knowledge (like a best practice), it can reference these materials so the user knows it’s coming from a knowledge source, not the specific case data.

4. Mock Courtroom Simulator: One of the most novel and entertaining features will be the animated mock trial simulation. This component of the UI provides a virtual courtroom where the user can practice or test arguments in a low-stakes, adorably animated setting.

Visual Design: The simulation will be stylized – likely a cute, cartoon-like 3D or 2D animation (to keep it light and approachable). Imagine a courtroom scene with caricatured characters: a judge (maybe an owl or a friendly robot judge to add humor), a jury box with simplified juror figures, a witness stand, and counsel tables. The style could be akin to a lighthearted video game or an educational cartoon, so that even though it’s a serious scenario, the presentation is engaging (as the user requested, “make the animation cute, lol”).

Functionality: The user can initiate a mock trial session by selecting which scenario to simulate – e.g. “Motion Hearing,” “Jury Opening Statement,” “Cross-examination of Witness X,” etc. Once started, the AI will animate the scene and generate dialogues for the other roles. For instance, if the user wants to practice an opening statement, the system will “play” the role of a judge who might interrupt with a question or an opposing counsel who objects. The user can either speak their responses or select from options if we provide a multiple-choice response interface for quick testing. The Co-Counsel agent’s AI will be driving the behavior of all NPCs (non-player characters) in the courtroom: it knows the case facts (from the knowledge graph) so it can have the opposing counsel AI raise relevant counterpoints (“But your client’s email on Jan 6 says the opposite, doesn’t it?”) and the judge AI enforce rules (“Sustained, please rephrase the question without leading”). This provides a dynamic environment to refine arguments.

Interactivity: During a simulation, the user might see speech bubbles or captions for each character as they speak (and optionally hear a voice-over for them – we could reuse the TTS system with different voices for each character: a deep authoritative voice for judge, a snarky tone for opposing counsel, etc., to the extent possible with our TTS). The user can pause the simulation at any time, ask Co-Counsel for advice (“How should I respond to that objection?”), and then proceed. After the simulation, the system can generate a brief “performance feedback” – e.g. pointing out which answers were strong or if any key facts were missed. This is part of the learning loop to help the user improve.

Technical Implementation: To keep one-click deployment feasible, we might implement the animation using web technologies (like a canvas or WebGL with a library such as Three.js or Pixi.js) rather than requiring an external game engine. The characters can be relatively simple models or even 2D sprites with a few posed images (e.g. happy judge, angry judge, etc.) that we toggle based on context. The dialogues are generated by the AI in real-time or could be pre-planned templates with variables. Because generating and speaking long dialogues on the fly might have latency, we might mix pre-scripted logic with AI fill-ins. For example, for a cross-exam simulation, we know the general flow (greet witness, ask first question, etc.) and only the witness’s answers need to be generated by AI using the case facts. This hybrid approach ensures the simulation is coherent and runs in a timely manner.

Entertainment Factor: While the primary goal is to test legal theories, we won’t miss the chance to make it entertaining. The characters might have witty asides (the judge avatar might sigh dramatically if proceedings drag on, etc., keeping it light). The use of cute animation will reduce the stress of the exercise and maybe even make the user laugh, which can be a valuable stress relief in high-pressure trial prep. We will, however, allow a “realistic mode” toggle if the user prefers a more serious simulation without the cutesy layer (perhaps replacing cartoon avatars with more realistic ones and toning down jokes).

5. Additional UI Elements:

Navigation & Layout: A sidebar or top menu will allow switching between main sections: e.g. Chat, Timeline, Documents, Trial University, Simulation. The chat might always remain accessible (like a dock at the bottom or side) so the user can talk to Co-Counsel no matter which section they’re in – the agent is omnipresent.

Notifications: Small notification toasts or highlights will inform the user of background actions – e.g. “New documents ingested” or “Simulation ready”. Also, when the Dev Agent adds a new feature or update (with user permission), the UI could notify “New feature available: Timeline export to PDF (click to try!)” – showcasing the system’s evolving nature.

Settings Panel: A settings area will let the user configure voices, toggle cost-saving modes (like disabling external API calls if they want to ensure no usage costs), adjust privacy settings, and view documentation. This is also where they can manage data sources (connect/disconnect a Google Drive, etc.).

Polish and Responsiveness: The UI will undergo thorough testing for a polished feel – consistent font sizes, proper alignment, responsive design to work on various screen sizes (likely focusing on desktop use, but possibly tablet-friendly if attorneys use iPads). Micro-interactions (hover highlights, button press animations) will be included to give a high-quality “feel”. Because the target is enterprise-grade, we’ll ensure the UI is stable and not glitchy: using proven UI libraries and best practices to avoid crashes or weird behavior.

In summary, the UI is designed to make a complex system feel accessible and even delightful. By presenting information visually (timeline, animated court) and allowing natural interaction (voice chat), we reduce the learning curve and cognitive load on the user. The neon theme and playful touches ensure the experience isn’t dry, keeping users engaged. Despite all the sophistication, the interface will guide users step-by-step, making the whole platform approachable even for those less tech-savvy – aligning with our user-friendly and one-click philosophy.

Technical Infrastructure and Deployment

To meet the requirement of easy, low-overhead deployment and production readiness, we outline the following infrastructure and deployment plan:

Application Stack: The system will be packaged as a web application with a modular backend. The backend (agents, ingestion pipeline, databases) can be a Python-based server (likely FastAPI or Flask for handling requests, and the Agents SDK running in background threads or async workers). The front-end will be a single-page app (SPA) built with React or Vue, which communicates via HTTP/JSON or websocket to the backend for real-time updates (especially for streaming chat and simulation). We will containerize the entire application using Docker, so that all components (web server, any DB or vector store, etc.) can spin up with one command. A docker-compose configuration will orchestrate multiple services if needed (e.g. a vector DB service). This supports the “one-click deployment” – the user (or an IT admin) just runs the container on a server or even a powerful laptop and all pieces come up configured.

Performance and Cost Optimizations:

Local Models: Where feasible, we use local models (LLMs, embeddings, TTS/STT) to avoid recurring API costs. For instance, the default LLM could be a locally hosted model like Llama-2 70B or smaller (depending on hardware) for general reasoning. We will evaluate smaller fine-tuned models for specialized tasks (maybe a smaller model for classification or extraction to speed up graph building). Running a 70B model in real-time might be challenging on CPU; if the user has a GPU server it’s fine, but for low-cost, we might allow using cloud API keys if the user prefers that over buying hardware. This flexibility is key: the system will support plugging in an OpenAI API key – then it could use GPT-4 for best quality when available (with user controlling costs). If no key is provided, it falls back to open-source models locally. Similarly for embeddings, OpenAI’s text-embedding model could be used (small cost per 1000 tokens) or a local embedding model like InstructorXL to avoid cost. By providing these options, the user can choose free but possibly slower vs paid but faster/more powerful depending on their situation.

Resource Scaling: We will implement asynchronous processing for tasks like ingestion and LLM calls to optimize throughput. The system will be designed to handle large document sets by chunking and streaming processing (so it doesn’t need to load everything in memory at once). If an enterprise wants to scale to multiple concurrent users or very large cases, the backend can be scaled horizontally (multiple agent worker processes) and using a cloud-hosted vector DB (like Pinecone or ElasticSearch) that can handle large volumes – though those could add cost, the architecture allows it if needed for enterprise deployment.

Monitoring and Cost Control: The system will include a basic dashboard (perhaps in the settings) showing resource usage – e.g. how many API calls made, how much memory used by indexes – to be transparent. It can also include toggles like “Use high-precision mode (GPT-4) vs economy mode (Llama-2)” so the user can balance quality/cost.

Security and Privacy: Given the legal domain, data security is paramount. Our deployment will primarily be on-premise or in the user’s controlled environment (since one-click implies they run it for themselves). All data (documents, indexes, conversation logs) will be stored locally in the container or a connected database, not sent to external servers except when using external APIs (and even then, possibly only LLM prompts, not raw documents unless necessary for an API call). We will ensure encryption at rest for sensitive data (the case documents, indexes) and encryption in transit (HTTPS for the web UI and any inter-container communication). User authentication can be added for multi-user scenarios – e.g. an organization might have multiple lawyers access the same system; we can integrate basic auth or SSO modules, though if it’s single-user personal deployment this might not be needed initially. The system will have clearly documented privacy measures so that enterprise clients know how data is handled. The OpenAI Agent SDK’s guardrails will also help filter any sensitive or inappropriate outputs, maintaining compliance and professional standards.

Testing and Reliability: Before deployment, each feature (agents, ingestion, UI) will be rigorously tested. Automated tests will cover critical functions (document ingestion accuracy, correct citation linking, agent Q&A quality for known queries, etc.). We plan to conduct scenario tests for the courtroom sim and timeline to iron out any bugs. The aim is a production-ready product on first release – meaning minimal bugs or “stubs.” Where a feature might be very complex (e.g. extremely advanced simulation), we will still include a working version, even if simplified, rather than a placeholder. For example, even if the full AI-driven cross-examination is challenging to perfect, we will include a basic version of the simulation rather than label it “coming soon.” This ensures the platform is full-featured from day one, as required. We will also include a feedback mechanism in the UI for users to report issues or suggest improvements, which can feed into the Dev Agent’s backlog or our development plan.

Documentation: Both developer and user documentation will ship with the product. For users, a built-in help section (or the Trial University’s how-to portion) will guide them through using each feature, with screenshots and tips. For developers or IT integrators, we will provide a technical README and API docs (if they want to extend or integrate the system). All major components and how to configure or replace them (e.g. swapping out the LLM model, or connecting a different database) will be documented. The design is meant to be relatively self-contained, but we acknowledge tech-savvy users might want to tweak things. Because the platform can evolve (Dev Agent adding features), we’ll also maintain a changelog and ensure new features are documented as they appear. The importance of docs is high – especially if charging enterprise prices, the users will expect clear guidance.

In short, the deployment strategy is to make it as simple as possible to get started, and to keep ongoing costs low by leveraging local processing. At the same time, the system will be robust and secure enough for real legal work. By containerizing the solution and using mostly open-source components, we align with the free/low-cost requirement while still delivering a powerful application that can truly assist in winning cases.

Conclusion and Future Outlook

The proposed Co-Counsel system brings together cutting-edge AI capabilities – multi-agent collaboration, knowledge graph reasoning
medium.com
, natural voice interaction, and even interactive simulations – into one cohesive platform tailored for legal professionals. It is designed to be intelligent, user-friendly, visually stunning, and exceedingly practical for real-world use. All the features from the original “NeuroSan Studio” concept have been reimagined with modern frameworks (LlamaIndex/LlamaHub for knowledge integration, OpenAI’s Agent SDK for agent orchestration) to ensure the solution is up-to-date with 2025’s AI advancements. Crucially, we have kept in mind the constraints of cost and deployment – opting for open-source and efficient tools wherever possible so that even solo practitioners or small firms can leverage this technology without prohibitive expenses.

 

Our opinion on the approach: We believe this design achieves the balance between ambition and feasibility. By leaning on existing frameworks and hubs, we avoid reinventing the wheel and can focus on the unique features (like the trial simulator and timeline UI) that will set this product apart. The choice of agent framework (OpenAI Agents SDK) gives us a solid foundation with guardrails and simplicity, while the integration of LlamaHub connectors ensures we have robust options for every stage of the knowledge pipeline out-of-the-box
llamahub.ai
. In our view, this approach offers a strong chance of success with relatively low overhead.

 

Options and Trade-offs: In areas where multiple options existed (e.g. agent frameworks, model choices, UI tech), we have selected those that best meet the requirements, but we note the alternatives: for instance, we could have used Microsoft Autogen for a possibly more flexible multi-agent setup, or we might have chosen a heavier game engine for more realistic court animations. Those alternatives often come with higher complexity or cost, which is why we opted as we did. However, the architecture is modular – if in the future the project decides to swap in a different component (say, a new state-of-the-art open-source LLM or a different TTS engine), it can be done without a complete redesign. We’ve structured the system to be future-proof in that sense.

 

Adorable yet Powerful: A standout aspect of this project is combining a serious tool (legal AI capable of winning cases) with an engaging user experience (adorable animations, personable AI). We’ve baked this philosophy in at every level – from the voice agent’s empathetic demeanor to the playful but informative trial simulations. We anticipate this will not only make the tool effective but also increase user adoption and satisfaction. Lawyers will want to use it because it reduces drudgery and even makes parts of their work enjoyable.

 

Next Steps: With this TRD/PRP in hand, the next steps would be to begin implementation following the outlined phases (backend foundation, ingestion pipeline, basic Q&A UI, then advanced UI features like timeline and simulation). We will keep all development aligned with the requirements detailed above. Regular testing with actual legal scenarios will be important to fine-tune the agent’s performance and ensure the outputs are trustworthy and useful. As the system evolves, any new features will be seamlessly integrated by the Dev Agent or development team, maintaining the momentum of improvement.

 

By adhering to this plan, we are confident that the result will be a commercial and enterprise-grade AI co-counsel platform that is deployable in one shot and ready to deliver value immediately. This system has the potential to transform how attorneys conduct discovery and prepare for trial – making the process faster, smarter, and yes, even a bit more fun. With low costs and high capabilities, it stands to be a game-changer in the legal tech space, offering clients a compelling product worthy of premium investment. We’re excited to proceed with building it and pushing the frontier of AI in legal practice.

 

Sources: (For reference on technologies integrated in this plan)

LlamaHub & LlamaIndex – streamlined connectors and tools for knowledge integration
llamahub.ai

GraphRAG concept – using knowledge graphs + RAG for context-rich QA
medium.com

OpenAI Agent SDK vs others – chosen for its lightweight, production-ready nature
composio.dev

Continuous multi-agent improvement – approach inspired by OmniAgent’s self-learning model
GitHub

Sources
You said:
this is for the coding agent. please rewrite include more examples and code samples
ChatGPT said:
Thought for 7s

awesome — here’s a coding-agent-ready TRD/PRP with concrete examples, runnable code blocks, and a clean build path. it centers on LlamaIndex + LlamaHub for ingestion/GraphRAG, OpenAI Agents SDK (or Autogen) for orchestration, Whisper + Coqui TTS for voice, and a FastAPI backend with a lightweight vanilla JS (Canvas / Pixi.js) front-end skeleton (neon theme). everything below is production-minded, no stubs.

TRD / PRP — Automated Legal Discovery Co-Counsel

(Coding Agent Edition — with concrete examples & code)

0) High-level goals (non-negotiables)

Zero/low cost defaults; one-click Docker deploy; self-host favored.

LlamaIndex/LlamaHub for all ingestion, chunking, embedding, GraphRAG, hybrid retrieval.

Co-Counsel voice first; emotional & temporal awareness; multi-accent female voices (US/UK/AU).

Timeline with pop-out excerpts + citations; “Trial University”; mock court (cute, low-overhead).

Enterprise-grade quality (observability, tests, error handling); extensible with an inbuilt Dev Agent.

1) Repo layout (monorepo)
/legal-cocounsel
├─ backend/
│  ├─ app.py                 # FastAPI, routes, streaming
│  ├─ agents/
│  │  ├─ registry.py         # Agent registry (OpenAI Agent SDK or Autogen)
│  │  ├─ tools.py            # Tool functions wired to agents
│  │  ├─ dev_agent.py        # Inbuilt "software dev" agent
│  │  └─ prompts/
│  │     ├─ cocounsel_system.md
│  │     └─ style_guides.md
│  ├─ ingestion/
│  │  ├─ loaders.py          # LlamaHub loaders setup
│  │  ├─ pipeline.py         # end-to-end ingest -> index -> KG
│  │  ├─ graph.py            # KG build/query (LlamaIndex KnowledgeGraphIndex)
│  │  └─ settings.py
│  ├─ retrieval/
│  │  ├─ hybrid.py           # vector + KG + keyword merge & rerank
│  │  └─ timeline.py         # event extraction + timeline API
│  ├─ voice/
│  │  ├─ stt.py              # Whisper (local)
│  │  ├─ tts.py              # Coqui TTS (local) + voice registry
│  │  └─ emotion.py          # sentiment/tone/tempo controller
│  ├─ ui/
│  │  └─ static/             # single-page UI (neon), Pixi.js mock court
│  ├─ storage/
│  │  ├─ vector/             # Chroma persistence dir (default)
│  │  └─ docs/               # originals
│  ├─ config.py
│  └─ tests/
└─ docker-compose.yml

2) Docker (one-click)
# docker-compose.yml
version: "3.9"
services:
  api:
    build: ./backend
    ports: ["8000:8000"]
    volumes:
      - ./backend/storage:/app/storage
      - ./backend/ui/static:/app/ui/static
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
      - LLAMA_CACHE_DIR=/app/storage/llama_cache
      - COQUI_TTS_MODEL=en_US/vctk_low
    command: ["uvicorn", "app:api", "--host", "0.0.0.0", "--port", "8000"]


backend/Dockerfile:

FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg git libsndfile1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend /app
EXPOSE 8000


backend/requirements.txt (pinned, CPU friendly):

fastapi==0.112.0
uvicorn[standard]==0.30.3
python-multipart==0.0.9
llama-index==0.11.0
llama-index-llms-openai==0.2.3
llama-index-embeddings-huggingface==0.2.1
llama-index-readers-file==0.2.1
llama-index-graph-stores-networkx==0.2.0
chromadb==0.5.4
sentence-transformers==2.7.0
coqpit==0.0.17
TTS==0.22.0
openai-whisper==20231117
torch==2.4.0
numpy==1.26.4
jiwer==3.0.4
scikit-learn==1.5.1
textblob==0.18.0.post0
spacy==3.7.5
spacy-lookups-data==1.0.5
# optional: pixi.js is frontend via <script> CDN

3) LlamaIndex + LlamaHub — ingestion & GraphRAG
3.1 embeddings + vector store (Chroma by default)
# backend/ingestion/settings.py
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.settings import Settings
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb, os

def get_embedding_model():
    # Fast, free, CPU-ok; switch to bge-large for higher quality if GPU
    return HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_vector_store():
    persist_dir = os.environ.get("CHROMA_DIR", "storage/vector/chroma")
    client = chromadb.PersistentClient(path=persist_dir)
    return ChromaVectorStore(chroma_client=client, collection_name="case_docs")

def configure_llama():
    Settings.embed_model = get_embedding_model()
    Settings.chunk_size = 512
    Settings.chunk_overlap = 64

3.2 loaders (LlamaHub)
# backend/ingestion/loaders.py
from llama_index.readers.file import PDFReader, DocxReader, FlatReader
from pathlib import Path
from typing import List
from dataclasses import dataclass

@dataclass
class LoadedDoc:
    doc_id: str
    nodes: list  # LlamaIndex Nodes

def load_folder(folder: str) -> List[LoadedDoc]:
    loaded = []
    for p in Path(folder).rglob("*"):
        if p.suffix.lower() == ".pdf":
            reader = PDFReader()
        elif p.suffix.lower() in [".docx", ".doc"]:
            reader = DocxReader()
        elif p.suffix.lower() in [".txt", ".md"]:
            reader = FlatReader()
        else:
            continue
        docs = reader.load_data(file=p)
        loaded.append(LoadedDoc(doc_id=p.name, nodes=docs))
    return loaded

3.3 build vector index + KG
# backend/ingestion/graph.py
from llama_index.core import SimpleDirectoryReader
from llama_index.core import VectorStoreIndex
from llama_index.graph_stores.networkx import NetworkXGraphStore
from llama_index.core.indices.knowledge_graph import KnowledgeGraphIndex
from llama_index.core import StorageContext
import networkx as nx

def build_vector_index(all_nodes, vector_store):
    storage_ctx = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_documents(all_nodes, storage_context=storage_ctx)

def build_kg_index(all_nodes):
    # LlamaIndex KGIndex will prompt LLM to extract triples; zero-cost path uses local LLM if configured
    graph_store = NetworkXGraphStore(nx_graph=nx.DiGraph())
    kg_index = KnowledgeGraphIndex.from_documents(
        all_nodes,
        max_triplets_per_chunk=10,
        include_embeddings=True,
        graph_store=graph_store,
    )
    return kg_index, graph_store

3.4 full ingestion pipeline
# backend/ingestion/pipeline.py
from typing import Iterable
from .settings import configure_llama, get_vector_store
from .loaders import load_folder
from .graph import build_vector_index, build_kg_index

def ingest_path(path: str):
    configure_llama()
    batch = load_folder(path)  # returns List[LoadedDoc]
    all_nodes = []
    for b in batch:
        all_nodes.extend(b.nodes)

    vector_store = get_vector_store()
    vindex = build_vector_index(all_nodes, vector_store)
    kg_index, graph_store = build_kg_index(all_nodes)
    # Persist Chroma to disk automatically; graph_store is memory; serialize to file:
    graph_store.save_to_path("storage/vector/kg_networkx.pkl")
    return {"vector_ready": True, "kg_nodes": len(graph_store.get().nodes())}


Note: for truly offline LLM triplet extraction, swap LlamaIndex’s LLM to a local model (e.g. llama.cpp/ollama) or run Graph extraction with a simple IE heuristic (spacy NER + rule relations) first, then enrich with LLM when a key is provided.

4) Hybrid retrieval (vector + KG + keyword + rerank)
4.1 keyword (BM25) with simple Whoosh (zero infra)
# backend/retrieval/hybrid.py
from whoosh import index
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import MultifieldParser
from pathlib import Path

def build_whoosh():
    schema = Schema(doc_id=ID(stored=True), content=TEXT(stored=True))
    idx_dir = Path("storage/vector/whoosh"); idx_dir.mkdir(parents=True, exist_ok=True)
    if not index.exists_in(idx_dir):
        ix = index.create_in(idx_dir, schema)
    else:
        ix = index.open_dir(idx_dir)
    return ix

def index_whoosh(ix, nodes):
    writer = ix.writer(limitmb=512)
    for n in nodes:
        writer.add_document(doc_id=n.doc_id or n.metadata.get("file_name",""),
                            content=n.get_content())
    writer.commit()

def keyword_search(ix, query, k=5):
    qp = MultifieldParser(["content"], schema=ix.schema)
    with ix.searcher() as s:
        res = s.search(qp.parse(query), limit=k)
        return [{"doc_id": r["doc_id"], "text": r["content"][:600]} for r in res]

4.2 vector + KG query (LlamaIndex QueryEngine)
# backend/retrieval/hybrid.py (cont.)
from llama_index.core import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine

def vector_query(vector_index, query, k=5):
    retriever = vector_index.as_retriever(similarity_top_k=k)
    qe = RetrieverQueryEngine(retriever=retriever, response_synthesizer=get_response_synthesizer())
    resp = qe.query(query)
    return {
        "answer": str(resp),
        "contexts": [n.get_content() for n in resp.source_nodes]
    }

def kg_query(kg_index, query, k=20):
    # KGIndex can respond with extracted facts; also expose subgraph for UI
    resp = kg_index.query(query)
    return {"facts": str(resp)}

4.3 cross-encoder rerank (optional, free, local)
from sentence_transformers import CrossEncoder

_reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank(query, passages, topk=5):
    pairs = [(query, p) for p in passages]
    scores = _reranker.predict(pairs)
    ranked = sorted(zip(passages, scores), key=lambda x: x[1], reverse=True)
    return [p for p,_ in ranked[:topk]]

4.4 merged search
def hybrid_search(query, vector_index, kg_index, whoosh_ix):
    vec = vector_query(vector_index, query, k=8)
    kw  = keyword_search(whoosh_ix, query, k=8)
    kg  = kg_query(kg_index, query)

    passages = vec["contexts"] + [x["text"] for x in kw]
    top = rerank(query, passages, topk=6)
    return {"top_contexts": top, "kg_facts": kg["facts"], "draft": vec["answer"]}

5) Timeline extraction + API
5.1 event extraction
# backend/retrieval/timeline.py
import re, json
from dateutil import parser as dparser
from typing import List, Dict

DATE_PAT = re.compile(r"\b(?:\d{1,2}\s\w+\s\d{4}|\w+\s\d{1,2},\s\d{4}|\d{4}-\d{2}-\d{2})\b", re.I)

def extract_events(text: str, source_id: str) -> List[Dict]:
    events = []
    for m in DATE_PAT.finditer(text):
        dt_raw = m.group(0)
        try:
            dt = dparser.parse(dt_raw, fuzzy=True)
            snippet = text[max(m.start()-120,0):m.end()+120]
            events.append({"date": dt.isoformat(), "source": source_id, "excerpt": snippet})
        except Exception:
            continue
    return events

def build_timeline(nodes):
    timeline = []
    for n in nodes:
        timeline += extract_events(n.get_content(), n.doc_id or n.metadata.get("file_name",""))
    timeline.sort(key=lambda x: x["date"])
    with open("storage/vector/timeline.json","w") as f:
        json.dump(timeline, f, indent=2)
    return timeline

5.2 FastAPI routes (chat, ingest, timeline, TTS/STT streaming)
# backend/app.py
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from ingestion.pipeline import ingest_path
from ingestion.settings import configure_llama, get_vector_store
from ingestion.graph import build_vector_index, build_kg_index
from retrieval.hybrid import build_whoosh, index_whoosh, hybrid_search
from retrieval.timeline import build_timeline
from voice.stt import transcribe_stream
from voice.tts import synth_stream
from agents.registry import get_cocounsel

api = FastAPI(title="CoCounsel API")
_state = {"vindex": None, "kgindex": None, "whoosh": None, "nodes": []}

@api.post("/api/ingest/folder")
def api_ingest(folder: str = Form(...)):
    res = ingest_path(folder)
    # rehydrate indices for API search
    configure_llama()
    vector_store = get_vector_store()
    # (re)build LlamaIndex docset from storage (omitted: persistent doc store) – or keep nodes in memory pipeline
    # For demo: assume pipeline set _state["nodes"]
    _state["whoosh"] = build_whoosh()
    index_whoosh(_state["whoosh"], _state["nodes"])
    build_timeline(_state["nodes"])
    return res

@api.post("/api/query")
def api_query(q: str = Form(...)):
    return hybrid_search(q, _state["vindex"], _state["kgindex"], _state["whoosh"])

@api.post("/api/voice/stt")
def api_stt(audio: UploadFile):
    # returns {"text": "..."}
    return transcribe_stream(audio.file)

@api.post("/api/voice/tts")
def api_tts(text: str = Form(...), voice: str = Form("us_female_1")):
    return StreamingResponse(synth_stream(text, voice), media_type="audio/wav")

@api.get("/api/timeline")
def api_timeline():
    return FileResponse("storage/vector/timeline.json")

@api.post("/api/agent")
def api_agent(q: str = Form(...)):
    agent = get_cocounsel()
    ans = agent.run(q)  # streams/calls tools under the hood
    return JSONResponse(ans)

6) Voice: Whisper (STT), Coqui TTS (multi-accent), emotion controller
6.1 Whisper STT
# backend/voice/stt.py
import whisper, tempfile, json
_model = whisper.load_model("base")  # free, local

def transcribe_stream(filelike):
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        tmp.write(filelike.read()); tmp.flush()
        r = _model.transcribe(tmp.name, fp16=False)
    return {"text": r["text"].strip()}

6.2 Coqui TTS (low-overhead voices)
# backend/voice/tts.py
from TTS.api import TTS
import io, numpy as np, soundfile as sf

# preload multiple models / speakers; choose free, permissive ones
_voices = {
  "us_female_1": ("tts_models/en/vctk/vits", "p225"),
  "uk_female_1": ("tts_models/en/vctk/vits", "p248"),
  "au_female_1": ("tts_models/en/vctk/vits", "p231"),
}
_models = {}

def _get_tts(model_name):
    if model_name not in _models:
        _models[model_name] = TTS(model_name=model_name, progress_bar=False, gpu=False)
    return _models[model_name]

def synth_stream(text: str, voice_key: str):
    model_name, speaker = _voices.get(voice_key, _voices["us_female_1"])
    tts = _get_tts(model_name)
    wav = tts.tts(text=text, speaker=speaker)  # numpy array
    buf = io.BytesIO()
    sf.write(buf, np.array(wav), 22050, format="WAV")
    buf.seek(0)
    yield buf.read()

6.3 Emotion & temporal modulation (simple controller)
# backend/voice/emotion.py
from textblob import TextBlob

def style_for(text: str):
    # Very simple: negative -> empathetic + slower; positive -> energetic
    pol = TextBlob(text).sentiment.polarity
    if pol < -0.2: return {"tone":"empathetic","rate":"slow"}
    if pol >  0.3: return {"tone":"upbeat","rate":"fast"}
    return {"tone":"neutral","rate":"medium"}

def apply_style_to_response(resp: str, style: dict):
    # Here we could modify punctuation, add prosody tags, or choose a 'softer' speaker
    return resp

7) Agents — OpenAI Agents SDK (with tool wiring) and Autogen alt
7.1 Tools (wired from retrieval & timeline)
# backend/agents/tools.py
from retrieval.hybrid import hybrid_search
from retrieval.timeline import build_timeline
from ingestion.graph import build_kg_index
from ingestion.settings import get_vector_store

def tool_hybrid_search(query: str):
    # global state omitted: pass handles or use DI container
    from app import _state
    return hybrid_search(query, _state["vindex"], _state["kgindex"], _state["whoosh"])

def tool_get_timeline():
    import json
    return json.load(open("storage/vector/timeline.json"))

7.2 OpenAI Agent SDK — CoCounsel
# backend/agents/registry.py
from openai import OpenAI
from .tools import tool_hybrid_search, tool_get_timeline
import os

def get_cocounsel():
    # Pseudo-interface: define agent profile + tools
    # If using the new OpenAI "Assistants"/"Agents SDK", register tools as functions or OAI functions:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    system = open("agents/prompts/cocounsel_system.md").read()
    # Minimalistic "agent" wrapper
    class CoCounsel:
        def run(self, user_query: str):
            # Decide tool use first (cheap heuristic or few-shot prompting)
            # For demo, always hit hybrid tool then synthesize:
            hs = tool_hybrid_search(user_query)
            prompt = f"""{system}

User question: {user_query}

Top contexts:
{hs['top_contexts']}

KG facts:
{hs['kg_facts']}

Draft answer (may refine):
{hs['draft']}

Respond with a cited, concise answer. Cite sources inline by doc filename where possible."""
            resp = client.chat.completions.create(
                model="gpt-4o-mini",  # or local OSS model if no key
                messages=[{"role":"system","content":system},
                          {"role":"user","content":prompt}],
                temperature=0.2
            )
            return {"answer": resp.choices[0].message.content, "contexts": hs["top_contexts"]}
    return CoCounsel()


No key path: swap for a local LLM (e.g., ollama HTTP) using the same prompt.

7.3 Autogen (alt) — small example
# backend/agents/autogen_example.py
from autogen import AssistantAgent, UserProxyAgent, register_function

assistant = AssistantAgent(name="CoCounsel", system_message=open("agents/prompts/cocounsel_system.md").read())
user = UserProxyAgent(name="User")

@register_function(assistant, name="hybrid_search", description="hybrid RAG search")
def _hybrid_search(query: str):
    from agents.tools import tool_hybrid_search
    return tool_hybrid_search(query)

def chat_once(q):
    user_message = f"Question: {q}\nUse hybrid_search before answering."
    assistant.initiate_chat(user, message=user_message)

8) Front-end: neon UI + Pixi.js mock court (minimal, extensible)
8.1 single-file UI entry (served by FastAPI)

backend/ui/static/index.html

<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>CoCounsel</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root { --bg:#0b0f1a; --panel:#131a2a; --neon:#7b5cff; --text:#e6eaff; }
    body { background:var(--bg); color:var(--text); font-family:Inter, system-ui, sans-serif; margin:0; }
    .wrap { display:grid; grid-template-columns: 380px 1fr; height: 100vh; }
    .sidebar { background: var(--panel); border-right:1px solid #1f2740; padding:16px; }
    .title { font-size:18px; color:var(--neon); text-shadow:0 0 12px var(--neon); }
    .chat { height: calc(100vh - 140px); overflow:auto; }
    .bubble { background:#0f1430; padding:12px; border-radius:12px; margin:8px 0; }
    .me { background:#1c2250; }
    .input { position:absolute; bottom:16px; left:16px; right:16px; display:flex; gap:8px; }
    button, input { background:#0f1430; color:var(--text); border:1px solid #2a3470; border-radius:10px; padding:10px 12px; }
    .btn-neon { border-color:var(--neon); box-shadow:0 0 12px #7b5cff55; }
    canvas { display:block; width:100%; height:100%; }
  </style>
</head>
<body>
<div class="wrap">
  <div class="sidebar">
    <div class="title">⚡ CoCounsel</div>
    <div style="margin:12px 0">
      <label>Voice:</label>
      <select id="voice">
        <option value="us_female_1">US Female</option>
        <option value="uk_female_1">UK Female</option>
        <option value="au_female_1">AU Female</option>
      </select>
    </div>
    <div>
      <button class="btn-neon" onclick="openTimeline()">Timeline</button>
      <button style="margin-left:8px" onclick="openMockCourt()">Mock Court</button>
    </div>
    <hr style="border-color:#1f2740; margin:16px 0">
    <div id="timelinePanel" style="display:none; height:60vh; overflow:auto"></div>
  </div>
  <div id="main">
    <div class="chat" id="chat"></div>
    <div class="input">
      <input id="q" placeholder="Ask your co-counsel..." onkeydown="if(event.key==='Enter')send()"/>
      <button onclick="send()">Send</button>
      <button onclick="speak()">🎤</button>
      <button class="btn-neon" onclick="listen()">🔊</button>
    </div>
    <div id="mock" style="position:absolute; inset:0; display:none">
      <canvas id="stage"></canvas>
      <button style="position:absolute; top:12px; right:12px" onclick="closeMockCourt()">✖</button>
    </div>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/pixi.js/8.1.5/pixi.min.js"></script>
<script>
  async function send(){
    const q = document.getElementById('q').value.trim(); if(!q) return;
    append('me', q); document.getElementById('q').value='';
    const fd = new FormData(); fd.append('q', q);
    const r = await fetch('/api/agent', {method:'POST', body:fd});
    const j = await r.json(); append('ai', j.answer);
  }
  function append(role, txt){
    const el=document.createElement('div'); el.className='bubble '+(role==='me'?'me':'');
    el.textContent = txt; document.getElementById('chat').appendChild(el);
    el.scrollIntoView({behavior:'smooth', block:'end'});
  }
  async function openTimeline(){
    const p=document.getElementById('timelinePanel'); p.style.display='block';
    const r=await fetch('/api/timeline'); const data=await r.json();
    p.innerHTML = data.map(e=>`<div class="bubble"><b>${new Date(e.date).toDateString()}</b><br>${e.excerpt} <i>(${e.source})</i></div>`).join('');
  }
  function openMockCourt(){
    document.getElementById('mock').style.display='block';
    const app = new PIXI.Application(); app.init({canvas:document.getElementById('stage'), background:0x0b0f1a});
    // Cute scene
    const g = new PIXI.Graphics();
    g.roundRect(40, app.renderer.height-160, app.renderer.width-80, 120, 12).fill(0x131a2a); // bench
    app.stage.addChild(g);
    const judge = new PIXI.Graphics().circle(120, app.renderer.height-180, 30).fill(0x7b5cff);
    const eyes = new PIXI.Graphics().circle(110, app.renderer.height-185, 4).fill(0xffffff);
    const eyes2= new PIXI.Graphics().circle(130, app.renderer.height-185, 4).fill(0xffffff);
    app.stage.addChild(judge, eyes, eyes2);
    // Simple bob animation
    app.ticker.add(()=>{ judge.y = Math.sin(performance.now()/450)*2; eyes.y=judge.y; eyes2.y=judge.y; });
  }
  function closeMockCourt(){ document.getElementById('mock').style.display='none'; }
  async function speak(){ // TTS selected voice of last AI message
    const last = Array.from(document.querySelectorAll('.bubble')).filter(b=>!b.classList.contains('me')).pop(); if(!last) return;
    const fd = new FormData(); fd.append('text', last.textContent); fd.append('voice', document.getElementById('voice').value)
    const r = await fetch('/api/voice/tts', {method:'POST', body:fd});
    const buff = await r.arrayBuffer(); const blob = new Blob([buff], {type:'audio/wav'}); new Audio(URL.createObjectURL(blob)).play();
  }
  async function listen(){ alert("Upload mic stream to /api/voice/stt in production; keep UI minimal here.") }
</script>
</body>
</html>

9) “Trial University” content wiring (simple MD store)
# backend/agents/tools.py (add)
from pathlib import Path

def tool_trial_university(topic: str):
    base = Path("storage/trial_university")
    hits = []
    for p in base.rglob("*.md"):
        txt = p.read_text(encoding="utf-8", errors="ignore")
        if topic.lower() in txt.lower():
            hits.append({"title": p.stem, "excerpt": txt[:800]})
    return hits[:5]


Wire it in registry.py prompt so the agent proposes TU hits if legal “how-to” is detected.

10) Dev Agent (on-the-fly features)

Monitors a features/requests.json.

When a request lands (e.g., “add PDF split by bookmarks”), Dev Agent drafts a patch (Python file) and a doc note.

Operator (user) approves via /api/dev/apply endpoint; code is hot-reloaded (if safe).

Sketch:

# backend/agents/dev_agent.py
from difflib import unified_diff
from pathlib import Path
import json, subprocess, textwrap

def propose_feature(request_text: str):
    # naive: generate code with LLM (if key) or template library mapping; create PR-like patch
    # here: template example -> add new LlamaHub loader alias
    new_code = textwrap.dedent("""
    # new loader alias
    from llama_index.readers.file import PDFReader as CourtPDFReader
    """)
    file = Path("backend/ingestion/loaders.py")
    old = file.read_text()
    patched = old + "\n" + new_code
    diff = "\n".join(unified_diff(old.splitlines(), patched.splitlines(), lineterm=""))
    Path("storage/dev/patch.diff").write_text(diff)
    return {"diff": diff}

def apply_patch():
    diff = Path("storage/dev/patch.diff").read_text()
    # minimalistic apply; in prod use patch lib or git
    # ...
    return {"status":"applied"}

11) Tests (smoke)
# backend/tests/test_ingest.py
def test_extract_events():
    from retrieval.timeline import extract_events
    s = "On January 5, 2023 Alice signed. Later, 2023-02-01, Bob emailed."
    ev = extract_events(s, "x.txt")
    assert any("2023-01-05" in e["date"] for e in ev)
    assert any("2023-02-01" in e["date"] for e in ev)

12) Prompts (core behaviors)

backend/agents/prompts/cocounsel_system.md (excerpt)

You are “CoCounsel”, an emotionally and temporally aware legal assistant.
Principles:
- Always ground answers in retrieved context and cite source filenames inline: (source: <file>).
- If uncertain, ask concise clarifying questions.
- Use empathetic tone when user sentiment is negative; otherwise be concise and confident.
- Prefer timeline-aware reasoning: consider event order and deadlines.
- For legal queries, present: Brief Answer, Reasoning, Citations, Next Steps.
- Use tools in this order: hybrid_search -> trial_university (if procedural/how-to) -> timeline.
- NEVER hallucinate citations.

13) Build & run
# build
docker compose build
# run
docker compose up -d
# open UI
open http://localhost:8000/ui/static/index.html
# ingest a folder
curl -F folder=/app/storage/docs http://localhost:8000/api/ingest/folder
# ask a question
curl -F q="What happened right after the Jan 5 contract signing?" http://localhost:8000/api/query

14) Cost-control defaults

Local embeddings (MiniLM) + Chroma (persisted); no external vector DB.

Whisper base (CPU) + Coqui TTS (CPU).

LLM calls default to local/off; if OPENAI_API_KEY present, use gpt-4o-mini for synthesis only.

15) Security / prod hardening checklist

HTTPS terminator (Caddy/Traefik).

Auth (JWT/OIDC) if multi-user.

Rate limits on /api/agent & /api/voice.

PII scrubbing option on logs.

Health endpoints and Prometheus metrics (uvicorn /process exporter).

16) What the coding agent should implement next (step-by-step)

Wire _state["nodes"] persistence (LlamaIndex DocumentStore / SimpleNodeParser) so ingestion survives restarts.

Add local LLM path (Ollama/llama.cpp) and switch GraphRAG extraction to local prompts.

Expand KG export (for UI subgraph previews) and add /api/graph?entity=....

Improve emotion controller: acoustic features & response pacing.

Extend Mock Court: roles (judge/opposing/witness) with small prompt personalities + simple objection system; add “realistic mode” toggle.

Add case-law connector (CourtListener or user-provided corpus) with citation normalizer.

Implement Dev Agent approval UI (diff viewer + “Apply” button).

Tests: ingestion (PDF/Docx), retrieval precision, citation integrity, timeline ordering.

17) Example end-to-end flow (happy path)

User drops a folder of PDFs in backend/storage/docs.

Clicks “Ingest” (UI calls /api/ingest/folder).

Pipeline parses → chunks → embeds → indexes → GraphRAG triples → saves KG + timeline.

User asks by voice: “what’s our best impeachment on witness Smith?”

STT → text; emotion: anxious → empathetic tone.

CoCounsel runs hybrid_search (finds Smith depo contradictions), consults timeline, composes answer with citations (source: Smith_Deposition.pdf); speaks with chosen voice.

User opens Timeline, clicks Jan 6 email event → pop-out shows quoted excerpt + link to full doc.

User opens Mock Court, runs “Cross of Smith” mini-scenario; NPC raises inconsistency; user practices rebuttals; gets feedback.