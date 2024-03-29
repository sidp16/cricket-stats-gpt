# Cric-GPT Project Insights
In this project, I leveraged the power of Langchain to generate accurate outputs from natural language questioning. It works by taking a natural language question (NLQ) as input, such as "What is Jasprit Bumrah's test match bowling average?". The Langchain model processes this question, understanding its context and intent. It then formulates a query that can be used to retrieve the relevant information from a MySQL database.

The MySQL database is populated with match stats extracted from Cricinfo. This data extraction process involves scraping the Cricinfo website for relevant statistics and storing them in a structured format in the database. This provides a rich source of data for the Langchain model to draw upon when answering questions.

#### Some of the other routes I attempted for generating a correct SQL query from an NLQ were:
- Fine-tuning a model using the extensive range of models available from OpenAI required a careful evaluation of each model's cost per input/output to determine its viability. The primary bottleneck in this process was supplying the model with a sufficient volume of training data, specifically prompt-completion pairs. This was crucial to effectively train the model to interpret cricket-related questions and generate precise SQL queries for my database.
- The Langchain agent can be enhanced with a prompt to improve its comprehension of the Natural Language Query (NLQ). While this strategy had the potential to significantly boost results, it also presented a unique challenge. The prompt has a relatively small character limit, making it difficult to include all pertinent cricket information for the model. This difficulty is further compounded by the substantial amount of boilerplate text in the prompt. 

#### When I resume this project, there are a few potential next steps I could consider:
- One option is to explore the use of GPT-4 which could provide improved performance and accuracy in interpreting natural language queries, in turn writing more accurate SQL queries for the database.
- Alternatively, I could investigate using Language Model Language Servers (LLMS) from Hugging Face, which offer a wide range of pre-trained models for various natural language processing tasks.
- Another step could be to generate a large number of prompt-completion pairs to fine-tune your model. This could be a long manual process or I could write a script to automate the generation of these pairs saving a lot of time. 
