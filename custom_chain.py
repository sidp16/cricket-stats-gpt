from __future__ import annotations

from credentials import gpt_api_key

from typing import Any, Dict, List, Optional

from pydantic import Extra

from langchain.base_language import BaseLanguageModel
from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
)
from langchain.chains.base import Chain
from langchain.prompts.base import BasePromptTemplate
from langchain.callbacks.stdout import StdOutCallbackHandler
from langchain.chat_models.openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate


class MyCustomChain(Chain):
    """
    An example of a custom chain.
    """

    prompt: BasePromptTemplate
    """Prompt object to use."""
    llm: BaseLanguageModel
    output_key: str = "text"  #: :meta private:

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @property
    def input_keys(self) -> List[str]:
        """Will be whatever keys the prompt expects.

        :meta private:
        """
        return self.prompt.input_variables

    @property
    def output_keys(self) -> List[str]:
        """Will always return text key.

        :meta private:
        """
        return [self.output_key]

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        # Your custom chain logic goes here
        # This is just an example that mimics LLMChain
        prompt_value = self.prompt.format_prompt(**inputs)

        # Whenever you call a language model, or another chain, you should pass
        # a callback manager to it. This allows the inner run to be tracked by
        # any callbacks that are registered on the outer run.
        # You can always obtain a callback manager for this by calling
        # `run_manager.get_child()` as shown below.
        response = self.llm.generate_prompt(
            [prompt_value], callbacks=run_manager.get_child() if run_manager else None
        )

        # If you want to log something about this run, you can do so by calling
        # methods on the `run_manager`, as shown below. This will trigger any
        # callbacks that are registered for that event.
        if run_manager:
            run_manager.on_text("Log something about this run")

        return {self.output_key: response.generations[0][0].text}

    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        # Your custom chain logic goes here
        # This is just an example that mimics LLMChain
        prompt_value = self.prompt.format_prompt(**inputs)

        # Whenever you call a language model, or another chain, you should pass
        # a callback manager to it. This allows the inner run to be tracked by
        # any callbacks that are registered on the outer run.
        # You can always obtain a callback manager for this by calling
        # `run_manager.get_child()` as shown below.
        response = await self.llm.agenerate_prompt(
            [prompt_value], callbacks=run_manager.get_child() if run_manager else None
        )

        # If you want to log something about this run, you can do so by calling
        # methods on the `run_manager`, as shown below. This will trigger any
        # callbacks that are registered for that event.
        if run_manager:
            await run_manager.on_text("Log something about this run")

        return {self.output_key: response.generations[0][0].text}

    @property
    def _chain_type(self) -> str:
        return "my_custom_chain"


if __name__ == "__main__":
    chain = MyCustomChain(
        prompt=PromptTemplate.from_template(
            """
You are an agent designed to extract key information about cricket, from a question.
Most, if not all questions will be based on cricket statistics. 

These are the key bits of information you should extract:
Names: The name(s) of the players in the question. This might be the first name and/or last name.
Format:  - T20I can be referred to as Twenty20 or Twenty twenty but return T20I if those are the case
         - ODI can be referred to as one-dayers, 50-over cricket or one-day but return ODI
         - White ball refers to ODI and T20I, therefore you return "T20I and ODI".
         - Test is only other format in cricket, if spotted return Test
         - Red ball refers to Test matches, therefore return "Test".
Teams: The team(s) in the question
Statistic: The statistic the question is involving, examples include:
                - Batting average
                - Batting strike rate
                - Bowling strike rate
                - Bowling average
                - Wickets
                - Economy
                - Runs
                - Balls
                - Boundaries
                - 4s
                - 6s
                - No balls
                - Wides
                - Maidens

After extracting the key info, understand how to calculate what is being asked IF A CALCULATION IS NEEDED.

Here are some useful definitions that will help you understand how to calculate statistics:
        - STAT: HOW TO CALCULATE IT
        - Batting average: runs divided by (number of times they have gotten out)
        - Bowling average: runs conceded / wickets taken
        - Bowling strike rate: balls / wickets
        - Batting strike rate: (runs / balls) * 100
        - An over has 6 balls. Therefore if a bowler has bowled 4.2 overs, they have bowled 4 complete overs and 2 more balls amounting in 26 balls.
        - Boundaries: 4s and 6s

Given the input question, return the information in this fashion if the question contains any of the below:
Name|Format|Teams|Statistic|Calculation Required


Example 1: "What is Virat Kohli's average in T20Is?"
You return:
Virat Kohli|T20I||Batting or bowling average|[runs / number of times they have gotten out OR runs / wickets]
You return "runs / number of times they gotten out OR runs / wickets" because you do not know which average the question is asking about.
Therefore, you must return both types of average definitions you know. However, if a type of average has been specified, return just that one.
Apply the same logic to strike rate.

Example 2: "List the white ball games for Australia where Smith has had a strike rate over 150."
You return:
Smith|T20I and ODI|Australia|Strike rate|[(runs / balls) * 100 OR balls / wickets]

Example 3: "Which Test matches have had a bowler get 8 or more wickets in an innings?"
You return:
|Test||Wickets|---

Example 4: "What was Dale Steyn's bowling average in Test matches in 2010?"
You return:
Dale Steyn|Test||Bowling average|[runs / wickets]

Example 5: "What was Rohit Sharma's batting average in red ball matches in 2014?"
You return:
Rohit Sharma|Test||Batting average|[runs / number of times they have gotten out]

Begin!
Question: {input}
"""
        ),
        llm=ChatOpenAI(
            temperature=0,
            openai_api_key=gpt_api_key,
            model="gpt-3.5-turbo",
        ),
    )

    print(
        chain.run(
            {"input": "List the bowlers that have gotten 100 runs and a wicket?"},
            callbacks=[StdOutCallbackHandler()],
        )
    )


