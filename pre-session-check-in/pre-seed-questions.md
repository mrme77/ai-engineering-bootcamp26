# Pre-seed Questions

## 1. What does it do?

It helps me decide what to study and practice next in the agentic AI engineering bootcamp. It connects my course material to learning objectives, checks my understanding through exercises and explanations in my own words, and saves my progress across study sessions. It uses that history to identify recurring mistakes, revisit weak concepts, and recommend targeted practice. Explanations include practical examples and references to the relevant course material.

## 2. Who is it for?

The primary user is me, a learner studying agentic AI engineering. It could later help other bootcamp learners review concepts and put them into practice.

## 3. What is the single most important question or task it must handle well first?

It must answer: "What should I practice next, based on what I currently understand?" The first milestone covers three selected bootcamp concepts: assess my understanding, save the results by concept, and recommend one next exercise with a clear reason. A later session should reuse those saved results rather than require me to repeat my study history.

The initial Session 1 `/ask` task is a stepping stone: explain a concept clearly, give a practical example, and ask one question to check understanding. For example: "What is retrieval-augmented generation (RAG), and when would I use it?" Answers should acknowledge uncertainty and must not claim to use course notes unless those notes are actually provided.

## 4. What would make you proud to demo on Demo Day?

I complete a short assessment covering three bootcamp concepts. The assistant explains mistakes using examples and course-note references, saves my results, and recommends a specific next exercise. When I return in a new session, it remembers a weak concept and tests it with a different scenario. For example, if I confuse retrieval with model training, it revisits that distinction and shows whether my understanding has improved. If the notes do not contain enough information, it says so rather than inventing a source.

## 5. How does it differ from a general chat interface?

Clear explanations and quizzes alone offer little beyond a well-written prompt in ChatGPT or another inference interface. The intended value is a connected study workflow:

- Course material organized around explicit learning objectives.
- Saved assessment results and recurring misconceptions across sessions.
- Practice and review selected from that history.
- Explanations supported by references to the course material.

General chat tools can support many of these activities. This project makes the curriculum, progress, and next-step selection part of the application, reducing the need to reconstruct context manually. A successful first demonstration must show that a saved assessment changes the next recommended exercise.

## 6. Could it use a local LLM?

I would like to explore running the assistant with a local LLM of approximately 30 billion parameters. This is a candidate deployment approach, not a finalized model choice or an implemented capability. Local execution is an additional design goal; the main product benefit remains the connected learning workflow.

Before selecting the model and runtime, check the available hardware, memory requirements, quantization options, context capacity, response latency, and answer quality on representative study tasks. Parameter count alone is not a quality target. Keep course-note retrieval, progress storage, and practice selection in the application so that replacing the inference model does not erase the learner's history.

The local deployment goal is to keep course material and study records on my own machine during inference. Verify the complete data flow before claiming that everything stays local. The current prototype uses OpenRouter; local inference is planned exploration, and moving to it has not yet been implemented.
